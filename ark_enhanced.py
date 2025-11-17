"""
ARK Personal AI Assistant - Enhanced Version
==========================================
Enhanced ARK with memory, intent detection, and system integration.
Uses lightweight rule-based responses instead of heavy AI models.
"""

import sys
import os
import logging
import threading
import sqlite3
import yaml
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

# Add the project root to path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/ark.log'),
        logging.StreamHandler()
    ]
)

class EnhancedMemory:
    """Memory system for ARK using SQLite."""
    
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Initialize the database with required tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                assistant_response TEXT,
                session_id TEXT
            )
        """)
        
        # User facts and preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_type TEXT,
                fact_value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fact_type, fact_value)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_conversation(self, user_input: str, response: str, session_id: str = "default"):
        """Add conversation to memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_input, assistant_response, session_id) VALUES (?, ?, ?)",
            (user_input, response, session_id)
        )
        conn.commit()
        conn.close()
    
    def add_user_fact(self, fact_type: str, fact_value: str):
        """Add a user fact to memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO user_facts (fact_type, fact_value) VALUES (?, ?)",
                (fact_type, fact_value)
            )
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding user fact: {e}")
        finally:
            conn.close()
    
    def get_user_fact(self, fact_type: str) -> str:
        """Get a user fact from memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fact_value FROM user_facts WHERE fact_type = ? ORDER BY timestamp DESC LIMIT 1",
            (fact_type,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_recent_conversations(self, limit: int = 5) -> list:
        """Get recent conversations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        conn.close()
        return results

class IntentDetector:
    """Lightweight intent detection for ARK."""
    
    def __init__(self):
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
            'goodbye': ['bye', 'goodbye', 'see you later', 'exit', 'quit'],
            'name_query': ['what is your name', 'who are you', 'your name'],
            'status_query': ['how are you', 'how are you doing', 'how do you feel'],
            'time_query': ['what time', 'current time', 'time is it'],
            'date_query': ['what date', 'today\'s date', 'current date'],
            'calculation': ['calc', 'calculate', 'math', 'compute', 'what is', 'what\'s', '+', '-', '*', '/', 'plus', 'minus', 'times', 'divided'],
            'open_app': ['open', 'launch', 'start', 'run'],
            'web_search': ['search', 'google', 'find', 'look up'],
            'weather': ['weather', 'temperature', 'forecast'],
            'remember_fact': ['remember', 'my name is', 'i am', 'note that'],
            'recall_fact': ['do you remember', 'what do you know about me', 'tell me about'],
            'help': ['help', 'commands', 'what can you do', 'what can u do', 'what are your features', 'what do you do']
        }
    
    def detect_intent(self, text: str) -> str:
        """Detect the intent of user input."""
        import re
        
        text = text.lower().strip()
        
        # Special handling for math expressions
        # Check if text contains math operators or math question patterns
        if (re.search(r'\b(what\s+is|what\'s)\s+[\d\s+\-*/()]+', text) or 
            re.search(r'[\d\s]*[+\-*/][\d\s]*', text) or
            any(word in text for word in ['calc', 'calculate', 'compute', 'plus', 'minus', 'times', 'divided'])):
            return 'calculation'
        
        # Regular keyword matching for other intents
        for intent, keywords in self.intents.items():
            if intent == 'calculation':  # Skip calculation, we handled it above
                continue
            for keyword in keywords:
                if keyword in text:
                    return intent
        
        return 'general'

class EnhancedArk:
    """Enhanced ARK with memory and intent detection."""
    
    def __init__(self):
        self.name = "Ark"
        self.memory = EnhancedMemory()
        self.intent_detector = IntentDetector()
        self.running = False
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load personality config
        try:
            with open("core/personality.yaml", 'r') as f:
                self.personality = yaml.safe_load(f)
        except:
            self.personality = {
                "name": "Ark",
                "traits": ["helpful", "friendly", "professional"],
                "greeting": "Hello! I'm Ark, your personal AI assistant."
            }
        
        print(f"ARK {self.name} Enhanced Version Initialized!")
        print("Features: Memory • Intent Detection • System Integration")
        
    def extract_user_facts(self, text: str, intent: str):
        """Extract and store user facts from conversation."""
        text_lower = text.lower()
        
        if intent == 'remember_fact' or 'my name is' in text_lower:
            if 'my name is' in text_lower:
                name = text_lower.split('my name is')[-1].strip()
                self.memory.add_user_fact('name', name)
                return f"Nice to meet you, {name}! I'll remember that."
            elif 'i am' in text_lower and ('developer' in text_lower or 'engineer' in text_lower):
                self.memory.add_user_fact('profession', 'developer')
                return "Great! I've noted that you're a developer."
        
        return None
    
    def handle_intent(self, text: str, intent: str) -> str:
        """Handle different types of intents."""
        
        # Check for user facts first
        fact_response = self.extract_user_facts(text, intent)
        if fact_response:
            return fact_response
        
        if intent == 'greeting':
            user_name = self.memory.get_user_fact('name')
            if user_name:
                return f"Hello {user_name}! Great to see you again. How can I help you today?"
            return self.personality.get('greeting', f"Hello! I'm {self.name}, your personal AI assistant. How can I help you?")
        
        elif intent == 'goodbye':
            return "Goodbye! It was great talking with you. Have a wonderful day!"
        
        elif intent == 'name_query':
            return f"I'm {self.name}, your personal AI assistant. I have memory capabilities and can help you with various tasks!"
        
        elif intent == 'status_query':
            return "I'm doing great! My memory is working well, and I'm ready to help you with anything you need."
        
        elif intent == 'time_query':
            return f"The current time is: {datetime.now().strftime('%I:%M %p')}"
        
        elif intent == 'date_query':
            return f"Today's date is: {datetime.now().strftime('%B %d, %Y')}"
        
        elif intent == 'calculation':
            return self.handle_calculation(text)
        
        elif intent == 'open_app':
            return self.handle_open_app(text)
        
        elif intent == 'web_search':
            return self.handle_web_search(text)
        
        elif intent == 'recall_fact':
            return self.handle_recall_facts()
        
        elif intent == 'help':
            return self.get_help_text()
        
        else:
            # General conversation
            user_name = self.memory.get_user_fact('name')
            if user_name:
                return f"I heard you say: '{text}'. I remember you're {user_name}. How can I help you with that?"
            return f"I heard you say: '{text}'. I have memory and intent detection active. Try asking me to remember something or help with a task!"
    
    def handle_calculation(self, text: str) -> str:
        """Handle mathematical calculations."""
        import re
        
        text = text.lower().strip()
        
        # Handle natural language math like "what is 1 + 3"
        if 'what is' in text or 'what\'s' in text:
            # Extract everything after "what is" or "what's"
            if 'what is' in text:
                expression = text.split('what is')[-1].strip()
            else:
                expression = text.split('what\'s')[-1].strip()
        else:
            # Handle explicit calc commands
            for prefix in ['calc', 'calculate', 'compute', 'math']:
                if prefix in text:
                    expression = text.split(prefix)[-1].strip()
                    break
            else:
                # If no prefix found, treat the whole thing as an expression
                expression = text
        
        # Convert word numbers to operators
        expression = expression.replace(' plus ', ' + ')
        expression = expression.replace(' minus ', ' - ')
        expression = expression.replace(' times ', ' * ')
        expression = expression.replace(' multiplied by ', ' * ')
        expression = expression.replace(' divided by ', ' / ')
        
        # Clean up the expression
        expression = re.sub(r'[^0-9+\-*/().\s]', '', expression).strip()
        
        if not expression:
            return "I didn't find a math expression. Try: 'what is 2 + 3' or 'calc 5 * 4'"
        
        try:
            # Safe evaluation for basic math
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"Sorry, I couldn't calculate '{expression}'. Please use simple math like: what is 2 + 3"
    
    def handle_open_app(self, text: str) -> str:
        """Handle opening applications."""
        text_lower = text.lower()
        
        if 'chrome' in text_lower or 'browser' in text_lower:
            try:
                subprocess.Popen(['chrome'])
                return "Opening Google Chrome for you!"
            except:
                webbrowser.open('https://www.google.com')
                return "Opening your default web browser!"
        
        elif 'notepad' in text_lower:
            try:
                subprocess.Popen(['notepad'])
                return "Opening Notepad for you!"
            except:
                return "Sorry, I couldn't open Notepad."
        
        elif 'calculator' in text_lower:
            try:
                subprocess.Popen(['calc'])
                return "Opening Calculator for you!"
            except:
                return "Sorry, I couldn't open Calculator."
        
        elif 'code' in text_lower or 'vscode' in text_lower:
            try:
                subprocess.Popen(['code'])
                return "Opening Visual Studio Code for you!"
            except:
                return "Sorry, I couldn't open VS Code. Make sure it's installed and in your PATH."
        
        return "I can open: Chrome, Notepad, Calculator, or VS Code. What would you like to open?"
    
    def handle_web_search(self, text: str) -> str:
        """Handle web searches."""
        # Extract search query
        for prefix in ['search', 'google', 'find', 'look up']:
            if prefix in text.lower():
                query = text.lower().replace(prefix, '').strip()
                if query:
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    return f"Searching for '{query}' in your web browser!"
        
        return "What would you like me to search for? Example: search Python tutorials"
    
    def handle_recall_facts(self) -> str:
        """Recall stored user facts."""
        name = self.memory.get_user_fact('name')
        profession = self.memory.get_user_fact('profession')
        
        facts = []
        if name:
            facts.append(f"Your name is {name}")
        if profession:
            facts.append(f"You work as a {profession}")
        
        if facts:
            return f"Here's what I remember about you: {', '.join(facts)}."
        else:
            return "I don't have any specific facts about you yet. Try telling me something like 'My name is...' or 'I am a developer'."
    
    def get_help_text(self) -> str:
        """Return help information."""
        return """ARK Enhanced Features:

** Conversation:**
• Hi/Hello - Greet me
• How are you - Check my status
• What's your name - Learn about me

** Memory System:**
• My name is [name] - I'll remember your name
• I am a [profession] - I'll remember your job
• Do you remember me? - Recall stored facts

** System Integration:**
• Open Chrome/Notepad/Calculator/VS Code
• Search [query] - Web search
• What is [math] - Calculator (e.g., what is 2+3)

** Utilities:**
• What time is it? - Current time
• What's the date? - Current date
• Help - Show this menu
• Exit/Quit - Close ARK

I have persistent memory and will remember our conversations!"""
    
    def respond(self, user_input: str) -> str:
        """Generate response with intent detection and memory."""
        intent = self.intent_detector.detect_intent(user_input)
        response = self.handle_intent(user_input, intent)
        
        # Store conversation in memory
        self.memory.add_conversation(user_input, response, self.session_id)
        
        return response
    
    def run(self):
        """Run the enhanced text interface."""
        self.running = True
        print(f"\nArk {self.name} Enhanced is ready!")
        
        # Check if user is returning
        user_name = self.memory.get_user_fact('name')
        if user_name:
            print(f"Welcome back, {user_name}! (wave)")
        
        while self.running:
            try:
                user_input = input(f"\nYou: ")
                
                if user_input.lower().strip() in ['exit', 'quit']:
                    print(f"{self.name}: Goodbye! I'll remember our conversation for next time.")
                    break
                    
                response = self.respond(user_input)
                print(f"{self.name}: {response}")
                
            except KeyboardInterrupt:
                print(f"\n{self.name}: Goodbye! I'll remember our conversation.")
                break
            except Exception as e:
                print(f"Error: {e}")
                logging.error(f"Error in main loop: {e}")
        
        self.running = False

def main():
    """Main entry point."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        ark = EnhancedArk()
        ark.run()
        
    except Exception as e:
        print(f"Error starting Ark: {e}")
        logging.error(f"Error starting Ark: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())