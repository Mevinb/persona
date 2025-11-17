"""
ARK Personal AI Assistant - Simple Test Version
===============================================
A simplified version for testing basic functionality without heavy AI models.
"""

import sys
import os
import logging
import threading
from pathlib import Path

# Add the project root to path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/ark_test.log'),
        logging.StreamHandler()
    ]
)

class SimpleArk:
    """Simplified ARK for testing basic functionality."""
    
    def __init__(self):
        self.name = "Ark"
        self.running = False
        print(f"🚀 {self.name} Simple Test Version Initialized!")
        print("Type 'help' for commands or 'exit' to quit")
        
    def respond(self, user_input: str) -> str:
        """Simple response system."""
        user_input = user_input.lower().strip()
        
        if user_input in ['hi', 'hello', 'hey']:
            return f"Hello! I'm {self.name}, your personal AI assistant. How can I help you?"
        elif user_input in ['how are you', 'how are you doing']:
            return "I'm doing great! Thanks for asking. Ready to help you with anything you need."
        elif user_input in ['what is your name', 'who are you']:
            return f"I'm {self.name}, your personal AI assistant. I'm here to help you!"
        elif user_input == 'help':
            return """Available commands:
• hi/hello - Say hello
• how are you - Check how I'm doing  
• what is your name - Learn about me
• time - Get current time
• calc [expression] - Simple calculator
• exit/quit - Exit the program"""
        elif user_input == 'time':
            from datetime import datetime
            return f"The current time is: {datetime.now().strftime('%I:%M %p on %B %d, %Y')}"
        elif user_input.startswith('calc '):
            try:
                expression = user_input[5:]
                # Simple math evaluation (safe for basic operations)
                result = eval(expression, {"__builtins__": {}}, {})
                return f"{expression} = {result}"
            except:
                return "Sorry, I couldn't calculate that. Please use simple math like: calc 2+2"
        elif user_input in ['exit', 'quit']:
            return "Goodbye! It was nice talking to you."
        else:
            return f"I heard you say: '{user_input}'. I'm in test mode, so my responses are limited. Try 'help' for available commands."
    
    def run(self):
        """Run the simple text interface."""
        self.running = True
        print(f"\n💬 {self.name} is ready! (Simple Test Mode)")
        
        while self.running:
            try:
                user_input = input(f"\nYou: ")
                
                if user_input.lower().strip() in ['exit', 'quit']:
                    print(f"{self.name}: Goodbye! It was nice talking to you.")
                    break
                    
                response = self.respond(user_input)
                print(f"{self.name}: {response}")
                
            except KeyboardInterrupt:
                print(f"\n{self.name}: Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.running = False

def main():
    """Main entry point."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        ark = SimpleArk()
        ark.run()
        
    except Exception as e:
        print(f"Error starting Ark: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())