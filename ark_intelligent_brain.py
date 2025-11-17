"""
ARK Intelligent Brain - Advanced AI System
==========================================
A hybrid AI system that combines training data, context awareness, and intelligent reasoning
to create a truly capable personal assistant.
"""

import json
import logging
import sqlite3
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yaml

class IntelligentResponseEngine:
    """Advanced response engine that uses training data and context for intelligent responses."""
    
    def __init__(self, training_data_path: str = "ark_comprehensive_training.jsonl"):
        self.training_data = []
        self.context_memory = {}
        self.user_preferences = {}
        self.conversation_history = []
        self.load_training_data(training_data_path)
        
    def load_training_data(self, path: str):
        """Load training data for intelligent responses."""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.training_data.append(json.loads(line))
                print(f"Loaded {len(self.training_data)} training examples")
            else:
                print(f"Training data not found at {path}")
        except Exception as e:
            logging.error(f"Error loading training data: {e}")
    
    def find_similar_scenario(self, user_input: str) -> Optional[Dict]:
        """Find the most similar training scenario."""
        user_input_lower = user_input.lower()
        best_match = None
        best_score = 0
        
        for example in self.training_data:
            for conversation in example.get("conversations", []):
                input_text = conversation.get("input", "").lower()
                
                # Calculate similarity score based on keyword matching
                common_words = set(user_input_lower.split()) & set(input_text.split())
                score = len(common_words) / max(len(user_input_lower.split()), len(input_text.split()))
                
                # Boost score for exact phrase matches
                if any(phrase in user_input_lower for phrase in input_text.split() if len(phrase) > 3):
                    score += 0.3
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        "conversation": conversation,
                        "category": example.get("category", "general"),
                        "complexity": example.get("complexity", "medium"),
                        "score": score
                    }
        
        return best_match if best_score > 0.2 else None
    
    def extract_context(self, user_input: str) -> Dict[str, Any]:
        """Extract context and intent from user input."""
        context = {
            "urgency": self.detect_urgency(user_input),
            "time_reference": self.extract_time_reference(user_input),
            "task_type": self.classify_task_type(user_input),
            "entities": self.extract_entities(user_input),
            "sentiment": self.analyze_sentiment(user_input)
        }
        return context
    
    def detect_urgency(self, text: str) -> str:
        """Detect urgency level in user input."""
        urgent_indicators = ["urgent", "asap", "immediately", "rush", "emergency", "now", "quickly", "deadline"]
        medium_indicators = ["soon", "today", "this week", "important"]
        
        text_lower = text.lower()
        
        if any(indicator in text_lower for indicator in urgent_indicators):
            return "high"
        elif any(indicator in text_lower for indicator in medium_indicators):
            return "medium"
        else:
            return "low"
    
    def extract_time_reference(self, text: str) -> Optional[str]:
        """Extract time references from text."""
        time_patterns = [
            r"tomorrow", r"today", r"next week", r"this week", r"next month",
            r"in \d+ (days?|weeks?|months?)", r"at \d+:\d+ (am|pm|AM|PM)",
            r"on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group()
        return None
    
    def classify_task_type(self, text: str) -> str:
        """Classify the type of task being requested."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["schedule", "meeting", "calendar", "appointment"]):
            return "scheduling"
        elif any(word in text_lower for word in ["organize", "plan", "project", "task"]):
            return "planning"
        elif any(word in text_lower for word in ["find", "search", "research", "look up"]):
            return "information"
        elif any(word in text_lower for word in ["open", "launch", "run", "execute"]):
            return "system_control"
        elif any(word in text_lower for word in ["remember", "note", "save", "store"]):
            return "memory"
        elif any(word in text_lower for word in ["help", "how to", "guide", "explain"]):
            return "guidance"
        else:
            return "general"
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities like names, dates, applications, etc."""
        entities = {
            "applications": [],
            "files": [],
            "people": [],
            "dates": [],
            "numbers": []
        }
        
        # Common applications
        apps = ["chrome", "firefox", "word", "excel", "powerpoint", "outlook", "teams", 
                "slack", "zoom", "notepad", "calculator", "photoshop", "code", "vscode"]
        
        text_lower = text.lower()
        for app in apps:
            if app in text_lower:
                entities["applications"].append(app)
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        entities["numbers"] = numbers
        
        # Extract potential file references
        file_patterns = re.findall(r'\w+\.(doc|pdf|xls|txt|png|jpg|mp4)', text_lower)
        entities["files"] = file_patterns
        
        return entities
    
    def analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis."""
        positive_words = ["good", "great", "excellent", "happy", "pleased", "thanks", "appreciate"]
        negative_words = ["bad", "terrible", "awful", "frustrated", "angry", "annoyed", "problem"]
        stress_words = ["overwhelmed", "stressed", "busy", "deadline", "urgent", "pressure"]
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in stress_words):
            return "stressed"
        elif any(word in text_lower for word in negative_words):
            return "negative"
        elif any(word in text_lower for word in positive_words):
            return "positive"
        else:
            return "neutral"
    
    def generate_intelligent_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generate an intelligent response based on training data and context."""
        
        # Try to find a similar training scenario
        similar_scenario = self.find_similar_scenario(user_input)
        
        if similar_scenario and similar_scenario["score"] > 0.4:
            # Adapt the training response to current context
            base_response = similar_scenario["conversation"]["output"]
            adapted_response = self.adapt_response_to_context(base_response, context)
            return adapted_response
        else:
            # Generate contextual response based on task type and context
            return self.generate_contextual_response(user_input, context)
    
    def adapt_response_to_context(self, base_response: str, context: Dict[str, Any]) -> str:
        """Adapt a training response to current context."""
        adapted = base_response
        
        # Adapt for urgency
        if context["urgency"] == "high":
            adapted = f"I understand this is urgent. {adapted}"
        elif context["sentiment"] == "stressed":
            adapted = f"I can sense you're feeling overwhelmed. Let me help reduce that stress. {adapted}"
        
        # Add time-specific adaptations
        if context["time_reference"]:
            adapted = adapted.replace("schedule", f"schedule for {context['time_reference']}")
        
        return adapted
    
    def generate_contextual_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generate a response based on context when no training match is found."""
        
        task_type = context["task_type"]
        urgency = context["urgency"]
        sentiment = context["sentiment"]
        
        # Base response templates by task type
        templates = {
            "scheduling": "I'll help you with scheduling. Let me check your calendar and find the best time for this.",
            "planning": "Let me help you create a comprehensive plan for this. I'll break it down into manageable steps.",
            "information": "I'll research this information for you and provide you with accurate, relevant details.",
            "system_control": "I'll help you execute this system command efficiently.",
            "memory": "I'll store this information securely and make sure I can recall it when you need it.",
            "guidance": "I'll provide you with step-by-step guidance to accomplish this effectively.",
            "general": "I understand you're looking for assistance. Let me help you with this request."
        }
        
        base_response = templates.get(task_type, templates["general"])
        
        # Adapt for sentiment and urgency
        if sentiment == "stressed":
            base_response = f"I can see this is important to you, and I want to help reduce any stress. {base_response}"
        elif urgency == "high":
            base_response = f"I recognize this is urgent. {base_response} Let me prioritize this for you."
        
        # Add specific action based on entities
        entities = context["entities"]
        if entities["applications"]:
            base_response += f" I notice you mentioned {', '.join(entities['applications'])}. I'll incorporate that into my assistance."
        
        return base_response

class ARKIntelligentBrain:
    """The main intelligent brain for ARK that orchestrates all AI capabilities."""
    
    def __init__(self, memory_db_path: str = "data/memory.db"):
        self.response_engine = IntelligentResponseEngine()
        self.memory_db_path = memory_db_path
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.init_memory()
        
        # Load user preferences and context
        self.load_user_preferences()
        
    def init_memory(self):
        """Initialize the memory system."""
        os.makedirs(os.path.dirname(self.memory_db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # Enhanced memory tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                assistant_response TEXT,
                session_id TEXT,
                context JSON,
                response_quality_score INTEGER DEFAULT 3
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_type TEXT,
                preference_value TEXT,
                confidence_score REAL DEFAULT 0.5,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_description TEXT,
                task_type TEXT,
                completion_status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success_score INTEGER DEFAULT 3
            )
        """)
        
        conn.commit()
        conn.close()
    
    def load_user_preferences(self):
        """Load user preferences from memory."""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preference_type, preference_value, confidence_score 
            FROM user_preferences 
            WHERE confidence_score > 0.3
        """)
        
        preferences = {}
        for row in cursor.fetchall():
            pref_type, pref_value, confidence = row
            preferences[pref_type] = {
                "value": pref_value,
                "confidence": confidence
            }
        
        conn.close()
        self.response_engine.user_preferences = preferences
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate intelligent response."""
        
        # Extract context from input
        context = self.response_engine.extract_context(user_input)
        
        # Generate intelligent response
        response = self.response_engine.generate_intelligent_response(user_input, context)
        
        # Store conversation with context
        self.store_conversation(user_input, response, context)
        
        # Update user preferences based on interaction
        self.update_preferences(user_input, context)
        
        return response
    
    def store_conversation(self, user_input: str, response: str, context: Dict[str, Any]):
        """Store conversation with full context."""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # Check if context column exists, if not add it
        try:
            cursor.execute("""
                INSERT INTO conversations (user_input, assistant_response, session_id, context)
                VALUES (?, ?, ?, ?)
            """, (user_input, response, self.current_session, json.dumps(context)))
        except sqlite3.OperationalError:
            # Add context column if it doesn't exist
            cursor.execute("ALTER TABLE conversations ADD COLUMN context TEXT")
            cursor.execute("ALTER TABLE conversations ADD COLUMN response_quality_score INTEGER DEFAULT 3")
            cursor.execute("""
                INSERT INTO conversations (user_input, assistant_response, session_id, context)
                VALUES (?, ?, ?, ?)
            """, (user_input, response, self.current_session, json.dumps(context)))
        
        conn.commit()
        conn.close()
    
    def update_preferences(self, user_input: str, context: Dict[str, Any]):
        """Update user preferences based on interaction patterns."""
        
        # Detect communication style preferences
        if len(user_input.split()) < 5:
            self.update_preference("communication_style", "brief", 0.1)
        elif len(user_input.split()) > 20:
            self.update_preference("communication_style", "detailed", 0.1)
        
        # Detect urgency patterns
        if context["urgency"] == "high":
            self.update_preference("default_urgency", "high", 0.05)
        
        # Detect preferred task types
        if context["task_type"] != "general":
            self.update_preference("frequent_task_type", context["task_type"], 0.1)
    
    def update_preference(self, pref_type: str, pref_value: str, confidence_increment: float):
        """Update a user preference with confidence tracking."""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # Check if preference exists
        cursor.execute("""
            SELECT confidence_score FROM user_preferences 
            WHERE preference_type = ? AND preference_value = ?
        """, (pref_type, pref_value))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing preference
            new_confidence = min(1.0, result[0] + confidence_increment)
            cursor.execute("""
                UPDATE user_preferences 
                SET confidence_score = ?, last_updated = CURRENT_TIMESTAMP
                WHERE preference_type = ? AND preference_value = ?
            """, (new_confidence, pref_type, pref_value))
        else:
            # Create new preference
            cursor.execute("""
                INSERT INTO user_preferences (preference_type, preference_value, confidence_score)
                VALUES (?, ?, ?)
            """, (pref_type, pref_value, confidence_increment))
        
        conn.commit()
        conn.close()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learned user preferences and patterns."""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # Get top preferences
        cursor.execute("""
            SELECT preference_type, preference_value, confidence_score
            FROM user_preferences
            ORDER BY confidence_score DESC
            LIMIT 10
        """)
        
        preferences = [
            {"type": row[0], "value": row[1], "confidence": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Get conversation patterns
        cursor.execute("""
            SELECT COUNT(*) as total_conversations,
                   AVG(response_quality_score) as avg_quality
            FROM conversations
            WHERE session_id = ?
        """, (self.current_session,))
        
        session_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "preferences": preferences,
            "session_conversations": session_stats[0] if session_stats else 0,
            "average_quality": session_stats[1] if session_stats else 0
        }

# Test the intelligent brain
def test_intelligent_brain():
    """Test the intelligent brain with various scenarios."""
    
    brain = ARKIntelligentBrain()
    
    test_inputs = [
        "I need to organize a team meeting for next week urgently",
        "Help me plan my career transition to data science",
        "My desktop is cluttered with files, help me organize",
        "I'm feeling overwhelmed with my workload",
        "Schedule a recurring meeting every Tuesday at 2 PM",
        "What's the best way to balance work and personal life?"
    ]
    
    print("=== Testing ARK Intelligent Brain ===\n")
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"Test {i}: {test_input}")
        response = brain.process_input(test_input)
        print(f"ARK: {response}")
        print("-" * 80)
    
    # Show learning insights
    insights = brain.get_learning_insights()
    print("\n=== Learning Insights ===")
    print(f"Session conversations: {insights['session_conversations']}")
    print("Top preferences:")
    for pref in insights['preferences'][:5]:
        print(f"  {pref['type']}: {pref['value']} (confidence: {pref['confidence']:.2f})")

if __name__ == "__main__":
    test_intelligent_brain()