"""
ARK Text UI Module
==================
Provides command-line interface for interacting with ARK when voice I/O is not available.
Includes conversation history, commands, and interactive features.
"""

import os
import sys
import logging
import threading
import time
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path
import colorama
from colorama import Fore, Back, Style


# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)


class TextUI:
    """
    Command-line interface for ARK assistant.
    Provides interactive text-based conversation and system commands.
    """
    
    def __init__(self, name: str = "Ark"):
        """
        Initialize the Text UI.
        
        Args:
            name: Assistant name to display
        """
        self.logger = logging.getLogger(__name__)
        self.assistant_name = name
        self.is_running = False
        self.show_timestamps = True
        self.show_colors = True
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_user_input: Optional[Callable[[str], str]] = None
        self.on_command: Optional[Callable[[str, List[str]], str]] = None
        self.on_exit: Optional[Callable] = None
        
        # UI State
        self.input_thread: Optional[threading.Thread] = None
        self.output_buffer: List[str] = []
        
        # Commands
        self.commands = {
            'help': self._cmd_help,
            'clear': self._cmd_clear,
            'history': self._cmd_history,
            'status': self._cmd_status,
            'settings': self._cmd_settings,
            'save': self._cmd_save,
            'load': self._cmd_load,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit
        }
        
        self.logger.info("Text UI initialized")
    
    def start(self, 
              on_user_input: Callable[[str], str] = None,
              on_command: Callable[[str, List[str]], str] = None,
              on_exit: Callable = None):
        """
        Start the interactive text interface.
        
        Args:
            on_user_input: Callback for user messages (returns assistant response)
            on_command: Callback for system commands
            on_exit: Callback when user exits
        """
        self.on_user_input = on_user_input
        self.on_command = on_command
        self.on_exit = on_exit
        
        self.is_running = True
        
        # Show welcome message
        self._show_welcome()
        
        # Start main loop
        self._run_main_loop()
    
    def stop(self):
        """Stop the text interface."""
        self.is_running = False
        self.logger.info("Text UI stopped")
    
    def _show_welcome(self):
        """Display welcome message and instructions."""
        if self.show_colors:
            print(f"\n{Fore.CYAN}{'=' * 60}")
            print(f"{Fore.CYAN}🤖 Welcome to {self.assistant_name} - Personal AI Assistant")
            print(f"{Fore.CYAN}{'=' * 60}")
            print(f"{Fore.YELLOW}Type 'help' for commands or just start chatting!")
            print(f"{Fore.YELLOW}Type 'exit' or 'quit' to leave.")
            print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
        else:
            print(f"\n{'=' * 60}")
            print(f"🤖 Welcome to {self.assistant_name} - Personal AI Assistant")
            print(f"{'=' * 60}")
            print("Type 'help' for commands or just start chatting!")
            print("Type 'exit' or 'quit' to leave.")
            print(f"{'=' * 60}\n")
    
    def _run_main_loop(self):
        """Main interactive loop."""
        while self.is_running:
            try:
                # Get user input
                user_input = self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Check if it's a command
                if user_input.startswith('/'):
                    self._handle_command(user_input[1:])
                    continue
                
                # Process as regular conversation
                self._handle_conversation(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Interrupted by user. Type 'exit' to quit properly.")
                continue
            except EOFError:
                print(f"\n{Fore.YELLOW}Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self._print_error(f"An error occurred: {e}")
    
    def _get_user_input(self) -> str:
        """Get input from user with prompt."""
        timestamp = self._get_timestamp()
        
        if self.show_colors:
            prompt = f"{Fore.GREEN}[{timestamp}] You: {Style.RESET_ALL}"
        else:
            prompt = f"[{timestamp}] You: "
        
        try:
            user_input = input(prompt).strip()
            return user_input
        except KeyboardInterrupt:
            raise
        except EOFError:
            raise
        except Exception as e:
            self.logger.error(f"Input error: {e}")
            return ""
    
    def _handle_conversation(self, user_input: str):
        """Handle regular conversation input."""
        # Add to history
        self._add_to_history("user", user_input)
        
        # Get response from callback
        if self.on_user_input:
            try:
                response = self.on_user_input(user_input)
                if response:
                    self._show_assistant_response(response)
                    self._add_to_history("assistant", response)
                else:
                    self._print_error("No response received from assistant")
            except Exception as e:
                self.logger.error(f"Error getting response: {e}")
                self._print_error(f"Error processing your message: {e}")
        else:
            self._print_error("No response handler configured")
    
    def _handle_command(self, command_line: str):
        """Handle system commands."""
        parts = command_line.split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                result = self.commands[command](args)
                if result:
                    self._print_info(result)
            except Exception as e:
                self.logger.error(f"Command error: {e}")
                self._print_error(f"Error executing command: {e}")
        elif self.on_command:
            try:
                result = self.on_command(command, args)
                if result:
                    self._print_info(result)
            except Exception as e:
                self.logger.error(f"External command error: {e}")
                self._print_error(f"Error executing command: {e}")
        else:
            self._print_error(f"Unknown command: {command}. Type '/help' for available commands.")
    
    def _show_assistant_response(self, response: str):
        """Display assistant response with formatting."""
        timestamp = self._get_timestamp()
        
        if self.show_colors:
            print(f"{Fore.BLUE}[{timestamp}] {self.assistant_name}: {Style.RESET_ALL}{response}")
        else:
            print(f"[{timestamp}] {self.assistant_name}: {response}")
    
    def _add_to_history(self, role: str, message: str):
        """Add message to conversation history."""
        entry = {
            'role': role,
            'message': message,
            'timestamp': self._get_timestamp(),
            'time': time.time()
        }
        self.conversation_history.append(entry)
        
        # Keep only last 100 entries
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp."""
        if self.show_timestamps:
            return time.strftime("%H:%M:%S")
        return ""
    
    def _print_info(self, message: str):
        """Print info message."""
        if self.show_colors:
            print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ {message}")
    
    def _print_success(self, message: str):
        """Print success message."""
        if self.show_colors:
            print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            print(f"✓ {message}")
    
    def _print_warning(self, message: str):
        """Print warning message."""
        if self.show_colors:
            print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        else:
            print(f"⚠ {message}")
    
    def _print_error(self, message: str):
        """Print error message."""
        if self.show_colors:
            print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        else:
            print(f"✗ {message}")
    
    # Built-in Commands
    def _cmd_help(self, args: List[str]) -> str:
        """Show help information."""
        help_text = f"""
{Fore.CYAN if self.show_colors else ''}Available Commands:{Style.RESET_ALL if self.show_colors else ''}

{Fore.YELLOW if self.show_colors else ''}/help{Style.RESET_ALL if self.show_colors else ''} - Show this help message
{Fore.YELLOW if self.show_colors else ''}/clear{Style.RESET_ALL if self.show_colors else ''} - Clear the screen
{Fore.YELLOW if self.show_colors else ''}/history [n]{Style.RESET_ALL if self.show_colors else ''} - Show conversation history (last n messages)
{Fore.YELLOW if self.show_colors else ''}/status{Style.RESET_ALL if self.show_colors else ''} - Show system status
{Fore.YELLOW if self.show_colors else ''}/settings{Style.RESET_ALL if self.show_colors else ''} - Show/modify settings
{Fore.YELLOW if self.show_colors else ''}/save [filename]{Style.RESET_ALL if self.show_colors else ''} - Save conversation history
{Fore.YELLOW if self.show_colors else ''}/load [filename]{Style.RESET_ALL if self.show_colors else ''} - Load conversation history
{Fore.YELLOW if self.show_colors else ''}/exit, /quit{Style.RESET_ALL if self.show_colors else ''} - Exit the program

{Fore.CYAN if self.show_colors else ''}Tips:{Style.RESET_ALL if self.show_colors else ''}
• Just type normally to chat with {self.assistant_name}
• Commands start with '/' (slash)
• Use Ctrl+C to interrupt, then type '/exit' to quit properly
        """.strip()
        
        print(help_text)
        return ""
    
    def _cmd_clear(self, args: List[str]) -> str:
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return "Screen cleared"
    
    def _cmd_history(self, args: List[str]) -> str:
        """Show conversation history."""
        num_entries = 10  # Default
        
        if args:
            try:
                num_entries = int(args[0])
            except ValueError:
                return "Invalid number for history count"
        
        if not self.conversation_history:
            return "No conversation history available"
        
        recent_history = self.conversation_history[-num_entries:]
        
        print(f"\n{Fore.CYAN if self.show_colors else ''}Conversation History (last {len(recent_history)} messages):{Style.RESET_ALL if self.show_colors else ''}")
        print("-" * 50)
        
        for entry in recent_history:
            role_color = Fore.GREEN if entry['role'] == 'user' else Fore.BLUE
            role_name = "You" if entry['role'] == 'user' else self.assistant_name
            
            if self.show_colors:
                print(f"{role_color}[{entry['timestamp']}] {role_name}: {Style.RESET_ALL}{entry['message']}")
            else:
                print(f"[{entry['timestamp']}] {role_name}: {entry['message']}")
        
        print("-" * 50)
        return ""
    
    def _cmd_status(self, args: List[str]) -> str:
        """Show system status."""
        status_info = f"""
{Fore.CYAN if self.show_colors else ''}System Status:{Style.RESET_ALL if self.show_colors else ''}

• Assistant: {self.assistant_name}
• UI Running: {self.is_running}
• Conversation entries: {len(self.conversation_history)}
• Colors enabled: {self.show_colors}
• Timestamps enabled: {self.show_timestamps}
• Platform: {sys.platform}
• Python: {sys.version.split()[0]}
        """.strip()
        
        print(status_info)
        return ""
    
    def _cmd_settings(self, args: List[str]) -> str:
        """Show or modify settings."""
        if not args:
            settings_info = f"""
{Fore.CYAN if self.show_colors else ''}Current Settings:{Style.RESET_ALL if self.show_colors else ''}

• colors: {self.show_colors} (enable/disable colored output)
• timestamps: {self.show_timestamps} (show/hide timestamps)

Usage: /settings <setting> <value>
Example: /settings colors false
            """.strip()
            print(settings_info)
            return ""
        
        if len(args) < 2:
            return "Usage: /settings <setting> <value>"
        
        setting = args[0].lower()
        value = args[1].lower()
        
        if setting == "colors":
            if value in ["true", "on", "yes", "1"]:
                self.show_colors = True
                return "Colors enabled"
            elif value in ["false", "off", "no", "0"]:
                self.show_colors = False
                return "Colors disabled"
        elif setting == "timestamps":
            if value in ["true", "on", "yes", "1"]:
                self.show_timestamps = True
                return "Timestamps enabled"
            elif value in ["false", "off", "no", "0"]:
                self.show_timestamps = False
                return "Timestamps disabled"
        
        return f"Unknown setting '{setting}' or invalid value '{value}'"
    
    def _cmd_save(self, args: List[str]) -> str:
        """Save conversation history."""
        filename = args[0] if args else f"conversation_{int(time.time())}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Conversation with {self.assistant_name}\n")
                f.write(f"Saved on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in self.conversation_history:
                    role_name = "You" if entry['role'] == 'user' else self.assistant_name
                    f.write(f"[{entry['timestamp']}] {role_name}: {entry['message']}\n\n")
            
            return f"Conversation saved to: {filename}"
            
        except Exception as e:
            return f"Failed to save conversation: {e}"
    
    def _cmd_load(self, args: List[str]) -> str:
        """Load conversation history (placeholder)."""
        if not args:
            return "Usage: /load <filename>"
        
        filename = args[0]
        
        if not os.path.exists(filename):
            return f"File not found: {filename}"
        
        return "Load feature not yet implemented"
    
    def _cmd_exit(self, args: List[str]) -> str:
        """Exit the program."""
        self.stop()
        
        if self.on_exit:
            self.on_exit()
        
        print(f"\n{Fore.YELLOW if self.show_colors else ''}Goodbye! Thanks for using {self.assistant_name}.{Style.RESET_ALL if self.show_colors else ''}")
        return ""
    
    def display_message(self, message: str, message_type: str = "info"):
        """
        Display a message from external source.
        
        Args:
            message: Message to display
            message_type: Type of message (info, success, warning, error)
        """
        if message_type == "info":
            self._print_info(message)
        elif message_type == "success":
            self._print_success(message)
        elif message_type == "warning":
            self._print_warning(message)
        elif message_type == "error":
            self._print_error(message)
        else:
            print(message)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        self._print_success("Conversation history cleared")


if __name__ == "__main__":
    # Test the Text UI
    def mock_response(user_input: str) -> str:
        """Mock assistant response for testing."""
        return f"I heard you say: '{user_input}'. This is a test response!"
    
    def mock_command(command: str, args: List[str]) -> str:
        """Mock command handler for testing."""
        return f"Executed command '{command}' with args: {args}"
    
    def on_exit():
        """Handle exit."""
        print("Cleanup completed.")
    
    ui = TextUI("TestArk")
    
    try:
        ui.start(
            on_user_input=mock_response,
            on_command=mock_command,
            on_exit=on_exit
        )
    except KeyboardInterrupt:
        ui.stop()