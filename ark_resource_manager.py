"""
ARK Resource Manager - External API Integration
=============================================
Connect ARK to external APIs and knowledge sources for enhanced training
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class ExternalAPIManager:
    """Manage connections to external APIs for training data."""
    
    def __init__(self):
        self.api_keys = self.load_api_keys()
        self.rate_limits = {
            'openai': {'calls_per_minute': 60, 'last_call': 0},
            'google': {'calls_per_minute': 100, 'last_call': 0},
            'wikipedia': {'calls_per_minute': 200, 'last_call': 0}
        }
    
    def load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment or config file."""
        api_keys = {}
        
        # Try to load from environment variables
        api_keys['openai'] = os.getenv('OPENAI_API_KEY', '')
        api_keys['google'] = os.getenv('GOOGLE_API_KEY', '')
        api_keys['newsapi'] = os.getenv('NEWSAPI_KEY', '')
        
        # Try to load from config file
        try:
            with open('config/api_keys.json', 'r') as f:
                file_keys = json.load(f)
                api_keys.update(file_keys)
        except FileNotFoundError:
            logging.warning("No API keys config file found. Some features may be limited.")
        
        return api_keys
    
    def respect_rate_limit(self, service: str):
        """Ensure we respect API rate limits."""
        if service in self.rate_limits:
            limit_info = self.rate_limits[service]
            time_since_last = time.time() - limit_info['last_call']
            min_interval = 60.0 / limit_info['calls_per_minute']
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                time.sleep(sleep_time)
            
            self.rate_limits[service]['last_call'] = time.time()
    
    def get_news_data(self, query: str = "artificial intelligence", count: int = 10) -> List[Dict]:
        """Get current news data for training context awareness."""
        if not self.api_keys.get('newsapi'):
            return self.fallback_news_collection(query, count)
        
        self.respect_rate_limit('newsapi')
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'pageSize': count,
                'language': 'en',
                'apiKey': self.api_keys['newsapi']
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'category': 'current_news'
                })
            
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching news data: {e}")
            return self.fallback_news_collection(query, count)
    
    def fallback_news_collection(self, query: str, count: int) -> List[Dict]:
        """Fallback news collection using free sources."""
        # Use RSS feeds as fallback
        import feedparser
        
        feeds = [
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.cnn.com/rss/edition.rss'
        ]
        
        articles = []
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:count//len(feeds)]:
                    articles.append({
                        'title': entry.title,
                        'description': entry.get('summary', ''),
                        'content': entry.get('summary', ''),
                        'url': entry.link,
                        'published_at': entry.get('published', ''),
                        'source': feed.feed.get('title', ''),
                        'category': 'current_news'
                    })
            except Exception as e:
                logging.error(f"Error with fallback news from {feed_url}: {e}")
        
        return articles[:count]
    
    def get_knowledge_base_data(self, topics: List[str]) -> List[Dict]:
        """Get knowledge base data from multiple sources."""
        knowledge_data = []
        
        # Wikipedia data
        knowledge_data.extend(self.get_wikipedia_data(topics))
        
        # Additional knowledge sources could be added here
        
        return knowledge_data
    
    def get_wikipedia_data(self, topics: List[str]) -> List[Dict]:
        """Get structured data from Wikipedia."""
        import wikipedia
        
        data = []
        
        for topic in topics:
            self.respect_rate_limit('wikipedia')
            
            try:
                # Search for the topic
                search_results = wikipedia.search(topic, results=1)
                if not search_results:
                    continue
                
                page_title = search_results[0]
                page = wikipedia.page(page_title)
                
                # Get summary
                summary = wikipedia.summary(page_title, sentences=3)
                
                data.append({
                    'title': page.title,
                    'summary': summary,
                    'content': page.content[:1000],  # Limit content length
                    'url': page.url,
                    'categories': getattr(page, 'categories', [])[:5],
                    'category': 'knowledge_base'
                })
                
            except Exception as e:
                logging.error(f"Error getting Wikipedia data for {topic}: {e}")
                continue
        
        return data
    
    def get_productivity_insights(self) -> List[Dict]:
        """Get productivity tips and insights from various sources."""
        insights = []
        
        # Productivity RSS feeds
        productivity_feeds = [
            'https://feeds.feedburner.com/LifehackerFull',
            'https://feeds.feedburner.com/zenhabits'
        ]
        
        import feedparser
        
        for feed_url in productivity_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    insights.append({
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'url': entry.link,
                        'published_at': entry.get('published', ''),
                        'category': 'productivity_tips'
                    })
            except Exception as e:
                logging.error(f"Error getting productivity insights from {feed_url}: {e}")
        
        return insights

