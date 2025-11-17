"""
ARK Listener Module
===================
Handles speech-to-text functionality using faster-whisper for offline voice recognition.
Provides continuous listening capabilities with configurable wake word detection.
"""

import logging
import threading
import time
import queue
import numpy as np
import sounddevice as sd
try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False
    logging.warning("webrtcvad not available. Voice activity detection disabled.")
from faster_whisper import WhisperModel
from typing import Optional, Callable, Dict, Any
import yaml
from pathlib import Path


class AudioBuffer:
    """Manages audio buffering for continuous recording."""
    
    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 0.03):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.buffer = queue.Queue()
        self.is_recording = False
        
    def add_chunk(self, audio_chunk: np.ndarray):
        """Add an audio chunk to the buffer."""
        if self.is_recording:
            self.buffer.put(audio_chunk)
    
    def get_audio(self, duration: float) -> np.ndarray:
        """Get audio data for specified duration."""
        num_chunks = int(duration / self.chunk_duration)
        audio_data = []
        
        for _ in range(num_chunks):
            try:
                chunk = self.buffer.get(timeout=0.1)
                audio_data.append(chunk)
            except queue.Empty:
                break
        
        if audio_data:
            return np.concatenate(audio_data)
        return np.array([], dtype=np.float32)
    
    def clear(self):
        """Clear the buffer."""
        while not self.buffer.empty():
            try:
                self.buffer.get_nowait()
            except queue.Empty:
                break


