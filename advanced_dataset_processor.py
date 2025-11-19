"""
Advanced Dataset Processor
==========================
Advanced processing for specialized datasets including academic papers,
technical documentation, and domain-specific knowledge.
"""

import requests
import json
import xml.etree.ElementTree as ET
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import logging

class AdvancedDatasetProcessor:
    """Processes specialized datasets for enhanced ARK training."""
    
    def __init__(self):
        self.db_path = "data/ark_complete_training.db"
        self.processed_count = 0
        
        # Specialized dataset sources
        self.specialized_sources = {
            "wikipedia": {
                "api_url": "https://en.wikipedia.org/w/api.php",
                "topics": [
                    "Artificial Intelligence", "Machine Learning", "Deep Learning",
                    "Computer Science", "Mathematics", "Physics", "Chemistry",
                    "Biology", "Psychology", "Philosophy", "History", "Literature"
                ]
            },
            "arxiv": {
                "api_url": "http://export.arxiv.org/api/query",
                "categories": [
                    "cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE",
                    "math.ST", "stat.ML", "physics.data-an"
                ]
            },
            "github_awesome": {
                "repos": [
                    "sindresorhus/awesome",
                    "jwasham/coding-interview-university",
                    "EbookFoundation/free-programming-books",
                    "public-apis/public-apis"
                ]
            }
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_wikipedia_articles(self, max_articles: int = 100) -> List[Dict]:
        """Extract knowledge from Wikipedia articles."""
        
        print("📖 Processing Wikipedia articles...")
        examples = []
        
        for topic in self.specialized_sources["wikipedia"]["topics"]:
            try:
                # Search for articles on this topic
                search_params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": topic,
                    "srlimit": 10
                }
                
                response = requests.get(
                    self.specialized_sources["wikipedia"]["api_url"],
                    params=search_params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get("query", {}).get("search", []):
                        article_title = article["title"]
                        snippet = article.get("snippet", "")
                        
                        if len(snippet) > 50:
                            # Create Q&A from article
                            question = f"What is {article_title}?"
                            answer = self._clean_html(snippet)
                            
                            example = {
                                "category": "wikipedia_knowledge",
                                "input_text": question,
                                "output_text": self._format_wikipedia_response(article_title, answer),
                                "quality_score": 0.9,
                                "source": f"wikipedia_{topic}"
                            }
                            examples.append(example)
                
                if len(examples) >= max_articles:
                    break
                    
            except Exception as e:
                self.logger.error(f"Wikipedia processing error for {topic}: {e}")
        
        print(f"✅ Processed {len(examples)} Wikipedia articles")
        return examples
    
    def process_arxiv_papers(self, max_papers: int = 50) -> List[Dict]:
        """Extract knowledge from ArXiv papers."""
        
        print("🔬 Processing ArXiv papers...")
        examples = []
        
        for category in self.specialized_sources["arxiv"]["categories"]:
            try:
                # Query ArXiv API
                params = {
                    "search_query": f"cat:{category}",
                    "start": 0,
                    "max_results": 10,
                    "sortBy": "relevance",
                    "sortOrder": "descending"
                }
                
                response = requests.get(
                    self.specialized_sources["arxiv"]["api_url"],
                    params=params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    # Parse XML response
                    root = ET.fromstring(response.text)
                    
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                        
                        if title and summary and len(summary) > 100:
                            # Create research Q&A
                            question = f"Explain the research on {title}"
                            
                            example = {
                                "category": "research_knowledge",
                                "input_text": question,
                                "output_text": self._format_research_response(title, summary),
                                "quality_score": 0.95,
                                "source": f"arxiv_{category}"
                            }
                            examples.append(example)
                
                if len(examples) >= max_papers:
                    break
                    
            except Exception as e:
                self.logger.error(f"ArXiv processing error for {category}: {e}")
        
        print(f"✅ Processed {len(examples)} ArXiv papers")
        return examples
    
    def process_github_awesome_lists(self) -> List[Dict]:
        """Process GitHub awesome lists for curated knowledge."""
        
        print("⭐ Processing GitHub awesome lists...")
        examples = []
        
        for repo in self.specialized_sources["github_awesome"]["repos"]:
            try:
                # Get README content
                url = f"https://api.github.com/repos/{repo}/readme"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    readme_data = response.json()
                    
                    # Decode base64 content
                    import base64
                    content = base64.b64decode(readme_data['content']).decode('utf-8')
                    
                    # Extract sections and create training data
                    sections = self._extract_markdown_sections(content)
                    
                    for section_title, section_content in sections.items():
                        if len(section_content) > 100:
                            question = f"What resources are available for {section_title}?"
                            
                            example = {
                                "category": "curated_resources",
                                "input_text": question,
                                "output_text": self._format_resource_response(section_title, section_content),
                                "quality_score": 0.85,
                                "source": f"github_{repo}"
                            }
                            examples.append(example)
            
            except Exception as e:
                self.logger.error(f"GitHub processing error for {repo}: {e}")
        
        print(f"✅ Processed {len(examples)} GitHub resources")
        return examples
    
    def process_public_apis(self) -> List[Dict]:
        """Process public APIs information for technical knowledge."""
        
        print("🌐 Processing public APIs data...")
        examples = []
        
        try:
            # Get public APIs list
            url = "https://api.publicapis.org/entries"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Group APIs by category
                api_categories = {}
                for api in data.get("entries", []):
                    category = api.get("Category", "Other")
                    if category not in api_categories:
                        api_categories[category] = []
                    api_categories[category].append(api)
                
                # Create training examples for each category
                for category, apis in api_categories.items():
                    if len(apis) >= 3:  # Only categories with multiple APIs
                        api_list = apis[:10]  # Limit to 10 APIs per category
                        
                        question = f"What APIs are available for {category}?"
                        
                        example = {
                            "category": "technical_apis",
                            "input_text": question,
                            "output_text": self._format_api_response(category, api_list),
                            "quality_score": 0.8,
                            "source": "public_apis"
                        }
                        examples.append(example)
        
        except Exception as e:
            self.logger.error(f"Public APIs processing error: {e}")
        
        print(f"✅ Processed {len(examples)} API categories")
        return examples
    
    def process_stackoverflow_data(self) -> List[Dict]:
        """Process Stack Overflow data for programming knowledge."""
        
        print("💻 Processing programming Q&A data...")
        examples = []
        
        # Common programming topics
        topics = [
            "python", "javascript", "java", "c++", "machine-learning",
            "web-development", "data-science", "algorithms", "sql", "react"
        ]
        
        for topic in topics:
            try:
                # Using Stack Exchange API
                url = "https://api.stackexchange.com/2.3/questions"
                params = {
                    "order": "desc",
                    "sort": "votes",
                    "tagged": topic,
                    "site": "stackoverflow",
                    "pagesize": 5,
                    "filter": "withbody"
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for question in data.get("items", []):
                        title = question.get("title", "")
                        body = question.get("body", "")
                        
                        if title and len(body) > 50:
                            # Clean HTML from body
                            clean_body = self._clean_html(body)
                            
                            if len(clean_body) > 30:
                                example = {
                                    "category": "programming_help",
                                    "input_text": title,
                                    "output_text": self._format_programming_response(title, clean_body),
                                    "quality_score": 0.85,
                                    "source": f"stackoverflow_{topic}"
                                }
                                examples.append(example)
            
            except Exception as e:
                self.logger.error(f"Stack Overflow processing error for {topic}: {e}")
        
        print(f"✅ Processed {len(examples)} programming Q&As")
        return examples
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    
    def _extract_markdown_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from markdown content."""
        import re
        
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('##'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _format_wikipedia_response(self, title: str, content: str) -> str:
        """Format Wikipedia response."""
        
        return f"""📚 **Wikipedia: {title}**

**Overview:**
{content}

**Key Information:**
• This information is from Wikipedia, a reliable encyclopedia source
• Provides foundational knowledge on the topic
• Additional details available through further research

Would you like me to explain any specific aspect of {title} in more detail?"""
    
    def _format_research_response(self, title: str, abstract: str) -> str:
        """Format research paper response."""
        
        return f"""🔬 **Research Paper: {title}**

**Abstract:**
{abstract[:500]}...

**Research Context:**
• This is from academic research published on ArXiv
• Represents current state-of-the-art knowledge
• May include advanced concepts and methodologies

**Key Takeaways:**
• Cutting-edge research findings
• Peer-reviewed academic content
• Applicable to advanced studies and professional development

Would you like me to explain any technical concepts from this research?"""
    
    def _format_resource_response(self, topic: str, content: str) -> str:
        """Format curated resource response."""
        
        return f"""⭐ **Curated Resources: {topic}**

**Available Resources:**
{content[:400]}...

**Resource Quality:**
• Curated by the developer community
• Regularly updated and maintained
• Covers both beginner and advanced levels

**How to Use:**
• Browse resources by your skill level
• Start with fundamentals before advanced topics
• Contribute back to the community when possible

What specific aspect of {topic} would you like to explore?"""
    
    def _format_api_response(self, category: str, apis: List[Dict]) -> str:
        """Format API information response."""
        
        api_list = []
        for api in apis[:5]:  # Show top 5
            name = api.get('API', 'Unknown')
            desc = api.get('Description', 'No description')
            api_list.append(f"• **{name}**: {desc}")
        
        return f"""🌐 **{category} APIs**

**Available APIs:**
{chr(10).join(api_list)}

**API Integration Tips:**
• Check authentication requirements
• Review rate limits and usage policies
• Test endpoints before production use
• Consider backup alternatives

**Getting Started:**
• Read API documentation thoroughly
• Start with simple GET requests
• Implement proper error handling
• Monitor usage and performance

Would you like specific integration guidance for any of these APIs?"""
    
    def _format_programming_response(self, title: str, content: str) -> str:
        """Format programming Q&A response."""
        
        return f"""💻 **Programming Solution: {title}**

**Problem Context:**
{content[:300]}...

**Solution Approach:**
• Analyze the specific requirements
• Consider performance and scalability
• Implement best practices and clean code
• Test thoroughly with edge cases

**Development Tips:**
• Break complex problems into smaller parts
• Use debugging tools effectively
• Write maintainable and readable code
• Document your implementation

**Best Practices:**
• Follow language-specific conventions
• Implement proper error handling
• Consider security implications
• Optimize for your use case

Need help implementing a specific part of this solution?"""
    
    def save_processed_examples(self, examples: List[Dict]):
        """Save processed examples to database."""
        
        if not examples:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for example in examples:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO training_data (category, input_text, output_text, quality_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    example['category'],
                    example['input_text'],
                    example['output_text'],
                    example['quality_score']
                ))
                self.processed_count += 1
            except Exception as e:
                self.logger.error(f"Database save error: {e}")
        
        conn.commit()
        conn.close()
    
    def process_all_specialized_datasets(self):
        """Process all specialized datasets."""
        
        print("🚀 PROCESSING SPECIALIZED DATASETS")
        print("=" * 40)
        
        all_examples = []
        
        # Process each dataset type
        try:
            all_examples.extend(self.process_wikipedia_articles())
        except Exception as e:
            print(f"❌ Wikipedia processing failed: {e}")
        
        try:
            all_examples.extend(self.process_arxiv_papers())
        except Exception as e:
            print(f"❌ ArXiv processing failed: {e}")
        
        try:
            all_examples.extend(self.process_github_awesome_lists())
        except Exception as e:
            print(f"❌ GitHub processing failed: {e}")
        
        try:
            all_examples.extend(self.process_public_apis())
        except Exception as e:
            print(f"❌ APIs processing failed: {e}")
        
        try:
            all_examples.extend(self.process_stackoverflow_data())
        except Exception as e:
            print(f"❌ StackOverflow processing failed: {e}")
        
        # Save all examples
        if all_examples:
            print(f"\n💾 Saving {len(all_examples)} specialized examples...")
            self.save_processed_examples(all_examples)
            print(f"✅ Saved {self.processed_count} examples to database")
        
        return len(all_examples)


def run_advanced_dataset_processing():
    """Run advanced dataset processing."""
    
    processor = AdvancedDatasetProcessor()
    total_processed = processor.process_all_specialized_datasets()
    
    print(f"\n📊 ADVANCED PROCESSING COMPLETE")
    print(f"Total examples processed: {total_processed}")
    
    return total_processed > 0


if __name__ == "__main__":
    run_advanced_dataset_processing()