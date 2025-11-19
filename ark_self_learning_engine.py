"""
ARK Self-Learning Engine
========================
Continuous learning system that automatically improves ARK's capabilities
through conversation analysis, feedback processing, and adaptive training.
"""

import json
import sqlite3
import os
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import re
import hashlib

class SelfLearningEngine:
    """Advanced self-learning system for continuous ARK improvement."""
    
    def __init__(self, db_path: str = "data/ark_complete_training.db"):
        self.db_path = db_path
        self.conversation_log_path = "data/conversation_history.json"
        self.learning_stats_path = "data/learning_statistics.json"
        self.feedback_path = "data/user_feedback.json"
        
        # Learning parameters
        self.min_confidence_score = 0.7
        self.learning_threshold = 3  # Minimum occurrences to create new training
        self.quality_threshold = 0.8
        
        # Conversation analysis
        self.conversation_buffer = []
        self.feedback_buffer = []
        self.learning_metrics = defaultdict(int)
        
        # Initialize databases and files
        self.init_learning_infrastructure()
        
        # Start background learning thread
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._continuous_learning_loop, daemon=True)
        self.learning_thread.start()
        
        logging.info("ARK Self-Learning Engine initialized")
    
    def init_learning_infrastructure(self):
        """Initialize all learning databases and files."""
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize conversation history file
        if not os.path.exists(self.conversation_log_path):
            with open(self.conversation_log_path, 'w') as f:
                json.dump([], f)
        
        # Initialize feedback file
        if not os.path.exists(self.feedback_path):
            with open(self.feedback_path, 'w') as f:
                json.dump([], f)
        
        # Initialize learning statistics
        if not os.path.exists(self.learning_stats_path):
            initial_stats = {
                "learning_sessions": 0,
                "new_patterns_learned": 0,
                "training_examples_added": 0,
                "last_learning_time": datetime.now().isoformat(),
                "capability_improvements": []
            }
            with open(self.learning_stats_path, 'w') as f:
                json.dump(initial_stats, f, indent=2)
        
        # Initialize enhanced learning tables in database
        self._setup_learning_tables()
    
    def _setup_learning_tables(self):
        """Setup advanced learning tables in the database."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT UNIQUE,
                input_pattern TEXT,
                context_keywords TEXT,
                successful_responses INTEGER DEFAULT 0,
                failed_responses INTEGER DEFAULT 0,
                confidence_score REAL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                learned_from_conversations INTEGER DEFAULT 0
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                user_input TEXT,
                ark_response TEXT,
                feedback_type TEXT, -- positive, negative, suggestion
                feedback_details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Learning insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT, -- pattern, gap, improvement
                description TEXT,
                confidence REAL,
                supporting_evidence TEXT,
                action_taken TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT, -- response_quality, relevance, user_satisfaction
                category TEXT,
                value REAL,
                date_measured DATE,
                context TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_conversation(self, user_input: str, ark_response: str, context: Dict = None):
        """Log conversation for learning analysis."""
        
        conversation_id = hashlib.md5(f"{user_input}{datetime.now().isoformat()}".encode()).hexdigest()
        
        conversation_entry = {
            "id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ark_response": ark_response,
            "context": context or {},
            "response_length": len(ark_response),
            "keywords": self._extract_keywords(user_input),
            "category": self._categorize_input(user_input)
        }
        
        # Add to buffer for processing
        self.conversation_buffer.append(conversation_entry)
        
        # Also append to conversation history file
        try:
            with open(self.conversation_log_path, 'r') as f:
                conversations = json.load(f)
            
            conversations.append(conversation_entry)
            
            # Keep only last 1000 conversations in file
            if len(conversations) > 1000:
                conversations = conversations[-1000:]
            
            with open(self.conversation_log_path, 'w') as f:
                json.dump(conversations, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving conversation: {e}")
    
    def process_user_feedback(self, feedback_type: str, details: str, conversation_id: str = None):
        """Process user feedback for learning."""
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "feedback_type": feedback_type,  # positive, negative, suggestion, correction
            "details": details,
            "conversation_id": conversation_id,
            "processed": False
        }
        
        self.feedback_buffer.append(feedback_entry)
        
        # Save to feedback file
        try:
            with open(self.feedback_path, 'r') as f:
                feedback_data = json.load(f)
            
            feedback_data.append(feedback_entry)
            
            with open(self.feedback_path, 'w') as f:
                json.dump(feedback_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving feedback: {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        
        # Common stop words to ignore
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        return list(set(keywords))  # Remove duplicates
    
    def _categorize_input(self, user_input: str) -> str:
        """Automatically categorize user input."""
        
        input_lower = user_input.lower()
        
        # Category patterns
        categories = {
            "academic": ["study", "exam", "homework", "learn", "understand", "concept", "research", "education"],
            "task_management": ["create", "make", "schedule", "plan", "organize", "manage", "task", "todo"],
            "information": ["what", "how", "why", "when", "where", "tell", "explain", "information"],
            "emotional_support": ["feel", "sad", "happy", "stressed", "anxious", "help", "support", "comfort"],
            "creative": ["write", "create", "design", "idea", "creative", "art", "story", "poem"],
            "technical": ["code", "program", "script", "function", "debug", "error", "software"],
            "communication": ["email", "message", "send", "contact", "call", "text", "communication"],
            "analysis": ["analyze", "compare", "evaluate", "assess", "review", "examine"]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in input_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return highest scoring category or "general"
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return "general"
    
    def _continuous_learning_loop(self):
        """Background thread for continuous learning."""
        
        learning_interval = 300  # Learn every 5 minutes
        
        while self.learning_active:
            try:
                time.sleep(learning_interval)
                
                if self.conversation_buffer or self.feedback_buffer:
                    self._perform_learning_cycle()
                    
            except Exception as e:
                logging.error(f"Learning loop error: {e}")
    
    def _perform_learning_cycle(self):
        """Perform a complete learning cycle."""
        
        print(f"\n🧠 LEARNING CYCLE STARTED - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # Analyze conversation patterns
        new_patterns = self._analyze_conversation_patterns()
        
        # Process feedback
        feedback_insights = self._process_feedback()
        
        # Identify knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps()
        
        # Generate new training data
        new_training = self._generate_training_data(new_patterns, feedback_insights, knowledge_gaps)
        
        # Update performance metrics
        self._update_performance_metrics()
        
        # Clear buffers
        self.conversation_buffer.clear()
        self.feedback_buffer.clear()
        
        # Update learning statistics
        self._update_learning_stats(new_patterns, new_training)
        
        print(f"✅ Learning cycle complete: {len(new_training)} new examples added")
    
    def _analyze_conversation_patterns(self) -> List[Dict]:
        """Analyze conversation patterns to identify learning opportunities."""
        
        patterns = []
        
        # Group conversations by category
        category_groups = defaultdict(list)
        for conv in self.conversation_buffer:
            category_groups[conv['category']].append(conv)
        
        for category, conversations in category_groups.items():
            if len(conversations) >= self.learning_threshold:
                
                # Analyze common patterns in this category
                common_keywords = defaultdict(int)
                successful_responses = []
                
                for conv in conversations:
                    for keyword in conv['keywords']:
                        common_keywords[keyword] += 1
                    
                    if len(conv['ark_response']) > 100:  # Assume longer responses are better
                        successful_responses.append(conv)
                
                if successful_responses:
                    pattern = {
                        "category": category,
                        "common_keywords": [kw for kw, count in common_keywords.items() if count >= 2],
                        "example_conversations": successful_responses[:3],
                        "frequency": len(conversations),
                        "confidence": min(len(successful_responses) / len(conversations), 1.0)
                    }
                    patterns.append(pattern)
        
        return patterns
    
    def _process_feedback(self) -> List[Dict]:
        """Process user feedback for learning insights."""
        
        insights = []
        
        # Analyze feedback by type
        feedback_by_type = defaultdict(list)
        for feedback in self.feedback_buffer:
            feedback_by_type[feedback['feedback_type']].append(feedback)
        
        # Process negative feedback for improvement areas
        if feedback_by_type['negative']:
            for feedback in feedback_by_type['negative']:
                insight = {
                    "type": "improvement_needed",
                    "area": "response_quality",
                    "details": feedback['details'],
                    "confidence": 0.8
                }
                insights.append(insight)
        
        # Process suggestions for new capabilities
        if feedback_by_type['suggestion']:
            for feedback in feedback_by_type['suggestion']:
                insight = {
                    "type": "new_capability",
                    "area": "feature_request",
                    "details": feedback['details'],
                    "confidence": 0.7
                }
                insights.append(insight)
        
        return insights
    
    def _identify_knowledge_gaps(self) -> List[Dict]:
        """Identify areas where ARK needs more training."""
        
        gaps = []
        
        # Analyze conversation categories with short responses
        category_performance = defaultdict(list)
        
        for conv in self.conversation_buffer:
            category_performance[conv['category']].append(len(conv['ark_response']))
        
        for category, response_lengths in category_performance.items():
            avg_length = sum(response_lengths) / len(response_lengths)
            
            # If average response length is too short, it's a gap
            if avg_length < 200:
                gap = {
                    "category": category,
                    "issue": "short_responses",
                    "avg_response_length": avg_length,
                    "sample_count": len(response_lengths),
                    "severity": "high" if avg_length < 100 else "medium"
                }
                gaps.append(gap)
        
        return gaps
    
    def _generate_training_data(self, patterns: List[Dict], insights: List[Dict], gaps: List[Dict]) -> List[Dict]:
        """Generate new training data based on learning analysis."""
        
        new_training = []
        
        # Generate training from successful patterns
        for pattern in patterns:
            if pattern['confidence'] >= self.min_confidence_score:
                
                example_conv = pattern['example_conversations'][0]
                
                new_example = {
                    "category": pattern['category'],
                    "input_text": example_conv['user_input'],
                    "output_text": example_conv['ark_response'],
                    "quality_score": pattern['confidence'],
                    "learned_from": "conversation_analysis",
                    "keywords": pattern['common_keywords']
                }
                new_training.append(new_example)
        
        # Generate training to address gaps
        for gap in gaps:
            if gap['severity'] == 'high':
                # Create enhanced training for this category
                enhanced_example = self._create_gap_training(gap)
                if enhanced_example:
                    new_training.append(enhanced_example)
        
        # Save new training to database
        if new_training:
            self._save_training_data(new_training)
        
        return new_training
    
    def _create_gap_training(self, gap: Dict) -> Optional[Dict]:
        """Create training data to address knowledge gaps."""
        
        # Gap-specific training templates
        gap_templates = {
            "academic": {
                "input": "help me with advanced {topic} concepts",
                "output": """🎓 **Advanced {topic} Learning Support**

