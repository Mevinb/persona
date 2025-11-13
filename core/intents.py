"""
ARK Intent Manager Module
=========================
Detects user intents and maps them to specific actions like opening apps,
setting reminders, fetching information, or performing system tasks.
"""

import re
import logging
import subprocess
import webbrowser
import os
import yaml
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json


class Intent:
    """Represents a detected user intent."""
    
    def __init__(self, name: str, confidence: float, parameters: Dict[str, Any] = None):
        self.name = name
        self.confidence = confidence
        self.parameters = parameters or {}
        self.timestamp = datetime.now()


class IntentManager:
    """
    Manages intent recognition and action execution for ARK.
    Maps natural language phrases to specific system actions.
    """
    
    def __init__(self, config_path: str = "data/config.yaml"):
        """
        Initialize the Intent Manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        
        # Intent patterns and actions
        self.intent_patterns: Dict[str, List[str]] = {}
        self.intent_actions: Dict[str, Callable] = {}
        self.applications: Dict[str, str] = {}
        
        # Load configuration
        self._load_config()
        self._setup_default_intents()
        self._setup_applications()
        
        self.logger.info("Intent Manager initialized")
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                intent_config = config.get('intents', {})
                
                # Load custom intent patterns
                self.intent_patterns.update(intent_config.get('patterns', {}))
                
                # Load application paths
                self.applications.update(intent_config.get('applications', {}))
                
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
    
    def _setup_default_intents(self):
        """Setup default intent patterns and actions."""
        
        # System Control Intents
        self.intent_patterns.update({
            "open_application": [
                r"open (?P<app>\w+)",
                r"launch (?P<app>\w+)",
                r"start (?P<app>\w+)",
                r"run (?P<app>\w+)"
            ],
            "close_application": [
                r"close (?P<app>\w+)",
                r"quit (?P<app>\w+)",
                r"exit (?P<app>\w+)",
                r"stop (?P<app>\w+)"
            ],
            "web_search": [
                r"search for (?P<query>.*)",
                r"look up (?P<query>.*)",
                r"find information about (?P<query>.*)",
                r"google (?P<query>.*)"
            ],
            "open_website": [
                r"open (?P<url>https?://.*)",
                r"go to (?P<url>https?://.*)",
                r"visit (?P<url>https?://.*)",
                r"browse to (?P<url>www\..*|.*\.com|.*\.org|.*\.net)"
            ],
            "system_command": [
                r"execute (?P<command>.*)",
                r"run command (?P<command>.*)",
                r"cmd (?P<command>.*)"
            ],
            
            # Time and Scheduling
            "set_reminder": [
                r"remind me (?:to )?(?P<task>.*) (?:in )?(?P<time>\d+) (?P<unit>minutes?|hours?|days?)",
                r"set (?:a )?reminder (?:for )?(?P<task>.*) (?:in )?(?P<time>\d+) (?P<unit>minutes?|hours?|days?)",
                r"alert me about (?P<task>.*) (?:in )?(?P<time>\d+) (?P<unit>minutes?|hours?|days?)"
            ],
            "get_time": [
                r"what time is it",
                r"current time",
                r"tell me the time",
                r"what's the time"
            ],
            "get_date": [
                r"what date is it",
                r"what's today's date",
                r"tell me the date",
                r"current date"
            ],
            
            # Information Requests
            "weather": [
                r"what's the weather (?:like )?(?:in )?(?P<location>.*)?",
                r"weather (?:forecast )?(?:for )?(?P<location>.*)?",
                r"is it raining (?:in )?(?P<location>.*)?",
                r"temperature (?:in )?(?P<location>.*)?"
            ],
            "calculator": [
                r"calculate (?P<expression>.*)",
                r"what's (?P<expression>\d+.*[\+\-\*/].*\d+)",
                r"compute (?P<expression>.*)",
                r"solve (?P<expression>.*)"
            ],
            
            # File Operations
            "create_file": [
                r"create (?:a )?file (?:called )?(?P<filename>.*)",
                r"make (?:a )?file (?:named )?(?P<filename>.*)",
                r"new file (?P<filename>.*)"
            ],
            "open_file": [
                r"open (?:the )?file (?P<filename>.*)",
                r"show me (?P<filename>.*)",
                r"display (?P<filename>.*)"
            ],
            
            # Memory and Preferences
            "remember_fact": [
                r"remember (?:that )?(?P<fact>.*)",
                r"save (?:the )?(?:fact )?(?:that )?(?P<fact>.*)",
                r"store (?P<fact>.*)"
            ],
            "set_preference": [
                r"set (?P<key>\w+) to (?P<value>.*)",
                r"change (?P<key>\w+) to (?P<value>.*)",
                r"update (?P<key>\w+) to (?P<value>.*)"
            ],
            "get_preference": [
                r"what's my (?P<key>\w+)",
                r"get my (?P<key>\w+)",
                r"show my (?P<key>\w+)"
            ],
            
            # General Conversation
            "greeting": [
                r"hello|hi|hey|good morning|good afternoon|good evening",
                r"how are you",
                r"what's up"
            ],
            "goodbye": [
                r"goodbye|bye|see you later|talk to you later",
                r"good night|goodnight"
            ],
            "help": [
                r"help|what can you do|commands|capabilities",
                r"how to|how do i"
            ]
        })
        
        # Map intents to action methods
        self.intent_actions = {
            "open_application": self._action_open_application,
            "close_application": self._action_close_application,
            "web_search": self._action_web_search,
            "open_website": self._action_open_website,
            "system_command": self._action_system_command,
            "set_reminder": self._action_set_reminder,
            "get_time": self._action_get_time,
            "get_date": self._action_get_date,
            "weather": self._action_weather,
            "calculator": self._action_calculator,
            "create_file": self._action_create_file,
            "open_file": self._action_open_file,
            "remember_fact": self._action_remember_fact,
            "set_preference": self._action_set_preference,
            "get_preference": self._action_get_preference,
            "greeting": self._action_greeting,
            "goodbye": self._action_goodbye,
            "help": self._action_help
        }
    
    def _setup_applications(self):
        """Setup common application mappings."""
        default_apps = {
            # Browsers
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            
            # Productivity
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            
            # Development
            "vscode": "code.exe",
            "visualstudio": "devenv.exe",
            "git": "git-bash.exe",
            
            # Media
            "vlc": "vlc.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            
            # System
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "settings": "ms-settings:",
        }
        
        # Add defaults if not in config
        for app, path in default_apps.items():
            if app not in self.applications:
                self.applications[app] = path
    
    def detect_intent(self, user_input: str) -> Optional[Intent]:
        """
        Detect intent from user input.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Detected Intent object or None
        """
        user_input_lower = user_input.lower().strip()
        
        # Try to match against each intent pattern
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input_lower, re.IGNORECASE)
                if match:
                    parameters = match.groupdict()
                    confidence = self._calculate_confidence(pattern, user_input_lower)
                    
                    intent = Intent(intent_name, confidence, parameters)
                    self.logger.info(f"Detected intent: {intent_name} (confidence: {confidence:.2f})")
                    return intent
        
        # No intent detected
        return None
    
    def _calculate_confidence(self, pattern: str, user_input: str) -> float:
        """
        Calculate confidence score for pattern match.
        
        Args:
            pattern: Matched regex pattern
            user_input: User input string
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence based on pattern specificity and input length
        pattern_length = len(pattern.replace(r"\w+", "").replace(r".*", ""))
        input_length = len(user_input)
        
        if input_length == 0:
            return 0.0
        
        # Base confidence from pattern match
        base_confidence = min(pattern_length / input_length, 1.0)
        
        # Adjust for exact matches
        if pattern_length == input_length:
            base_confidence = 1.0
        
        return max(0.1, min(base_confidence * 1.2, 1.0))
    
    def execute_intent(self, intent: Intent) -> Tuple[bool, str]:
        """
        Execute the action for a detected intent.
        
        Args:
            intent: Intent object to execute
            
        Returns:
            Tuple of (success, message)
        """
        if intent.name not in self.intent_actions:
            return False, f"No action defined for intent: {intent.name}"
        
        try:
            action_function = self.intent_actions[intent.name]
            success, message = action_function(intent.parameters)
            
            if success:
                self.logger.info(f"Successfully executed intent: {intent.name}")
            else:
                self.logger.warning(f"Failed to execute intent: {intent.name} - {message}")
            
            return success, message
            
        except Exception as e:
            error_msg = f"Error executing intent {intent.name}: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    # Action Methods
    def _action_open_application(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Open an application."""
        app_name = params.get("app", "").lower()
        
        if app_name not in self.applications:
            return False, f"Application '{app_name}' not found in configuration."
        
        try:
            app_path = self.applications[app_name]
            
            if app_path.startswith("ms-"):
                # Windows settings URI
                os.system(f"start {app_path}")
            else:
                subprocess.Popen(app_path, shell=True)
            
            return True, f"Opened {app_name}"
            
        except Exception as e:
            return False, f"Failed to open {app_name}: {e}"
    
    def _action_close_application(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Close an application."""
        app_name = params.get("app", "").lower()
        
        try:
            # Use taskkill on Windows
            subprocess.run(f"taskkill /F /IM {app_name}.exe", shell=True, capture_output=True)
            return True, f"Closed {app_name}"
            
        except Exception as e:
            return False, f"Failed to close {app_name}: {e}"
    
    def _action_web_search(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Perform a web search."""
        query = params.get("query", "")
        
        if not query:
            return False, "No search query provided"
        
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True, f"Searching for '{query}'"
            
        except Exception as e:
            return False, f"Failed to perform search: {e}"
    
    def _action_open_website(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Open a website."""
        url = params.get("url", "")
        
        if not url:
            return False, "No URL provided"
        
        # Add protocol if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            webbrowser.open(url)
            return True, f"Opening {url}"
            
        except Exception as e:
            return False, f"Failed to open website: {e}"
    
    def _action_system_command(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Execute a system command."""
        command = params.get("command", "")
        
        if not command:
            return False, "No command provided"
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip() if result.stdout else "Command executed successfully"
                return True, output
            else:
                return False, f"Command failed: {result.stderr.strip()}"
                
        except Exception as e:
            return False, f"Failed to execute command: {e}"
    
    def _action_set_reminder(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Set a reminder (placeholder - needs scheduling system)."""
        task = params.get("task", "")
        time_str = params.get("time", "")
        unit = params.get("unit", "")
        
        if not all([task, time_str, unit]):
            return False, "Incomplete reminder parameters"
        
        try:
            time_value = int(time_str)
            
            # Convert to timedelta
            if "minute" in unit:
                delta = timedelta(minutes=time_value)
            elif "hour" in unit:
                delta = timedelta(hours=time_value)
            elif "day" in unit:
                delta = timedelta(days=time_value)
            else:
                return False, f"Unsupported time unit: {unit}"
            
            reminder_time = datetime.now() + delta
            
            # TODO: Implement actual reminder scheduling
            return True, f"Reminder set for '{task}' in {time_value} {unit} (at {reminder_time.strftime('%H:%M')})"
            
        except ValueError:
            return False, "Invalid time value"
    
    def _action_get_time(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Get current time."""
        current_time = datetime.now().strftime("%I:%M %p")
        return True, f"The current time is {current_time}"
    
    def _action_get_date(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Get current date."""
        current_date = datetime.now().strftime("%B %d, %Y")
        return True, f"Today is {current_date}"
    
    def _action_weather(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Get weather information (placeholder - needs weather API)."""
        location = params.get("location", "your area")
        return True, f"I'd love to tell you the weather for {location}, but I need a weather API to be configured first!"
    
    def _action_calculator(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Perform calculation."""
        expression = params.get("expression", "")
        
        if not expression:
            return False, "No expression provided"
        
        try:
            # Simple safe evaluation for basic math
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return False, "Invalid characters in expression"
            
            result = eval(expression)
            return True, f"{expression} = {result}"
            
        except Exception as e:
            return False, f"Calculation error: {e}"
    
    def _action_create_file(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Create a new file."""
        filename = params.get("filename", "")
        
        if not filename:
            return False, "No filename provided"
        
        try:
            # Create in current directory
            with open(filename, 'w') as f:
                f.write("")
            return True, f"Created file: {filename}"
            
        except Exception as e:
            return False, f"Failed to create file: {e}"
    
    def _action_open_file(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Open a file."""
        filename = params.get("filename", "")
        
        if not filename:
            return False, "No filename provided"
        
        try:
            os.startfile(filename)  # Windows specific
            return True, f"Opened file: {filename}"
            
        except Exception as e:
            return False, f"Failed to open file: {e}"
    
    def _action_remember_fact(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Remember a fact (requires memory manager)."""
        fact = params.get("fact", "")
        
        if not fact:
            return False, "No fact provided"
        
        # TODO: Integrate with MemoryManager
        return True, f"I'll remember that: {fact}"
    
    def _action_set_preference(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Set a user preference (requires memory manager)."""
        key = params.get("key", "")
        value = params.get("value", "")
        
        if not key or not value:
            return False, "Incomplete preference parameters"
        
        # TODO: Integrate with MemoryManager
        return True, f"Set {key} to {value}"
    
    def _action_get_preference(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Get a user preference (requires memory manager)."""
        key = params.get("key", "")
        
        if not key:
            return False, "No preference key provided"
        
        # TODO: Integrate with MemoryManager
        return True, f"Your {key} preference would be shown here"
    
    def _action_greeting(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Handle greeting."""
        return True, "Hello! I'm Ark, your personal assistant. How can I help you today?"
    
    def _action_goodbye(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Handle goodbye."""
        return True, "Goodbye! It was nice talking with you. Have a great day!"
    
    def _action_help(self, params: Dict[str, str]) -> Tuple[bool, str]:
        """Show help information."""
        help_text = """I can help you with:
        
• Open applications (open chrome, launch notepad)
• Web searches (search for python tutorials)
• System commands (execute dir, run command)
• Set reminders (remind me to call mom in 2 hours)
• Get time and date
• Basic calculations
• File operations
• And much more!

Just tell me what you'd like to do in natural language."""
        
        return True, help_text


if __name__ == "__main__":
    # Test the Intent Manager
    logging.basicConfig(level=logging.INFO)
    
    intent_manager = IntentManager()
    
    test_phrases = [
        "open chrome",
        "search for python tutorials",
        "what time is it",
        "remind me to call mom in 2 hours",
        "calculate 15 * 8",
        "hello",
        "help"
    ]
    
    for phrase in test_phrases:
        print(f"\nTesting: '{phrase}'")
        intent = intent_manager.detect_intent(phrase)
        if intent:
            print(f"Intent: {intent.name} (confidence: {intent.confidence:.2f})")
            print(f"Parameters: {intent.parameters}")
            
            success, message = intent_manager.execute_intent(intent)
            print(f"Execution: {success} - {message}")
        else:
            print("No intent detected")