class TrainingDataAugmenter:
    """Augment and improve existing training data."""
    
    def __init__(self):
        self.api_manager = ExternalAPIManager()
    
    def augment_conversations(self, conversations: List[Dict]) -> List[Dict]:
        """Augment conversation data with additional context and variations."""
        augmented = []
        
        for conv in conversations:
            # Original conversation
            augmented.append(conv)
            
            # Create variations
            variations = self.create_conversation_variations(conv)
            augmented.extend(variations)
        
        return augmented
    
    def create_conversation_variations(self, conversation: Dict) -> List[Dict]:
        """Create variations of a conversation for more robust training."""
        variations = []
        
        input_text = conversation.get('input', '')
        output_text = conversation.get('output', '')
        
        # Variation 1: More formal version
        formal_input = self.make_more_formal(input_text)
        if formal_input != input_text:
            variations.append({
                'input': formal_input,
                'output': output_text,
                'category': conversation.get('category', 'general') + '_formal',
                'variation_type': 'formal'
            })
        
        # Variation 2: More casual version
        casual_input = self.make_more_casual(input_text)
        if casual_input != input_text:
            variations.append({
                'input': casual_input,
                'output': output_text,
                'category': conversation.get('category', 'general') + '_casual',
                'variation_type': 'casual'
            })
        
        # Variation 3: Question format
        question_input = self.convert_to_question(input_text)
        if question_input != input_text:
            variations.append({
                'input': question_input,
                'output': output_text,
                'category': conversation.get('category', 'general') + '_question',
                'variation_type': 'question'
            })
        
        return variations
    
    def make_more_formal(self, text: str) -> str:
        """Convert text to more formal version."""
        replacements = {
            "can you": "could you please",
            "wanna": "want to",
            "gonna": "going to",
            "hey": "hello",
            "hi": "hello",
            "thanks": "thank you",
            "ok": "okay"
        }
        
        formal_text = text
        for informal, formal in replacements.items():
            formal_text = formal_text.replace(informal, formal)
        
        return formal_text
    
    def make_more_casual(self, text: str) -> str:
        """Convert text to more casual version."""
        replacements = {
            "could you please": "can you",
            "would you": "can you",
            "hello": "hey",
            "thank you": "thanks",
            "assistance": "help"
        }
        
        casual_text = text
        for formal, casual in replacements.items():
            casual_text = casual_text.replace(formal, casual)
        
        return casual_text
    
    def convert_to_question(self, text: str) -> str:
        """Convert statement to question format."""
        if text.endswith('?'):
            return text
        
        question_starters = [
            "how can I", "what should I", "can you help me", "is it possible to"
        ]
        
        # Try to convert to question
        for starter in question_starters:
            if starter.lower() in text.lower():
                return text + "?"
        
        # If no natural question conversion, add "how do I" prefix
        return f"How do I {text.lower()}?"

class SmartTrainingScheduler:
    """Intelligent scheduling for training tasks."""
    
    def __init__(self):
        self.training_history = []
        self.performance_metrics = {}
    
    def schedule_optimal_training(self, user_activity_pattern: Dict) -> Dict:
        """Schedule training during optimal times based on user patterns."""
        
        # Analyze user activity to find low-usage periods
        low_usage_hours = self.find_low_usage_periods(user_activity_pattern)
        
        schedule = {
            'data_collection': low_usage_hours[0] if low_usage_hours else 3,  # 3 AM default
            'model_retraining': low_usage_hours[1] if len(low_usage_hours) > 1 else 4,
            'analysis_tasks': low_usage_hours[2] if len(low_usage_hours) > 2 else 5,
            'optimization': low_usage_hours[3] if len(low_usage_hours) > 3 else 2
        }
        
        return schedule
    
    def find_low_usage_periods(self, activity_pattern: Dict) -> List[int]:
        """Find periods of low user activity for training."""
        
        # Default low usage periods (assuming typical patterns)
        default_low_usage = [2, 3, 4, 5]  # 2-5 AM
        
        if not activity_pattern:
            return default_low_usage
        
        # Analyze hourly activity
        hourly_activity = activity_pattern.get('hourly_usage', {})
        
        # Find hours with lowest activity
        sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1])
        low_usage_hours = [int(hour) for hour, activity in sorted_hours[:4]]
        
        return low_usage_hours if low_usage_hours else default_low_usage
    
    def adapt_training_intensity(self, performance_feedback: Dict) -> Dict:
        """Adapt training intensity based on performance feedback."""
        
        intensity_config = {
            'data_collection_frequency': 'normal',  # normal, high, low
            'retraining_frequency': 'normal',
            'analysis_depth': 'normal'
        }
        
        # Increase intensity if performance is poor
        if performance_feedback.get('user_satisfaction', 0.5) < 0.6:
            intensity_config['data_collection_frequency'] = 'high'
            intensity_config['retraining_frequency'] = 'high'
            intensity_config['analysis_depth'] = 'high'
        
        # Decrease intensity if performance is excellent
        elif performance_feedback.get('user_satisfaction', 0.5) > 0.9:
            intensity_config['data_collection_frequency'] = 'low'
            intensity_config['retraining_frequency'] = 'low'
        
        return intensity_config

def main():
    """Test the resource management system."""
    print("Testing ARK Resource Manager...")
    
    # Test API manager
    api_manager = ExternalAPIManager()
    
    print("🌐 Testing news collection...")
    news_data = api_manager.get_news_data("artificial intelligence", 3)
    print(f"   Collected {len(news_data)} news articles")
    
    print("📚 Testing knowledge collection...")
    knowledge_data = api_manager.get_knowledge_base_data(["productivity", "time management"])
    print(f"   Collected {len(knowledge_data)} knowledge articles")
    
    print("💡 Testing productivity insights...")
    productivity_data = api_manager.get_productivity_insights()
    print(f"   Collected {len(productivity_data)} productivity tips")
    
    # Test data augmentation
    augmenter = TrainingDataAugmenter()
    sample_conversation = {
        'input': "Can you help me organize my tasks?",
        'output': "I'd be happy to help you organize your tasks. Let me break this down into manageable steps.",
        'category': 'task_management'
    }
    
    print("🔄 Testing data augmentation...")
    variations = augmenter.create_conversation_variations(sample_conversation)
    print(f"   Created {len(variations)} conversation variations")
    
    print("✅ Resource Manager testing complete!")

if __name__ == "__main__":
    main()