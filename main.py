#!/usr/bin/env python3
"""
NOVA - Personal AI Assistant
============================
Main orchestrator that brings together all NOVA components for a complete
personal AI assistant experience.

Author: Your Name
Version: 1.0
"""

import sys
import os
import logging
import argparse
import signal
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import NOVA components
from core.brain import Brain
from core.memory import MemoryManager
from core.intents import IntentManager
from io.listener import Listener
from io.speaker import Speaker
from io.text_ui import TextUI

import yaml
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)


class NovaAssistant:
    """
    Main NOVA Assistant class that orchestrates all components.
    Provides voice and text interfaces for interacting with the AI.
    """
    
    def __init__(self, config_path: str = "data/config.yaml"):
        """
        Initialize NOVA Assistant.
        
        Args:
            config_path: Path to configuration file
        """
        # Setup logging first
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.brain: Optional[Brain] = None
        self.memory: Optional[MemoryManager] = None
        self.intents: Optional[IntentManager] = None
        self.listener: Optional[Listener] = None
        self.speaker: Optional[Speaker] = None
        self.text_ui: Optional[TextUI] = None
        
        # State management
        self.is_running = False
        self.voice_mode = False
        self.wake_word_detected = False
        
        # Interface mode
        ui_config = self.config.get('ui', {})
        self.default_interface = ui_config.get('default_interface', 'text')
        
        self.logger.info("NOVA Assistant initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory
        log_dir = Path("data")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "nova.log"),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.logger.info(f"Loaded configuration from {self.config_path}")
                return config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return {}
    
    def initialize_components(self) -> bool:
        """
        Initialize all NOVA components.
        
        Returns:
            True if all components initialized successfully
        """
        try:
            print(f"{Fore.CYAN}🚀 Initializing NOVA components...{Style.RESET_ALL}")
            
            # Initialize Memory Manager
            print(f"{Fore.YELLOW}📚 Initializing Memory Manager...{Style.RESET_ALL}")
            self.memory = MemoryManager(self.config.get('memory', {}).get('database_path', 'data/memory.db'))
            print(f"{Fore.GREEN}✓ Memory Manager ready{Style.RESET_ALL}")
            
            # Initialize Intent Manager
            print(f"{Fore.YELLOW}🎯 Initializing Intent Manager...{Style.RESET_ALL}")
            self.intents = IntentManager(self.config_path)
            print(f"{Fore.GREEN}✓ Intent Manager ready{Style.RESET_ALL}")
            
            # Initialize Brain (AI Model)
            print(f"{Fore.YELLOW}🧠 Initializing AI Brain...{Style.RESET_ALL}")
            self.brain = Brain(self.config_path)
            if not self.brain.load_model():
                raise RuntimeError("Failed to load AI model")
            print(f"{Fore.GREEN}✓ AI Brain ready{Style.RESET_ALL}")
            
            # Initialize Speaker
            print(f"{Fore.YELLOW}🔊 Initializing Speech Engine...{Style.RESET_ALL}")
            self.speaker = Speaker(self.config_path)
            print(f"{Fore.GREEN}✓ Speech Engine ready{Style.RESET_ALL}")
            
            # Initialize Listener (optional)
            if self.default_interface in ['voice', 'hybrid']:
                print(f"{Fore.YELLOW}🎙️ Initializing Voice Recognition...{Style.RESET_ALL}")
                self.listener = Listener(self.config_path)
                if not self.listener.load_model():
                    self.logger.warning("Failed to load voice recognition model")
                    print(f"{Fore.YELLOW}⚠ Voice recognition not available, using text mode{Style.RESET_ALL}")
                    self.default_interface = 'text'
                else:
                    print(f"{Fore.GREEN}✓ Voice Recognition ready{Style.RESET_ALL}")
            
            # Initialize Text UI
            print(f"{Fore.YELLOW}💬 Initializing Text Interface...{Style.RESET_ALL}")
            self.text_ui = TextUI("Nova")
            print(f"{Fore.GREEN}✓ Text Interface ready{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}🎉 All components initialized successfully!{Style.RESET_ALL}\n")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            print(f"{Fore.RED}❌ Initialization failed: {e}{Style.RESET_ALL}")
            return False
    
    def start(self, interface: str = None):
        """
        Start the NOVA Assistant.
        
        Args:
            interface: Interface mode ('text', 'voice', 'hybrid')
        """
        if not self.brain or not self.memory or not self.intents:
            print(f"{Fore.RED}❌ Components not initialized. Call initialize_components() first.{Style.RESET_ALL}")
            return
        
        interface = interface or self.default_interface
        self.is_running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            if interface == 'text':
                self._start_text_mode()
            elif interface == 'voice':
                self._start_voice_mode()
            elif interface == 'hybrid':
                self._start_hybrid_mode()
            else:
                self.logger.error(f"Unknown interface mode: {interface}")
                self._start_text_mode()  # Fallback to text mode
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Shutdown requested by user{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the NOVA Assistant and cleanup resources."""
        print(f"{Fore.CYAN}🛑 Shutting down NOVA...{Style.RESET_ALL}")
        
        self.is_running = False
        
        # Stop voice components
        if self.listener:
            self.listener.stop_listening()
        
        if self.speaker:
            self.speaker.clear_queue()
        
        # Stop text UI
        if self.text_ui:
            self.text_ui.stop()
        
        # Cleanup brain
        if self.brain:
            self.brain.unload_model()
        
        print(f"{Fore.GREEN}✅ NOVA shutdown complete{Style.RESET_ALL}")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)
    
    def _start_text_mode(self):
        """Start text-only interface."""
        print(f"{Fore.CYAN}💬 Starting NOVA in text mode...{Style.RESET_ALL}\n")
        
        self.text_ui.start(
            on_user_input=self._handle_user_input,
            on_command=self._handle_system_command,
            on_exit=self.stop
        )
    
    def _start_voice_mode(self):
        """Start voice-only interface."""
        if not self.listener:
            print(f"{Fore.RED}❌ Voice recognition not available{Style.RESET_ALL}")
            return self._start_text_mode()
        
        print(f"{Fore.CYAN}🎙️ Starting NOVA in voice mode...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Say '{self.listener.wake_word}' to activate listening{Style.RESET_ALL}\n")
        
        self.voice_mode = True
        
        self.listener.start_listening(
            on_wake_word=self._on_wake_word,
            on_speech_start=self._on_speech_start,
            on_speech_end=self._handle_voice_input,
            on_error=self._on_voice_error
        )
        
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    
    def _start_hybrid_mode(self):
        """Start hybrid text/voice interface."""
        print(f"{Fore.CYAN}🎙️💬 Starting NOVA in hybrid mode...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Use text input or say '{self.listener.wake_word}' for voice{Style.RESET_ALL}\n")
        
        # Start voice listening in background
        if self.listener:
            self.listener.start_listening(
                on_wake_word=self._on_wake_word,
                on_speech_start=self._on_speech_start,
                on_speech_end=self._handle_voice_input,
                on_error=self._on_voice_error
            )
        
        # Start text interface
        self._start_text_mode()
    
    def _handle_user_input(self, user_input: str) -> str:
        """
        Handle user input and generate response.
        
        Args:
            user_input: User's message
            
        Returns:
            Assistant's response
        """
        try:
            # Store user input in memory
            self.memory.update_session_context("last_user_input", user_input)
            
            # Check for intents first
            intent = self.intents.detect_intent(user_input)
            
            if intent and intent.confidence > 0.5:
                # Execute intent action
                success, intent_response = self.intents.execute_intent(intent)
                
                if success:
                    # Generate conversational response about the action
                    context = self.memory.get_recent_conversations(5)
                    prompt = f"User asked: {user_input}\nAction completed: {intent_response}\nRespond conversationally about what was done."
                    
                    brain_response = self.brain.generate_response(prompt, context)
                    full_response = f"{intent_response}\n\n{brain_response}"
                else:
                    full_response = f"I tried to {intent.name}, but encountered an issue: {intent_response}"
            else:
                # Generate AI response
                context = self.memory.get_recent_conversations(5)
                full_response = self.brain.generate_response(user_input, context)
            
            # Store conversation in memory
            self.memory.add_conversation(
                user_input=user_input,
                assistant_response=full_response,
                context={"intent": intent.name if intent else None},
                importance=3 if intent else 2
            )
            
            # Extract user facts if mentioned
            self._extract_user_facts(user_input)
            
            return full_response
            
        except Exception as e:
            self.logger.error(f"Error handling user input: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."
    
    def _handle_voice_input(self, transcribed_text: str):
        """Handle voice input after transcription."""
        if not transcribed_text.strip():
            return
        
        print(f"{Fore.GREEN}You said: {transcribed_text}{Style.RESET_ALL}")
        
        # Process the input
        response = self._handle_user_input(transcribed_text)
        
        # Speak the response
        if self.speaker and response:
            print(f"{Fore.BLUE}Nova: {response}{Style.RESET_ALL}")
            self.speaker.speak(response)
    
    def _handle_system_command(self, command: str, args: list) -> str:
        """Handle system commands."""
        try:
            if command == "status":
                return self._get_system_status()
            elif command == "memory":
                return self._get_memory_status()
            elif command == "voice":
                return self._toggle_voice_mode()
            elif command == "reload":
                return self._reload_components()
            else:
                return f"Unknown command: {command}"
                
        except Exception as e:
            self.logger.error(f"Error handling command {command}: {e}")
            return f"Error executing command: {e}"
    
    def _extract_user_facts(self, user_input: str):
        """Extract and store user facts from conversation."""
        # Simple fact extraction (could be enhanced with NLP)
        lower_input = user_input.lower()
        
        # Name extraction
        if "my name is" in lower_input:
            name = user_input.lower().split("my name is")[-1].strip().split()[0]
            if name:
                self.memory.add_user_fact("name", name.title())
        
        # Age extraction
        if "i am" in lower_input and "years old" in lower_input:
            try:
                age_part = lower_input.split("i am")[-1].split("years old")[0].strip()
                age = int(age_part.split()[-1])
                self.memory.add_user_fact("age", str(age))
            except:
                pass
        
        # Job extraction
        if "i work as" in lower_input or "i am a" in lower_input:
            if "i work as" in lower_input:
                job = lower_input.split("i work as")[-1].strip()
            else:
                job = lower_input.split("i am a")[-1].strip()
            
            if job and len(job.split()) <= 3:  # Reasonable job length
                self.memory.add_user_fact("job", job.title())
    
    def _on_wake_word(self):
        """Handle wake word detection."""
        self.wake_word_detected = True
        print(f"{Fore.GREEN}👂 Wake word detected! Listening...{Style.RESET_ALL}")
        
        if self.speaker:
            self.speaker.speak("Yes?", priority=10, interrupt=True)
    
    def _on_speech_start(self):
        """Handle speech start detection."""
        print(f"{Fore.YELLOW}🎙️ Listening...{Style.RESET_ALL}")
    
    def _on_voice_error(self, error: str):
        """Handle voice recognition errors."""
        self.logger.error(f"Voice error: {error}")
        print(f"{Fore.RED}🎙️ Voice error: {error}{Style.RESET_ALL}")
    
    def _get_system_status(self) -> str:
        """Get system status information."""
        brain_info = self.brain.get_model_info() if self.brain else {}
        memory_stats = self.memory.get_memory_stats() if self.memory else {}
        
        status = f"""
NOVA System Status:
• Brain: {'✓ Loaded' if brain_info.get('loaded') else '❌ Not loaded'}
• Model: {brain_info.get('model_name', 'Unknown')}
• Memory: {memory_stats.get('total_memories', 0)} stored memories
• Voice: {'✓ Available' if self.listener and self.listener.is_model_loaded() else '❌ Not available'}
• Speech: {'✓ Available' if self.speaker else '❌ Not available'}
• Mode: {'Voice' if self.voice_mode else 'Text'}
        """.strip()
        
        return status
    
    def _get_memory_status(self) -> str:
        """Get memory status information."""
        if not self.memory:
            return "Memory not initialized"
        
        stats = self.memory.get_memory_stats()
        facts = self.memory.get_all_user_facts()
        
        status = f"""
Memory Status:
• Total memories: {stats.get('total_memories', 0)}
• Conversations: {stats.get('conversation_memories', 0)}
• User facts: {stats.get('user_facts', 0)}
• Session memories: {stats.get('session_memories', 0)}

Known facts about you:
""".strip()
        
        for fact_type, fact_value in facts.items():
            status += f"\n• {fact_type.title()}: {fact_value}"
        
        return status
    
    def _toggle_voice_mode(self) -> str:
        """Toggle voice mode on/off."""
        if not self.listener:
            return "Voice recognition not available"
        
        if self.voice_mode:
            self.listener.stop_listening()
            self.voice_mode = False
            return "Voice mode disabled"
        else:
            self.listener.start_listening(
                on_wake_word=self._on_wake_word,
                on_speech_start=self._on_speech_start,
                on_speech_end=self._handle_voice_input,
                on_error=self._on_voice_error
            )
            self.voice_mode = True
            return "Voice mode enabled"
    
    def _reload_components(self) -> str:
        """Reload configuration and components."""
        try:
            self.config = self._load_config()
            return "Configuration reloaded successfully"
        except Exception as e:
            return f"Failed to reload configuration: {e}"


def main():
    """Main entry point for NOVA Assistant."""
    parser = argparse.ArgumentParser(description="NOVA - Personal AI Assistant")
    parser.add_argument(
        "--interface", 
        choices=["text", "voice", "hybrid"], 
        default=None,
        help="Interface mode (default: from config)"
    )
    parser.add_argument(
        "--config", 
        default="data/config.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and initialize NOVA
    nova = NovaAssistant(args.config)
    
    # Initialize components
    if not nova.initialize_components():
        print(f"{Fore.RED}❌ Failed to initialize NOVA components{Style.RESET_ALL}")
        sys.exit(1)
    
    # Start the assistant
    try:
        nova.start(args.interface)
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()