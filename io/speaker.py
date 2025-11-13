"""
NOVA Speaker Module
==================
Handles text-to-speech functionality using pyttsx3 and optional TTS models.
Provides voice synthesis with configurable voice characteristics.
"""

import logging
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any, List
import pyttsx3
import yaml
from pathlib import Path


class SpeechQueue:
    """Manages queued text-to-speech requests."""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.is_processing = False
        self.current_text = ""
        
    def add(self, text: str, priority: int = 1):
        """Add text to speech queue."""
        self.queue.put((priority, time.time(), text))
    
    def get_next(self) -> Optional[str]:
        """Get next text to speak."""
        try:
            priority, timestamp, text = self.queue.get_nowait()
            return text
        except queue.Empty:
            return None
    
    def clear(self):
        """Clear the speech queue."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
    
    def size(self) -> int:
        """Get queue size."""
        return self.queue.qsize()


class Speaker:
    """
    Text-to-speech manager for NOVA using pyttsx3 and optional TTS models.
    Supports voice customization, speech queuing, and emotion-based speech.
    """
    
    def __init__(self, config_path: str = "data/config.yaml"):
        """
        Initialize the Speaker.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # TTS Engine
        self.engine: Optional[pyttsx3.Engine] = None
        self.speech_queue = SpeechQueue()
        
        # Voice configuration
        voice_config = self.config.get('voice', {})
        self.voice_id = voice_config.get('voice_id', None)
        self.speech_rate = voice_config.get('rate', 180)
        self.speech_volume = voice_config.get('volume', 0.8)
        self.voice_gender = voice_config.get('gender', 'female')
        
        # Speech control
        self.is_speaking = False
        self.is_enabled = voice_config.get('enabled', True)
        self.interrupt_current = False
        
        # Threading
        self.speech_thread: Optional[threading.Thread] = None
        self.processing_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_speech_start: Optional[Callable[[str], None]] = None
        self.on_speech_end: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Initialize engine
        self._init_engine()
        
        self.logger.info("Speaker initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
    
    def _init_engine(self) -> bool:
        """
        Initialize the TTS engine.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.engine = pyttsx3.init()
            
            if not self.engine:
                raise RuntimeError("Failed to initialize TTS engine")
            
            # Configure voice properties
            self._configure_voice()
            
            # Set up event callbacks
            self.engine.connect('started-utterance', self._on_utterance_start)
            self.engine.connect('finished-utterance', self._on_utterance_end)
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
            self.processing_thread.start()
            
            self.logger.info("TTS engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            return False
    
    def _configure_voice(self):
        """Configure voice properties."""
        if not self.engine:
            return
        
        try:
            # Set speech rate
            self.engine.setProperty('rate', self.speech_rate)
            
            # Set volume
            self.engine.setProperty('volume', self.speech_volume)
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices:
                if self.voice_id:
                    # Use specific voice ID
                    for voice in voices:
                        if voice.id == self.voice_id:
                            self.engine.setProperty('voice', voice.id)
                            self.logger.info(f"Set voice to: {voice.name}")
                            return
                
                # Fallback to gender preference
                preferred_voices = []
                for voice in voices:
                    voice_name = voice.name.lower()
                    if self.voice_gender.lower() in voice_name or \
                       (self.voice_gender.lower() == 'female' and any(word in voice_name for word in ['zira', 'hazel', 'susan', 'samantha'])) or \
                       (self.voice_gender.lower() == 'male' and any(word in voice_name for word in ['david', 'mark', 'richard', 'alex'])):
                        preferred_voices.append(voice)
                
                if preferred_voices:
                    selected_voice = preferred_voices[0]
                    self.engine.setProperty('voice', selected_voice.id)
                    self.voice_id = selected_voice.id
                    self.logger.info(f"Set voice to: {selected_voice.name}")
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
                    self.voice_id = voices[0].id
                    self.logger.info(f"Set voice to default: {voices[0].name}")
        
        except Exception as e:
            self.logger.error(f"Error configuring voice: {e}")
    
    def _process_speech_queue(self):
        """Process queued speech requests."""
        while True:
            try:
                if self.speech_queue.size() > 0 and not self.is_speaking:
                    text = self.speech_queue.get_next()
                    if text:
                        self._speak_text_sync(text)
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in speech processing thread: {e}")
                time.sleep(0.5)
    
    def speak(self, text: str, priority: int = 1, interrupt: bool = False) -> bool:
        """
        Speak the given text.
        
        Args:
            text: Text to speak
            priority: Speech priority (higher = more important)
            interrupt: Whether to interrupt current speech
            
        Returns:
            True if speech was queued/started successfully
        """
        if not self.is_enabled:
            self.logger.debug("Speech is disabled")
            return False
        
        if not self.engine:
            self.logger.error("TTS engine not initialized")
            return False
        
        if not text.strip():
            self.logger.debug("Empty text provided")
            return False
        
        # Clean and prepare text
        text = self._prepare_text(text)
        
        # Handle interruption
        if interrupt and self.is_speaking:
            self.stop_speaking()
        
        # Add to queue
        self.speech_queue.add(text, priority)
        
        self.logger.info(f"Queued speech: {text[:50]}{'...' if len(text) > 50 else ''}")
        return True
    
    def speak_immediately(self, text: str) -> bool:
        """
        Speak text immediately, bypassing queue.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful
        """
        if not self.is_enabled or not self.engine:
            return False
        
        text = self._prepare_text(text)
        
        # Stop current speech and clear queue
        self.stop_speaking()
        self.speech_queue.clear()
        
        # Speak immediately
        return self._speak_text_sync(text)
    
    def _prepare_text(self, text: str) -> str:
        """
        Prepare text for speech synthesis.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text ready for TTS
        """
        # Remove or replace special characters
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        
        # Handle common abbreviations
        abbreviations = {
            'vs.': 'versus',
            'etc.': 'etcetera',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Dr.': 'Doctor',
            'Prof.': 'Professor'
        }
        
        for abbrev, expansion in abbreviations.items():
            text = text.replace(abbrev, expansion)
        
        # Handle URLs and emails (make them more speakable)
        import re
        # Simple URL detection and replacement
        text = re.sub(r'https?://\S+', 'link', text)
        text = re.sub(r'\S+@\S+\.\S+', 'email address', text)
        
        # Clean multiple spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _speak_text_sync(self, text: str) -> bool:
        """
        Speak text synchronously.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful
        """
        try:
            self.speech_queue.current_text = text
            self.is_speaking = True
            
            # Trigger callbacks
            if self.on_speech_start:
                self.on_speech_start(text)
            
            # Use engine to speak
            self.engine.say(text)
            self.engine.runAndWait()
            
            return True
            
        except Exception as e:
            error_msg = f"TTS error: {e}"
            self.logger.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
        finally:
            self.is_speaking = False
            self.speech_queue.current_text = ""
    
    def _on_utterance_start(self, name: str):
        """Called when utterance starts."""
        self.is_speaking = True
        self.logger.debug(f"Started speaking: {name}")
    
    def _on_utterance_end(self, name: str, completed: bool):
        """Called when utterance ends."""
        self.is_speaking = False
        
        if self.on_speech_end:
            self.on_speech_end(self.speech_queue.current_text)
        
        self.logger.debug(f"Finished speaking: {name} (completed: {completed})")
    
    def stop_speaking(self):
        """Stop current speech."""
        if self.is_speaking and self.engine:
            try:
                self.engine.stop()
                self.is_speaking = False
                self.logger.info("Stopped speaking")
            except Exception as e:
                self.logger.error(f"Error stopping speech: {e}")
    
    def clear_queue(self):
        """Clear the speech queue."""
        self.speech_queue.clear()
        self.logger.info("Cleared speech queue")
    
    def set_rate(self, rate: int):
        """
        Set speech rate.
        
        Args:
            rate: Speech rate (words per minute, typically 150-250)
        """
        if self.engine and 50 <= rate <= 400:
            self.engine.setProperty('rate', rate)
            self.speech_rate = rate
            self.logger.info(f"Set speech rate to {rate} WPM")
    
    def set_volume(self, volume: float):
        """
        Set speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine and 0.0 <= volume <= 1.0:
            self.engine.setProperty('volume', volume)
            self.speech_volume = volume
            self.logger.info(f"Set speech volume to {volume}")
    
    def set_voice(self, voice_id: str):
        """
        Set voice by ID.
        
        Args:
            voice_id: Voice identifier
        """
        if not self.engine:
            return False
        
        try:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if voice.id == voice_id:
                    self.engine.setProperty('voice', voice_id)
                    self.voice_id = voice_id
                    self.logger.info(f"Set voice to: {voice.name}")
                    return True
            
            self.logger.warning(f"Voice ID not found: {voice_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices.
        
        Returns:
            List of voice dictionaries with id, name, and languages
        """
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': self._detect_gender(voice.name),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def _detect_gender(self, voice_name: str) -> str:
        """Detect voice gender from name."""
        voice_name_lower = voice_name.lower()
        
        female_indicators = ['zira', 'hazel', 'susan', 'samantha', 'female', 'woman']
        male_indicators = ['david', 'mark', 'richard', 'alex', 'male', 'man']
        
        for indicator in female_indicators:
            if indicator in voice_name_lower:
                return 'female'
        
        for indicator in male_indicators:
            if indicator in voice_name_lower:
                return 'male'
        
        return 'unknown'
    
    def enable(self):
        """Enable speech output."""
        self.is_enabled = True
        self.logger.info("Speech enabled")
    
    def disable(self):
        """Disable speech output."""
        self.is_enabled = False
        self.stop_speaking()
        self.clear_queue()
        self.logger.info("Speech disabled")
    
    def is_busy(self) -> bool:
        """Check if currently speaking or has queued speech."""
        return self.is_speaking or self.speech_queue.size() > 0
    
    def get_speaker_info(self) -> Dict[str, Any]:
        """Get speaker configuration and status."""
        current_voice = None
        if self.engine:
            try:
                voice = self.engine.getProperty('voice')
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if v.id == voice:
                        current_voice = {'id': v.id, 'name': v.name}
                        break
            except:
                pass
        
        return {
            'enabled': self.is_enabled,
            'is_speaking': self.is_speaking,
            'queue_size': self.speech_queue.size(),
            'current_voice': current_voice,
            'speech_rate': self.speech_rate,
            'speech_volume': self.speech_volume,
            'voice_gender': self.voice_gender,
            'engine_available': self.engine is not None
        }
    
    def set_callbacks(self, 
                     on_speech_start: Callable[[str], None] = None,
                     on_speech_end: Callable[[str], None] = None,
                     on_error: Callable[[str], None] = None):
        """Set callback functions."""
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        self.on_error = on_error


if __name__ == "__main__":
    # Test the Speaker
    logging.basicConfig(level=logging.INFO)
    
    def on_start(text):
        print(f"Started speaking: {text[:30]}...")
    
    def on_end(text):
        print(f"Finished speaking: {text[:30]}...")
    
    def on_error(error):
        print(f"Speech error: {error}")
    
    speaker = Speaker()
    speaker.set_callbacks(on_start, on_end, on_error)
    
    print("Available voices:")
    for voice in speaker.get_available_voices():
        print(f"  {voice['name']} ({voice['gender']}) - {voice['id']}")
    
    print(f"\nSpeaker info: {speaker.get_speaker_info()}")
    
    # Test speech
    speaker.speak("Hello! I'm Nova, your personal assistant. How are you today?")
    
    time.sleep(3)
    
    speaker.speak("I can help you with various tasks like opening applications, searching the web, and managing your schedule.")
    
    # Wait for speech to finish
    while speaker.is_busy():
        time.sleep(0.1)
    
    print("Speech test completed!")