**COMPREHENSIVE APPROACH:**

**Foundation Review:**
• Core principles and fundamentals
• Key terminology and definitions  
• Essential theories and frameworks

**Advanced Concepts:**
• Complex applications and scenarios
• Integration with other topics
• Real-world problem solving

**STUDY STRATEGIES:**
✓ Break complex topics into manageable parts
✓ Use multiple learning resources and perspectives
✓ Practice with challenging examples
✓ Connect new concepts to existing knowledge

**SUPPORT RESOURCES:**
• Academic textbooks and journals
• Online courses and tutorials
• Study groups and discussions
• Professional guidance when needed

What specific {topic} concepts would you like to explore in detail?"""
            },
            "task_management": {
                "input": "help me organize my {task_type} more effectively",
                "output": """📋 **Advanced {task_type} Organization**

**STRATEGIC PLANNING:**

**Assessment Phase:**
• Analyze current {task_type} workflow
• Identify bottlenecks and inefficiencies
• Set clear goals and priorities

**Organization System:**
• Categorize by importance and urgency
• Create structured timelines
• Implement tracking mechanisms

**OPTIMIZATION TECHNIQUES:**
✓ Time-blocking for focused work
✓ Batch similar tasks together
✓ Automate repetitive processes
✓ Regular review and adjustment

