"""
ARK Personal AI Assistant - Voice Enabled Version
===============================================
Enhanced ARK with voice input/output capabilities using the existing speaker module.
"""

import sys
import os
import logging
import threading
import time
from pathlib import Path

# Add the project root to path
sys.path.append(str(Path(__file__).parent))

# Import from our enhanced version
from ark_enhanced import EnhancedArk

# Import voice components (gracefully handle missing dependencies)
try:
    # Import from our modules
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from io.speaker import Speaker
    SPEAKER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Speaker not available: {e}")
    SPEAKER_AVAILABLE = False

try:
    import sounddevice as sd
    import numpy as np
    from faster_whisper import WhisperModel
    VOICE_INPUT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice input not available: {e}")
    VOICE_INPUT_AVAILABLE = False

class SimpleVoiceInput:
    """Simple voice input using faster-whisper (without webrtcvad)."""
    
    def __init__(self):
        self.model = None
        self.recording = False
        self.sample_rate = 16000
        
        if VOICE_INPUT_AVAILABLE:
            try:
                print("Loading Whisper model... (this may take a moment)")
                self.model = WhisperModel("base", device="cpu")
                print("Voice input ready!")
            except Exception as e:
                logging.error(f"Failed to load Whisper model: {e}")
                self.model = None
    
    def record_audio(self, duration: int = 3) -> str:
        """Record audio for specified duration and transcribe."""
        if not self.model:
            return "Voice input not available"
        
        try:
            print(f"🎤 Recording for {duration} seconds... Speak now!")
            audio = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=1, 
                          dtype=np.float32)
            sd.wait()
            print("🔄 Processing...")
            
            # Save temporarily for whisper
            audio_path = "temp_audio.wav"
            import wave
            with wave.open(audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio * 32767).astype(np.int16).tobytes())
            
            # Transcribe
            segments, info = self.model.transcribe(audio_path)
            text = " ".join([segment.text for segment in segments]).strip()
            
            # Clean up
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return text if text else "No speech detected"
            
        except Exception as e:
            logging.error(f"Recording error: {e}")
            return f"Recording error: {e}"

class VoiceEnabledArk(EnhancedArk):
    """ARK with voice input and output capabilities."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize voice components
        self.speaker = None
        self.voice_input = None
        
        if SPEAKER_AVAILABLE:
            try:
                self.speaker = Speaker()
                print("🔊 Voice output ready!")
            except Exception as e:
                logging.warning(f"Speaker initialization failed: {e}")
        
        if VOICE_INPUT_AVAILABLE:
            self.voice_input = SimpleVoiceInput()
        
        self.voice_mode = False
        
        print(f"🎯 Voice Features: Input={VOICE_INPUT_AVAILABLE}, Output={SPEAKER_AVAILABLE}")
    
    def speak(self, text: str):
        """Speak the given text."""
        if self.speaker:
            try:
                self.speaker.speak(text)
            except Exception as e:
                logging.error(f"Speech error: {e}")
                print(f"[Speech Error: {e}]")
        else:
            print(f"[Voice not available: {text}]")
    
    def listen(self, duration: int = 3) -> str:
        """Listen for voice input."""
        if self.voice_input and self.voice_input.model:
            return self.voice_input.record_audio(duration)
        else:
            return "Voice input not available"
    
    def toggle_voice_mode(self):
        """Toggle between text and voice mode."""
        if VOICE_INPUT_AVAILABLE and SPEAKER_AVAILABLE:
            self.voice_mode = not self.voice_mode
            mode_text = "Voice mode ON" if self.voice_mode else "Voice mode OFF"
            print(f"🎤 {mode_text}")
            if self.voice_mode:
                self.speak("Voice mode activated")
            return mode_text
        else:
            return "Voice capabilities not fully available"
    
    def run_voice_mode(self):
        """Run in voice interaction mode."""
        print("🎤 Voice Mode Active!")
        print("Say 'stop voice mode' to return to text mode")
        
        if self.speaker:
            self.speak("Voice mode activated. How can I help you?")
        
        while self.running and self.voice_mode:
            try:
                print("\n🎤 Listening... (3 seconds)")
                user_input = self.listen(3)
                
                if not user_input or user_input == "No speech detected":
                    continue
                    
                print(f"You said: {user_input}")
                
                if "stop voice mode" in user_input.lower():
                    self.voice_mode = False
                    self.speak("Switching to text mode")
                    print("Switched to text mode")
                    break
                
                if user_input.lower().strip() in ['exit', 'quit', 'goodbye']:
                    self.speak("Goodbye!")
                    self.running = False
                    break
                
                response = self.respond(user_input)
                print(f"{self.name}: {response}")
                self.speak(response)
                
            except KeyboardInterrupt:
                self.voice_mode = False
                print("\nReturning to text mode...")
                break
            except Exception as e:
                print(f"Voice mode error: {e}")
                logging.error(f"Voice mode error: {e}")
    
    def run(self):
        """Run the voice-enabled interface."""
        self.running = True
        print(f"\n💬 {self.name} Voice-Enabled is ready!")
        
        # Check if user is returning
        user_name = self.memory.get_user_fact('name')
        if user_name:
            welcome_msg = f"Welcome back, {user_name}!"
            print(f"{welcome_msg} 👋")
            if self.speaker:
                self.speak(welcome_msg)
        
        print("\nCommands:")
        print("• Type normally for text chat")
        print("• Type '/voice' to enable voice mode")
        print("• Type '/help' for full help")
        print("• Type 'exit' to quit")
        
        while self.running:
            try:
                if self.voice_mode:
                    self.run_voice_mode()
                    continue
                
                user_input = input(f"\nYou: ")
                
                if user_input.lower().strip() in ['exit', 'quit']:
                    goodbye_msg = "Goodbye! I'll remember our conversation for next time."
                    print(f"{self.name}: {goodbye_msg}")
                    if self.speaker:
                        self.speak("Goodbye!")
                    break
                
                elif user_input.strip() == '/voice':
                    if VOICE_INPUT_AVAILABLE and SPEAKER_AVAILABLE:
                        self.voice_mode = True
                        continue
                    else:
                        print("Voice capabilities not available. Missing dependencies.")
                        continue
                
                elif user_input.strip() == '/help':
                    help_text = self.get_voice_help_text()
                    print(f"{self.name}: {help_text}")
                    continue
                    
                response = self.respond(user_input)
                print(f"{self.name}: {response}")
                
            except KeyboardInterrupt:
                print(f"\n{self.name}: Goodbye! I'll remember our conversation.")
                break
            except Exception as e:
                print(f"Error: {e}")
                logging.error(f"Error in main loop: {e}")
        
        self.running = False
    
    def get_voice_help_text(self) -> str:
        """Return voice-specific help information."""
        base_help = super().get_help_text()
        voice_help = """

🎤 **Voice Commands:**
• /voice - Enable voice mode
• In voice mode: "stop voice mode" - Return to text
• Voice input automatically transcribed
• Responses spoken aloud

🔧 **Requirements:**
• Voice Input: faster-whisper, sounddevice
• Voice Output: pyttsx3"""
        
        return base_help + voice_help

def main():
    """Main entry point."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        ark = VoiceEnabledArk()
        ark.run()
        
    except Exception as e:
        print(f"Error starting Ark: {e}")
        logging.error(f"Error starting Ark: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())