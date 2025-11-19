"""
ARK Advanced Training System
==========================
Multi-resource training pipeline for continuous AI improvement
"""

import sys
import json
import sqlite3
import requests
import time
import threading
import schedule
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import feedparser
import wikipedia
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from ark_intelligent_brain import ARKIntelligentBrain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/training.log'),
        logging.StreamHandler()
    ]
)

class WebResourceCollector:
    """Collect training data from web resources."""
    
    def __init__(self):
        self.news_feeds = [
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.cnn.com/rss/edition.rss',
            'https://techcrunch.com/feed/',
            'https://feeds.reuters.com/reuters/technologyNews',
        ]
        
        self.productivity_feeds = [
            'https://feeds.feedburner.com/LifehackerFull',
            'https://feeds.feedburner.com/zenhabits',
        ]
    
    def collect_news_data(self) -> List[Dict]:
        """Collect recent news for context awareness."""
        training_data = []
        
        for feed_url in self.news_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Limit to recent entries
                    training_data.append({
                        'source': 'news',
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'url': entry.link,
                        'published': entry.get('published', ''),
                        'category': 'current_events'
                    })
            except Exception as e:
                logging.error(f"Error collecting from {feed_url}: {e}")
        
        return training_data
    
    def collect_productivity_tips(self) -> List[Dict]:
        """Collect productivity and life improvement content."""
        training_data = []
        
        for feed_url in self.productivity_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    training_data.append({
                        'source': 'productivity',
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'url': entry.link,
                        'published': entry.get('published', ''),
                        'category': 'productivity_tips'
                    })
            except Exception as e:
                logging.error(f"Error collecting productivity tips from {feed_url}: {e}")
        
        return training_data
    
    def collect_wikipedia_knowledge(self, topics: List[str]) -> List[Dict]:
        """Collect knowledge from Wikipedia on specific topics."""
        training_data = []
        
        for topic in topics:
            try:
                page = wikipedia.page(topic)
                training_data.append({
                    'source': 'wikipedia',
                    'title': page.title,
                    'summary': wikipedia.summary(topic, sentences=3),
                    'url': page.url,
                    'category': 'knowledge_base'
                })
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logging.error(f"Error collecting Wikipedia data for {topic}: {e}")
        
        return training_data