**PRODUCTIVITY TOOLS:**
• Digital task managers and calendars
• Project management platforms
• Collaboration tools for team work
• Progress tracking and analytics

**MAINTENANCE:**
• Weekly planning sessions
• Daily priority reviews
• Monthly system evaluations
• Continuous improvement mindset

What specific aspects of your {task_type} need the most attention?"""
            }
        }
        
        category = gap['category']
        if category in gap_templates:
            template = gap_templates[category]
            
            return {
                "category": f"enhanced_{category}",
                "input_text": template['input'].format(topic="studies", task_type="projects"),
                "output_text": template['output'].format(topic="Studies", task_type="Projects"),
                "quality_score": 0.85,
                "learned_from": "gap_analysis",
                "addresses_gap": gap['issue']
            }
        
        return None
    
    def _save_training_data(self, training_examples: List[Dict]):
        """Save new training data to the database."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for example in training_examples:
            cursor.execute("""
                INSERT OR REPLACE INTO training_data 
                (category, input_text, output_text, quality_score)
                VALUES (?, ?, ?, ?)
            """, (
                example['category'],
                example['input_text'],
                example['output_text'],
                example['quality_score']
            ))
        
        conn.commit()
        conn.close()
    
    def _update_performance_metrics(self):
        """Update performance metrics based on recent conversations."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate metrics from conversation buffer
        if self.conversation_buffer:
            avg_response_length = sum(len(conv['ark_response']) for conv in self.conversation_buffer) / len(self.conversation_buffer)
            
            # Response quality metric
            cursor.execute("""
                INSERT INTO performance_metrics (metric_type, category, value, date_measured, context)
                VALUES (?, ?, ?, ?, ?)
            """, ("response_length", "overall", avg_response_length, datetime.now().date().isoformat(), f"{len(self.conversation_buffer)} conversations"))
            
            # Category performance
            category_stats = defaultdict(list)
            for conv in self.conversation_buffer:
                category_stats[conv['category']].append(len(conv['ark_response']))
            
            for category, lengths in category_stats.items():
                avg_length = sum(lengths) / len(lengths)
                cursor.execute("""
                    INSERT INTO performance_metrics (metric_type, category, value, date_measured, context)
                    VALUES (?, ?, ?, ?, ?)
                """, ("category_performance", category, avg_length, datetime.now().date().isoformat(), f"{len(lengths)} responses"))
        
        conn.commit()
        conn.close()
    
    def _update_learning_stats(self, new_patterns: List[Dict], new_training: List[Dict]):
        """Update learning statistics."""
        
        try:
            with open(self.learning_stats_path, 'r') as f:
                stats = json.load(f)
            
            stats['learning_sessions'] += 1
            stats['new_patterns_learned'] += len(new_patterns)
            stats['training_examples_added'] += len(new_training)
            stats['last_learning_time'] = datetime.now().isoformat()
            
            # Add capability improvements
            for pattern in new_patterns:
                improvement = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "pattern_learning",
                    "category": pattern['category'],
                    "confidence": pattern['confidence']
                }
                stats['capability_improvements'].append(improvement)
            
            with open(self.learning_stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error updating learning stats: {e}")
    
    def get_learning_status(self) -> Dict:
        """Get current learning status and statistics."""
        
        try:
            with open(self.learning_stats_path, 'r') as f:
                stats = json.load(f)
            
            # Add current metrics
            stats['conversation_buffer_size'] = len(self.conversation_buffer)
            stats['feedback_buffer_size'] = len(self.feedback_buffer)
            stats['learning_active'] = self.learning_active
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting learning status: {e}")
            return {"error": str(e)}
    
    def force_learning_cycle(self):
        """Manually trigger a learning cycle."""
        
        if self.conversation_buffer or self.feedback_buffer:
            print("🔄 Forcing learning cycle...")
            self._perform_learning_cycle()
        else:
            print("⚠️  No data available for learning cycle")
    
    def stop_learning(self):
        """Stop the continuous learning system."""
        
        self.learning_active = False
        print("🛑 Self-learning system stopped")


class ARKSelfLearningBot:
    """Enhanced ARK with self-learning capabilities."""
    
    def __init__(self):
        # Import ARK brain
        try:
            from ark_intelligent_brain import ARKIntelligentBrain
            self.brain = ARKIntelligentBrain()
        except ImportError:
            print("❌ Could not import ARK brain")
            self.brain = None
        
        # Initialize learning engine
        self.learning_engine = SelfLearningEngine()
        print("🧠 ARK Self-Learning Bot initialized")
    
    def process_input_with_learning(self, user_input: str) -> str:
        """Process input and log for learning."""
        
        if not self.brain:
            return "❌ ARK brain not available"
        
        # Get response from ARK
        response = self.brain.process_input(user_input)
        
        # Log conversation for learning
        self.learning_engine.log_conversation(user_input, response)
        
        return response
    
    def provide_feedback(self, feedback_type: str, details: str):
        """Provide feedback for learning."""
        
        self.learning_engine.process_user_feedback(feedback_type, details)
        print(f"✅ Feedback recorded: {feedback_type}")
    
    def get_learning_status(self):
        """Get learning status."""
        
        return self.learning_engine.get_learning_status()
    
    def force_learning(self):
        """Force a learning cycle."""
        
        self.learning_engine.force_learning_cycle()


def main():
    """Demo of the self-learning system."""
    
    print("🚀 ARK SELF-LEARNING SYSTEM DEMO")
    print("=" * 40)
    
    # Initialize self-learning ARK
    ark = ARKSelfLearningBot()
    
    # Simulate some conversations for learning
    test_conversations = [
        "create a study plan for my physics exam",
        "help me organize my daily tasks",
        "explain quantum mechanics concepts",
        "what are good time management techniques",
        "I need help with my research project"
    ]
    
    print("\n🎯 Simulating conversations for learning...")
    
    for i, question in enumerate(test_conversations, 1):
        print(f"\n{i}. User: {question}")
        response = ark.process_input_with_learning(question)
        print(f"ARK: {response[:100]}...")
    
    # Simulate some feedback
    print(f"\n📝 Adding user feedback...")
    ark.provide_feedback("positive", "Great study plan, very detailed!")
    ark.provide_feedback("suggestion", "Could you add more examples for time management?")
    ark.provide_feedback("negative", "The explanation was too technical")
    
    # Check learning status
    print(f"\n📊 Learning Status:")
    status = ark.get_learning_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Force learning cycle
    print(f"\n🔄 Forcing learning cycle...")
    ark.force_learning()
    
    print(f"\n🎉 Self-learning demo complete!")

if __name__ == "__main__":
    main()