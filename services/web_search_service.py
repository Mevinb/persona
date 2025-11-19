"""
Web Search & Information Service
==============================
Comprehensive web search, news, weather, and information retrieval service.
"""

import re
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_service import BaseService, ServiceResult

class WebSearchService(BaseService):
    """Web search and information service for ARK."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("web_search", config)
        self.search_engine = self.config.get("search_engine", "google")
        self.news_enabled = self.config.get("news_enabled", True)
        self.weather_enabled = self.config.get("weather_enabled", True)
        
    def initialize(self) -> bool:
        """Initialize web search service."""
        try:
            # Test internet connectivity
            response = requests.get("https://httpbin.org/get", timeout=5)
            if response.status_code == 200:
                self.is_initialized = True
                self.log_info("Web search service initialized successfully")
                return True
            else:
                self.log_error("No internet connectivity")
                return False
        except Exception as e:
            self.log_error(f"Failed to initialize web search service: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get web search service capabilities."""
        capabilities = ["web_search", "quick_facts", "definitions"]
        if self.news_enabled:
            capabilities.extend(["news", "headlines", "trending"])
        if self.weather_enabled:
            capabilities.extend(["weather", "forecast", "current_conditions"])
        return capabilities
    
    def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute web search command."""
        params = parameters or {}
        
        try:
            if command == "search":
                return self._web_search(params)
            elif command == "weather":
                return self._get_weather(params)
            elif command == "news":
                return self._get_news(params)
            elif command == "definition":
                return self._get_definition(params)
            elif command == "quick_facts":
                return self._get_quick_facts(params)
            else:
                return {"error": f"Unknown search command: {command}"}
                
        except Exception as e:
            self.log_error(f"Search command '{command}' failed: {e}")
            return {"error": str(e)}
    
    def _web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web search."""
        query = self._extract_search_query(params.get("input", ""))
        
        if not query:
            return {
                "action": "request_info",
                "message": "What would you like me to search for?",
                "needed": "search_query"
            }
        
        # Demo search results (in production, would use search APIs)
        demo_results = [
            {
                "title": f"Search Results for: {query}",
                "url": f"https://example.com/search?q={query}",
                "snippet": f"Here are the most relevant results for your search about {query}. This would contain actual search results from the web.",
                "domain": "example.com"
            },
            {
                "title": f"{query} - Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/{query}",
                "snippet": f"Wikipedia article providing comprehensive information about {query}.",
                "domain": "wikipedia.org"
            },
            {
                "title": f"Latest news about {query}",
                "url": f"https://news.example.com/{query}",
                "snippet": f"Recent news and updates related to {query}.",
                "domain": "news.example.com"
            }
        ]
        
        return {
            "action": "search_results",
            "query": query,
            "results": demo_results,
            "message": f"Found {len(demo_results)} results for '{query}'"
        }
    
    def _get_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather information."""
        location = self._extract_location(params.get("input", ""))
        
        if not location:
            location = "your location"  # Default
        
        # Demo weather data
        demo_weather = {
            "location": location,
            "current": {
                "temperature": "72°F",
                "condition": "Partly Cloudy",
                "humidity": "65%",
                "wind": "8 mph NW"
            },
            "forecast": [
                {
                    "day": "Today",
                    "high": "75°F",
                    "low": "58°F", 
                    "condition": "Partly Cloudy"
                },
                {
                    "day": "Tomorrow",
                    "high": "78°F",
                    "low": "60°F",
                    "condition": "Sunny"
                },
                {
                    "day": "Thursday",
                    "high": "71°F",
                    "low": "55°F",
                    "condition": "Rain"
                }
            ],
            "alerts": []
        }
        
        return {
            "action": "weather_info",
            "weather": demo_weather,
            "message": f"Current weather in {location}: {demo_weather['current']['temperature']}, {demo_weather['current']['condition']}"
        }
    
    def _get_news(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get news headlines."""
        topic = self._extract_news_topic(params.get("input", ""))
        
        # Demo news data
        demo_news = [
            {
                "headline": "Major Technology Breakthrough Announced",
                "source": "Tech News",
                "time": "2 hours ago",
                "summary": "Researchers have made a significant breakthrough in artificial intelligence...",
                "url": "https://technews.example.com/breakthrough"
            },
            {
                "headline": "Global Climate Summit Reaches Agreement", 
                "source": "World News",
                "time": "4 hours ago",
                "summary": "World leaders have reached a consensus on new climate initiatives...",
                "url": "https://worldnews.example.com/climate"
            },
            {
                "headline": "Stock Market Shows Strong Performance",
                "source": "Financial Times",
                "time": "6 hours ago", 
                "summary": "Major indices continue upward trend amid positive economic indicators...",
                "url": "https://finance.example.com/markets"
            }
        ]
        
        if topic:
            # Filter news by topic
            filtered_news = [n for n in demo_news if topic.lower() in n["headline"].lower()]
            if filtered_news:
                demo_news = filtered_news
        
        return {
            "action": "news_results",
            "topic": topic or "general",
            "articles": demo_news,
            "message": f"Here are the latest {'news headlines' if not topic else f'news about {topic}'}"
        }
    
    def _get_definition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get definition of a term."""
        term = self._extract_definition_term(params.get("input", ""))
        
        if not term:
            return {
                "action": "request_info",
                "message": "What term would you like me to define?",
                "needed": "term"
            }
        
        # Demo definition
        demo_definition = {
            "term": term,
            "pronunciation": f"/{term}/",
            "part_of_speech": "noun",
            "definition": f"A comprehensive explanation of the term '{term}' would be provided here with detailed meaning and context.",
            "examples": [
                f"Here's an example sentence using {term}.",
                f"Another context where {term} would be used."
            ],
            "synonyms": ["example", "sample", "instance"]
        }
        
        return {
            "action": "definition_result",
            "definition": demo_definition,
            "message": f"Definition of '{term}': {demo_definition['definition']}"
        }
    
    def _get_quick_facts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get quick facts about a topic."""
        topic = self._extract_search_query(params.get("input", ""))
        
        demo_facts = {
            "topic": topic,
            "facts": [
                f"Interesting fact #1 about {topic}",
                f"Key information point about {topic}",
                f"Notable detail regarding {topic}"
            ],
            "sources": ["Encyclopedia", "Academic Research", "Official Documentation"]
        }
        
        return {
            "action": "quick_facts",
            "facts": demo_facts,
            "message": f"Here are some quick facts about {topic}"
        }
    
    def _extract_search_query(self, text: str) -> str:
        """Extract search query from natural language input."""
        text = text.lower()
        
        # Remove search command words
        search_words = ["search for", "look up", "find", "what is", "tell me about"]
        for word in search_words:
            if word in text:
                text = text.replace(word, "", 1).strip()
                break
        
        # Clean up the query
        text = text.strip("?.,!\"'")
        return text.strip()
    
    def _extract_location(self, text: str) -> str:
        """Extract location from weather request."""
        text = text.lower()
        
        # Look for location indicators
        location_patterns = [
            r"weather in ([\\w\\s,]+)",
            r"weather for ([\\w\\s,]+)",
            r"weather at ([\\w\\s,]+)",
            r"forecast for ([\\w\\s,]+)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_news_topic(self, text: str) -> str:
        """Extract news topic from request."""
        text = text.lower()
        
        # Look for topic indicators
        topic_patterns = [
            r"news about ([\\w\\s]+)",
            r"news on ([\\w\\s]+)",
            r"latest on ([\\w\\s]+)",
            r"headlines about ([\\w\\s]+)"
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_definition_term(self, text: str) -> str:
        """Extract term to define from request."""
        text = text.lower()
        
        # Look for definition indicators
        definition_patterns = [
            r"define ([\\w\\s]+)",
            r"what is ([\\w\\s]+)",
            r"definition of ([\\w\\s]+)",
            r"meaning of ([\\w\\s]+)"
        ]
        
        for pattern in definition_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""