class VoiceActivityDetector:
    """Detects voice activity in audio stream using WebRTC VAD."""
    
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 3):
        self.sample_rate = sample_rate
        self.vad_available = VAD_AVAILABLE
        if self.vad_available:
            self.vad = webrtcvad.Vad(aggressiveness)  # 0-3, 3 is most aggressive
        else:
            self.vad = None
        self.frame_duration = 30  # ms
        self.frame_size = int(sample_rate * self.frame_duration / 1000)
        
    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Check if audio chunk contains speech.
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            True if speech detected, False otherwise
        """
        # Convert float32 to int16
        if audio_chunk.dtype == np.float32:
            audio_chunk = (audio_chunk * 32767).astype(np.int16)
        
        # Ensure proper frame size
        if len(audio_chunk) != self.frame_size:
            return False
        
        try:
            if not self.vad_available:
                return True  # Default to assuming speech when VAD unavailable
            return self.vad.is_speech(audio_chunk.tobytes(), self.sample_rate)
        except Exception:
            return False


class Listener:
    """
    Voice input manager for ARK using faster-whisper for offline STT.
    Supports continuous listening, wake word detection, and voice activity detection.
    """
    
    def __init__(self, config_path: str = "data/config.yaml"):
        """
        Initialize the Listener.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # Audio configuration
        self.sample_rate = self.config.get('audio', {}).get('sample_rate', 16000)
        self.channels = 1
        self.chunk_duration = 0.03  # 30ms chunks
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Whisper configuration
        self.model_size = self.config.get('whisper', {}).get('model_size', 'base')
        self.device = self.config.get('whisper', {}).get('device', 'cpu')
        self.language = self.config.get('whisper', {}).get('language', 'en')
        
        # Listening configuration
        self.wake_word = self.config.get('listening', {}).get('wake_word', 'ark')
        self.listening_timeout = self.config.get('listening', {}).get('timeout', 5.0)
        self.silence_threshold = self.config.get('listening', {}).get('silence_threshold', 2.0)
        self.energy_threshold = self.config.get('listening', {}).get('energy_threshold', 300)
        
        # Initialize components
        self.whisper_model: Optional[WhisperModel] = None
        self.audio_buffer = AudioBuffer(self.sample_rate, self.chunk_duration)
        self.vad = VoiceActivityDetector(self.sample_rate)
        
        # State management
        self.is_listening = False
        self.is_recording = False
        self.listening_thread: Optional[threading.Thread] = None
        self.audio_stream = None
        
        # Callbacks
        self.on_wake_word: Optional[Callable] = None
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        self.logger.info("Listener initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    def load_model(self) -> bool:
        """
        Load the Whisper model for speech recognition.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Load faster-whisper model
            self.whisper_model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="float32" if self.device == "cpu" else "float16"
            )
            
            self.logger.info("Whisper model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            return False
    
    def start_listening(self, 
                       on_wake_word: Callable = None,
                       on_speech_start: Callable = None,
                       on_speech_end: Callable[[str], None] = None,
                       on_error: Callable[[str], None] = None):
        """
        Start continuous listening for wake word and speech.
        
        Args:
            on_wake_word: Callback when wake word is detected
            on_speech_start: Callback when speech starts
            on_speech_end: Callback when speech ends with transcribed text
            on_error: Callback for errors
        """
        if not self.whisper_model:
            error_msg = "Whisper model not loaded. Call load_model() first."
            self.logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return False
        
        if self.is_listening:
            self.logger.warning("Already listening")
            return True
        
        # Set callbacks
        self.on_wake_word = on_wake_word
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        self.on_error = on_error
        
        # Start audio stream
        try:
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            
            self.audio_stream.start()
            self.is_listening = True
            
            # Start listening thread
            self.listening_thread = threading.Thread(target=self._listening_loop, daemon=True)
            self.listening_thread.start()
            
            self.logger.info("Started listening for wake word")
            return True
            
        except Exception as e:
            error_msg = f"Failed to start listening: {e}"
            self.logger.error(error_msg)
            if on_error:
                on_error(error_msg)
            return False
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        self.is_recording = False
        
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1.0)
        
        self.audio_buffer.clear()
        self.logger.info("Stopped listening")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        # Add audio chunk to buffer
        audio_chunk = indata[:, 0] if indata.ndim > 1 else indata
        self.audio_buffer.add_chunk(audio_chunk)
    
    def _listening_loop(self):
        """Main listening loop for wake word detection."""
        consecutive_speech = 0
        consecutive_silence = 0
        
        while self.is_listening:
            try:
                # Get audio chunk for analysis
                audio_chunk = self.audio_buffer.get_audio(self.chunk_duration)
                
                if len(audio_chunk) == 0:
                    time.sleep(0.01)
                    continue
                
                # Check for voice activity
                if self._has_voice_activity(audio_chunk):
                    consecutive_speech += 1
                    consecutive_silence = 0
                    
                    # Start recording after detecting consistent speech
                    if consecutive_speech >= 3 and not self.is_recording:
                        self._start_recording()
                else:
                    consecutive_silence += 1
                    consecutive_speech = 0
                    
                    # Stop recording after silence threshold
                    if self.is_recording and consecutive_silence >= int(self.silence_threshold / self.chunk_duration):
                        self._stop_recording()
                
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                if self.on_error:
                    self.on_error(f"Listening error: {e}")
                time.sleep(0.1)
    
    def _has_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """
        Check if audio chunk has voice activity.
        
        Args:
            audio_chunk: Audio data
            
        Returns:
            True if voice activity detected
        """
        # Check energy level
        energy = np.sqrt(np.mean(audio_chunk**2))
        energy_db = 20 * np.log10(max(energy, 1e-10))
        
        has_energy = energy_db > -40  # Minimum energy threshold
        
        # Use VAD for more sophisticated detection
        frame_size = self.vad.frame_size
        if len(audio_chunk) >= frame_size:
            frame = audio_chunk[:frame_size]
            has_speech = self.vad.is_speech(frame)
        else:
            has_speech = False
        
        return has_energy and has_speech
    
    def _start_recording(self):
        """Start recording user speech."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.audio_buffer.is_recording = True
        self.audio_buffer.clear()
        
        self.logger.info("Started recording speech")
        
        if self.on_speech_start:
            self.on_speech_start()
    
    def _stop_recording(self):
        """Stop recording and transcribe speech."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.audio_buffer.is_recording = False
        
        self.logger.info("Stopped recording speech")
        
        # Transcribe the recorded audio
        self._transcribe_recorded_audio()
    
    def _transcribe_recorded_audio(self):
        """Transcribe the recorded audio using Whisper."""
        try:
            # Get all recorded audio
            audio_data = self.audio_buffer.get_audio(self.listening_timeout)
            
            if len(audio_data) < self.sample_rate * 0.5:  # Minimum 0.5 seconds
                self.logger.debug("Audio too short for transcription")
                return
            
            # Transcribe with Whisper
            segments, info = self.whisper_model.transcribe(
                audio_data,
                language=self.language,
                beam_size=1,
                word_timestamps=False
            )
            
            # Combine segments into full transcription
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            transcription = transcription.strip()
            
            if transcription:
                self.logger.info(f"Transcribed: {transcription}")
                
                # Check for wake word
                if self._contains_wake_word(transcription):
                    if self.on_wake_word:
                        self.on_wake_word()
                
                # Send transcription to callback
                if self.on_speech_end:
                    self.on_speech_end(transcription)
            
        except Exception as e:
            error_msg = f"Transcription error: {e}"
            self.logger.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def _contains_wake_word(self, text: str) -> bool:
        """
        Check if transcribed text contains the wake word.
        
        Args:
            text: Transcribed text
            
        Returns:
            True if wake word found
        """
        text_lower = text.lower()
        wake_word_lower = self.wake_word.lower()
        
        # Simple substring matching
        return wake_word_lower in text_lower
    
    def transcribe_audio_file(self, file_path: str) -> str:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not self.whisper_model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            segments, info = self.whisper_model.transcribe(
                file_path,
                language=self.language,
                beam_size=5
            )
            
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            return transcription.strip()
            
        except Exception as e:
            self.logger.error(f"File transcription error: {e}")
            raise
    
    def get_available_microphones(self) -> list:
        """Get list of available microphone devices."""
        devices = sd.query_devices()
        microphones = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                microphones.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        
        return microphones
    
    def set_microphone(self, device_id: int):
        """Set the microphone device to use."""
        sd.default.device[0] = device_id
        self.logger.info(f"Set microphone to device {device_id}")
    
    def is_model_loaded(self) -> bool:
        """Check if the Whisper model is loaded."""
        return self.whisper_model is not None
    
    def get_listener_info(self) -> Dict[str, Any]:
        """Get information about the listener configuration."""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'language': self.language,
            'sample_rate': self.sample_rate,
            'wake_word': self.wake_word,
            'is_listening': self.is_listening,
            'is_recording': self.is_recording,
            'model_loaded': self.is_model_loaded()
        }


if __name__ == "__main__":
    # Test the Listener
    logging.basicConfig(level=logging.INFO)
    
    def on_wake_word():
        print("Wake word detected!")
    
    def on_speech_start():
        print("Speech started...")
    
    def on_speech_end(text: str):
        print(f"Speech ended. Transcription: {text}")
    
    def on_error(error: str):
        print(f"Error: {error}")
    
    listener = Listener()
    
    print("Available microphones:")
    for mic in listener.get_available_microphones():
        print(f"  {mic['id']}: {mic['name']}")
    
    print(f"\nListener info: {listener.get_listener_info()}")
    
    if listener.load_model():
        print("Model loaded successfully!")
        print("Starting listener... (say something)")
        
        listener.start_listening(
            on_wake_word=on_wake_word,
            on_speech_start=on_speech_start,
            on_speech_end=on_speech_end,
            on_error=on_error
        )
        
        try:
            input("Press Enter to stop listening...")
        finally:
            listener.stop_listening()
    else:
        print("Failed to load model")