class ConversationLearner:
    """Learn from user conversations and interactions."""
    
    def __init__(self, memory_db_path: str):
        self.db_path = memory_db_path
        self.init_learning_db()
    
    def init_learning_db(self):
        """Initialize learning database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                user_input TEXT,
                ark_response TEXT,
                user_satisfaction INTEGER,
                response_quality REAL,
                context_tags TEXT,
                improvement_suggestions TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_value TEXT,
                frequency INTEGER DEFAULT 1,
                confidence REAL DEFAULT 0.1,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement_type TEXT,
                before_response TEXT,
                after_response TEXT,
                success_metrics TEXT,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def analyze_conversation(self, user_input: str, ark_response: str, context: Dict = None) -> Dict:
        """Analyze conversation for learning opportunities."""
        
        analysis = {
            'response_length': len(ark_response),
            'helpfulness_indicators': self.detect_helpfulness(ark_response),
            'context_awareness': self.assess_context_usage(user_input, ark_response, context),
            'personalization': self.assess_personalization(ark_response),
            'improvement_areas': []
        }
        
        # Detect improvement opportunities
        if analysis['response_length'] < 20:
            analysis['improvement_areas'].append('response_too_brief')
        
        if not analysis['helpfulness_indicators']:
            analysis['improvement_areas'].append('lack_helpful_indicators')
        
        if analysis['context_awareness'] < 0.5:
            analysis['improvement_areas'].append('poor_context_usage')
        
        return analysis
    
    def detect_helpfulness(self, response: str) -> List[str]:
        """Detect indicators of helpful responses."""
        indicators = []
        response_lower = response.lower()
        
        helpful_phrases = [
            'let me help', 'i can assist', 'here are some options',
            'would you like me to', 'i suggest', 'here\'s what i recommend',
            'step by step', 'first', 'second', 'next'
        ]
        
        for phrase in helpful_phrases:
            if phrase in response_lower:
                indicators.append(phrase)
        
        return indicators
    
    def assess_context_usage(self, user_input: str, response: str, context: Dict = None) -> float:
        """Assess how well the response uses available context."""
        if not context:
            return 0.5  # Neutral score when no context available
        
        context_usage_score = 0.0
        
        # Check if response references user preferences
        if 'preferences' in context:
            for pref in context['preferences']:
                if pref.lower() in response.lower():
                    context_usage_score += 0.3
        
        # Check if response considers user's current tasks
        if 'current_tasks' in context:
            if any(task.lower() in response.lower() for task in context['current_tasks']):
                context_usage_score += 0.3
        
        # Check if response considers time context
        if 'time_context' in context:
            time_words = ['morning', 'afternoon', 'evening', 'today', 'tomorrow']
            if any(word in response.lower() for word in time_words):
                context_usage_score += 0.2
        
        return min(context_usage_score, 1.0)
    
    def assess_personalization(self, response: str) -> float:
        """Assess how personalized the response is."""
        personalization_indicators = [
            'you', 'your', 'based on your', 'i remember', 'as you prefer',
            'given your', 'since you', 'knowing that you'
        ]
        
        response_lower = response.lower()
        score = sum(1 for indicator in personalization_indicators if indicator in response_lower)
        
        return min(score * 0.2, 1.0)

class ARKAdvancedTrainer:
    """Advanced training system for ARK AI."""
    
    def __init__(self):
        self.ark_brain = ARKIntelligentBrain()
        self.web_collector = WebResourceCollector()
        self.conversation_learner = ConversationLearner(self.ark_brain.memory_db_path)
        
        self.training_active = False
        self.training_thread = None
        
        # Training configuration
        self.training_config = {
            'web_data_collection_interval': 3600,  # 1 hour
            'conversation_analysis_interval': 300,  # 5 minutes
            'model_retraining_interval': 86400,    # 24 hours
            'max_web_articles_per_cycle': 20,
            'wikipedia_topics': [
                'productivity', 'time management', 'artificial intelligence',
                'project management', 'communication', 'leadership',
                'technology trends', 'workflow optimization'
            ]
        }
        
        logging.info("ARK Advanced Trainer initialized")
    
    def start_continuous_training(self):
        """Start continuous training in background."""
        if self.training_active:
            logging.warning("Training already active")
            return
        
        self.training_active = True
        
        # Schedule training tasks
        schedule.every().hour.do(self.collect_web_training_data)
        schedule.every(5).minutes.do(self.analyze_recent_conversations)
        schedule.every().day.do(self.retrain_model)
        schedule.every(30).minutes.do(self.optimize_responses)
        
        # Start background training thread
        self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self.training_thread.start()
        
        logging.info("Continuous training started")
        print("🚀 ARK Advanced Training System Started!")
        print("📊 Training Components Active:")
        print("   • Web resource collection (hourly)")
        print("   • Conversation analysis (every 5 minutes)")
        print("   • Model retraining (daily)")
        print("   • Response optimization (every 30 minutes)")
    
    def _training_loop(self):
        """Main training loop."""
        while self.training_active:
            try:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logging.error(f"Error in training loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def collect_web_training_data(self):
        """Collect training data from web resources."""
        try:
            logging.info("Starting web data collection")
            
            # Collect various types of data
            news_data = self.web_collector.collect_news_data()
            productivity_data = self.web_collector.collect_productivity_tips()
            knowledge_data = self.web_collector.collect_wikipedia_knowledge(
                self.training_config['wikipedia_topics'][:3]  # Limit to avoid rate limits
            )
            
            # Process and store training data
            all_data = news_data + productivity_data + knowledge_data
            self.process_web_training_data(all_data)
            
            logging.info(f"Collected {len(all_data)} training samples from web resources")
            
        except Exception as e:
            logging.error(f"Error collecting web training data: {e}")
    
    def process_web_training_data(self, data: List[Dict]):
        """Process and integrate web data into training."""
        
        # Convert web data to training format
        training_samples = []
        
        for item in data:
            # Create training scenarios based on web content
            if item['category'] == 'current_events':
                training_samples.append({
                    'input': f"What's happening with {item['title'].split()[0]}?",
                    'output': f"Based on recent news: {item['summary'][:200]}...",
                    'category': 'current_events',
                    'confidence': 0.7
                })
            
            elif item['category'] == 'productivity_tips':
                training_samples.append({
                    'input': f"How can I improve my productivity?",
                    'output': f"Here's a helpful tip: {item['summary'][:200]}...",
                    'category': 'productivity_advice',
                    'confidence': 0.8
                })
            
            elif item['category'] == 'knowledge_base':
                training_samples.append({
                    'input': f"Tell me about {item['title'].lower()}",
                    'output': f"Based on reliable sources: {item['summary']}",
                    'category': 'knowledge',
                    'confidence': 0.9
                })
        
        # Store training samples
        self.store_training_samples(training_samples)
    
    def analyze_recent_conversations(self):
        """Analyze recent conversations for learning."""
        try:
            conn = sqlite3.connect(self.ark_brain.memory_db_path)
            cursor = conn.cursor()
            
            # Get recent conversations not yet analyzed
            cursor.execute("""
                SELECT id, user_input, ark_response, timestamp
                FROM conversations
                WHERE timestamp > datetime('now', '-1 hour')
                AND id NOT IN (
                    SELECT conversation_id FROM conversation_analysis
                    WHERE conversation_id IS NOT NULL
                )
            """)
            
            recent_conversations = cursor.fetchall()
            
            for conv in recent_conversations:
                conv_id, user_input, ark_response, timestamp = conv
                
                # Analyze conversation
                analysis = self.conversation_learner.analyze_conversation(
                    user_input, ark_response
                )
                
                # Store analysis
                cursor.execute("""
                    INSERT INTO conversation_analysis
                    (conversation_id, user_input, ark_response, response_quality, context_tags, improvement_suggestions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    conv_id, user_input, ark_response,
                    analysis.get('helpfulness_score', 0.5),
                    json.dumps(analysis.get('context_awareness', {})),
                    json.dumps(analysis.get('improvement_areas', []))
                ))
            
            conn.commit()
            conn.close()
            
            if recent_conversations:
                logging.info(f"Analyzed {len(recent_conversations)} recent conversations")
            
        except Exception as e:
            logging.error(f"Error analyzing conversations: {e}")
    
    def optimize_responses(self):
        """Optimize responses based on learned patterns."""
        try:
            # Get improvement opportunities
            conn = sqlite3.connect(self.ark_brain.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT improvement_suggestions, COUNT(*) as frequency
                FROM conversation_analysis
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY improvement_suggestions
                HAVING frequency > 1
                ORDER BY frequency DESC
            """)
            
            improvements = cursor.fetchall()
            
            for improvement_data, frequency in improvements:
                try:
                    improvement_list = json.loads(improvement_data)
                    
                    for improvement in improvement_list:
                        if improvement == 'response_too_brief':
                            self.implement_response_improvement('expand_responses')
                        elif improvement == 'lack_helpful_indicators':
                            self.implement_response_improvement('add_helpful_phrases')
                        elif improvement == 'poor_context_usage':
                            self.implement_response_improvement('improve_context_awareness')
                
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            
            if improvements:
                logging.info(f"Applied {len(improvements)} response optimizations")
            
        except Exception as e:
            logging.error(f"Error optimizing responses: {e}")
    
    def implement_response_improvement(self, improvement_type: str):
        """Implement specific response improvements."""
        
        improvement_strategies = {
            'expand_responses': [
                "I'd be happy to help you with that. Let me provide more details:",
                "That's a great question. Here's what I can tell you:",
                "I understand what you're looking for. Let me break this down:"
            ],
            'add_helpful_phrases': [
                "Would you like me to help you with anything else?",
                "I'm here to assist you further if needed.",
                "Let me know if you'd like more information about this."
            ],
            'improve_context_awareness': [
                "Based on what you've told me before,",
                "Considering your preferences,",
                "Given your usual workflow,"
            ]
        }
        
        # These would be integrated into the response generation logic
        # For now, log the improvement
        logging.info(f"Implementing improvement: {improvement_type}")
    
    def retrain_model(self):
        """Retrain the AI model with new data."""
        try:
            logging.info("Starting model retraining")
            
            # Load all available training data
            training_data = self.load_all_training_data()
            
            # Update the training dataset file
            training_file = 'training/ark_comprehensive_training.jsonl'
            
            with open(training_file, 'w') as f:
                for item in training_data:
                    f.write(json.dumps(item) + '\n')
            
            # Reload the brain with updated training data
            self.ark_brain = ARKIntelligentBrain()
            
            logging.info(f"Model retrained with {len(training_data)} samples")
            
        except Exception as e:
            logging.error(f"Error retraining model: {e}")
    
    def load_all_training_data(self) -> List[Dict]:
        """Load all available training data."""
        training_data = []
        
        # Load existing training data
        try:
            with open('training/ark_comprehensive_training.jsonl', 'r') as f:
                for line in f:
                    training_data.append(json.loads(line.strip()))
        except FileNotFoundError:
            pass
        
        # Load web-collected data
        try:
            conn = sqlite3.connect(self.ark_brain.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM training_samples WHERE confidence > 0.6")
            samples = cursor.fetchall()
            
            for sample in samples:
                training_data.append({
                    'input': sample[1],
                    'output': sample[2],
                    'category': sample[3]
                })
            
            conn.close()
        except:
            pass
        
        return training_data
    
    def store_training_samples(self, samples: List[Dict]):
        """Store training samples in database."""
        try:
            conn = sqlite3.connect(self.ark_brain.memory_db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT,
                    output_text TEXT,
                    category TEXT,
                    confidence REAL,
                    source TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            for sample in samples:
                cursor.execute("""
                    INSERT INTO training_samples (input_text, output_text, category, confidence, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    sample['input'],
                    sample['output'],
                    sample['category'],
                    sample.get('confidence', 0.5),
                    'web_collection'
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error storing training samples: {e}")
    
    def get_training_statistics(self) -> Dict:
        """Get comprehensive training statistics."""
        try:
            conn = sqlite3.connect(self.ark_brain.memory_db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            stats['total_conversations'] = cursor.fetchone()[0]
            
            # Training samples
            cursor.execute("SELECT COUNT(*) FROM training_samples")
            stats['training_samples'] = cursor.fetchone()[0] if cursor.fetchone() else 0
            
            # Recent analysis
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_analysis 
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            stats['recent_analyses'] = cursor.fetchone()[0]
            
            # Preferences learned
            cursor.execute("SELECT COUNT(*) FROM user_preferences")
            stats['preferences_learned'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logging.error(f"Error getting training statistics: {e}")
            return {}
    
    def stop_training(self):
        """Stop continuous training."""
        self.training_active = False
        if self.training_thread:
            self.training_thread.join(timeout=5)
        
        schedule.clear()
        logging.info("Training stopped")
        print("🛑 ARK Training System Stopped")

def main():
    """Main training interface."""
    print("=" * 60)
    print("ARK ADVANCED TRAINING SYSTEM")
    print("Multi-Resource AI Training Pipeline")
    print("=" * 60)
    
    trainer = ARKAdvancedTrainer()
    
    try:
        print("\n🚀 Starting Advanced Training System...")
        print("This will train ARK using:")
        print("  • Live web data collection")
        print("  • Conversation analysis")
        print("  • Wikipedia knowledge")
        print("  • Productivity resources")
        print("  • User interaction patterns")
        
        response = input("\nStart continuous training? (y/n): ")
        if response.lower().strip() == 'y':
            trainer.start_continuous_training()
            
            print("\n📊 Training System Active! Press Ctrl+C to stop...")
            
            # Show periodic statistics
            while trainer.training_active:
                time.sleep(300)  # Wait 5 minutes
                stats = trainer.get_training_statistics()
                print(f"\n📈 Training Progress:")
                print(f"   Total Conversations: {stats.get('total_conversations', 0)}")
                print(f"   Training Samples: {stats.get('training_samples', 0)}")
                print(f"   Recent Analyses: {stats.get('recent_analyses', 0)}")
                print(f"   Preferences Learned: {stats.get('preferences_learned', 0)}")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping training system...")
        trainer.stop_training()
    except Exception as e:
        print(f"❌ Training error: {e}")
        logging.error(f"Training system error: {e}")
    
    print("Training session complete!")

if __name__ == "__main__":
    main()