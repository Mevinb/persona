"""
Internet Dataset Trainer for ARK
=================================
Downloads and processes multiple datasets from the internet to train ARK
with diverse knowledge from various domains.
"""

import os
import json
import sqlite3
import requests
import csv
import zipfile
import tarfile
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging
import threading
import time
from urllib.parse import urlparse
import hashlib
import re

class InternetDatasetTrainer:
    """Downloads and processes internet datasets for ARK training."""
    
    def __init__(self):
        self.datasets_dir = "data/internet_datasets"
        self.processed_dir = "data/processed_datasets"
        self.db_path = "data/ark_complete_training.db"
        
        # Dataset sources
        self.dataset_sources = {
            "conversational": [
                {
                    "name": "Cornell Movie Dialogs",
                    "url": "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip",
                    "type": "conversational",
                    "description": "Movie conversations for natural dialogue training"
                },
                {
                    "name": "PersonaChat",
                    "url": "https://raw.githubusercontent.com/facebookresearch/ParlAI/main/parlai/tasks/personachat/personachat.txt",
                    "type": "conversational", 
                    "description": "Personality-based conversations"
                }
            ],
            "educational": [
                {
                    "name": "SQuAD QA",
                    "url": "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/train-v1.1.json",
                    "type": "qa",
                    "description": "Stanford Question Answering Dataset"
                },
                {
                    "name": "MS MARCO QA",
                    "url": "https://msmarco.blob.core.windows.net/msmarcoranking/qidpidtriples.train.full.2.tsv.gz",
                    "type": "qa",
                    "description": "Microsoft Machine Reading Comprehension"
                }
            ],
            "knowledge": [
                {
                    "name": "WikiQA",
                    "url": "https://download.microsoft.com/download/E/5/F/E5FCFCEE-7005-4814-853D-DAA7C66507E0/WikiQACorpus.zip",
                    "type": "knowledge",
                    "description": "Wikipedia-based question answering"
                },
                {
                    "name": "Natural Questions",
                    "url": "https://storage.googleapis.com/natural_questions/v1.0-simplified/simplified-nq-train.jsonl.gz",
                    "type": "knowledge",
                    "description": "Google Natural Questions dataset"
                }
            ],
            "instruction": [
                {
                    "name": "Alpaca Instructions",
                    "url": "https://raw.githubusercontent.com/tatsu-lab/stanford_alpaca/main/alpaca_data.json",
                    "type": "instruction",
                    "description": "Instruction-following training data"
                },
                {
                    "name": "OpenAssistant",
                    "url": "https://huggingface.co/datasets/OpenAssistant/oasst1/raw/main/data/2023-04-12_oasst_ready.trees.jsonl.gz",
                    "type": "instruction",
                    "description": "Human-assistant conversations"
                }
            ],
            "academic": [
                {
                    "name": "ArXiv Papers",
                    "url": "https://www.kaggle.com/datasets/Cornell-University/arxiv/download?datasetVersionNumber=128",
                    "type": "academic",
                    "description": "Academic paper abstracts and metadata"
                },
                {
                    "name": "PubMed QA",
                    "url": "https://github.com/pubmedqa/pubmedqa/raw/master/data/ori_pqal.json",
                    "type": "academic",
                    "description": "Biomedical question answering"
                }
            ]
        }
        
        # Ensure directories exist
        os.makedirs(self.datasets_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Training statistics
        self.training_stats = {
            "datasets_downloaded": 0,
            "datasets_processed": 0,
            "training_examples_added": 0,
            "start_time": datetime.now().isoformat()
        }
    
    def download_all_datasets(self):
        """Download all available datasets."""
        
        print("🌐 DOWNLOADING INTERNET DATASETS")
        print("=" * 40)
        
        total_datasets = sum(len(sources) for sources in self.dataset_sources.values())
        downloaded = 0
        
        for category, datasets in self.dataset_sources.items():
            print(f"\n📂 Category: {category.upper()}")
            print("-" * 30)
            
            for dataset in datasets:
                try:
                    print(f"📥 Downloading: {dataset['name']}")
                    success = self._download_dataset(dataset)
                    
                    if success:
                        downloaded += 1
                        print(f"✅ Downloaded: {dataset['name']}")
                    else:
                        print(f"❌ Failed: {dataset['name']}")
                        
                except Exception as e:
                    print(f"❌ Error downloading {dataset['name']}: {e}")
        
        print(f"\n📊 Download Summary: {downloaded}/{total_datasets} datasets downloaded")
        self.training_stats["datasets_downloaded"] = downloaded
        
        return downloaded > 0
    
    def _download_dataset(self, dataset_info: Dict) -> bool:
        """Download a single dataset."""
        
        url = dataset_info["url"]
        name = dataset_info["name"]
        
        # Generate filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path) or f"{name.replace(' ', '_').lower()}.data"
        filepath = os.path.join(self.datasets_dir, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            print(f"  ⚠️  Already exists: {filename}")
            return True
        
        try:
            # Download with progress
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  📊 Progress: {progress:.1f}%", end="", flush=True)
            
            print(f"\r  ✅ Downloaded: {filename} ({self._format_size(downloaded)})")
            
            # Extract if compressed
            if filename.endswith(('.zip', '.gz', '.tar.gz')):
                self._extract_dataset(filepath)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Download error for {name}: {e}")
            return False
    
    def _extract_dataset(self, filepath: str):
        """Extract compressed datasets."""
        
        try:
            extract_dir = filepath.replace('.zip', '').replace('.gz', '').replace('.tar', '')
            
            if filepath.endswith('.zip'):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif filepath.endswith('.tar.gz'):
                with tarfile.open(filepath, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
            elif filepath.endswith('.gz'):
                import gzip
                with gzip.open(filepath, 'rb') as f_in:
                    with open(extract_dir, 'wb') as f_out:
                        f_out.write(f_in.read())
            
            print(f"  🗂️  Extracted to: {os.path.basename(extract_dir)}")
            
        except Exception as e:
            self.logger.error(f"Extraction error: {e}")
    
    def process_all_datasets(self):
        """Process all downloaded datasets for training."""
        
        print("\n🔄 PROCESSING DATASETS FOR TRAINING")
        print("=" * 40)
        
        # Find all downloaded files
        dataset_files = []
        for root, dirs, files in os.walk(self.datasets_dir):
            for file in files:
                if file.endswith(('.json', '.jsonl', '.csv', '.tsv', '.txt')):
                    dataset_files.append(os.path.join(root, file))
        
        print(f"📁 Found {len(dataset_files)} dataset files to process")
        
        processed_count = 0
        total_examples = 0
        
        for file_path in dataset_files:
            try:
                print(f"\n🔄 Processing: {os.path.basename(file_path)}")
                
                examples = self._process_dataset_file(file_path)
                
                if examples:
                    self._save_training_examples(examples, os.path.basename(file_path))
                    processed_count += 1
                    total_examples += len(examples)
                    print(f"✅ Processed: {len(examples)} examples from {os.path.basename(file_path)}")
                else:
                    print(f"⚠️  No examples extracted from {os.path.basename(file_path)}")
                    
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        
        print(f"\n📊 Processing Summary:")
        print(f"   Files processed: {processed_count}/{len(dataset_files)}")
        print(f"   Training examples: {total_examples}")
        
        self.training_stats["datasets_processed"] = processed_count
        self.training_stats["training_examples_added"] = total_examples
        
        return total_examples > 0
    
    def _process_dataset_file(self, file_path: str) -> List[Dict]:
        """Process a single dataset file."""
        
        filename = os.path.basename(file_path).lower()
        examples = []
        
        try:
            # JSON files
            if filename.endswith('.json'):
                examples = self._process_json_dataset(file_path)
            
            # JSONL files
            elif filename.endswith('.jsonl'):
                examples = self._process_jsonl_dataset(file_path)
            
            # CSV/TSV files  
            elif filename.endswith(('.csv', '.tsv')):
                examples = self._process_csv_dataset(file_path)
            
            # Text files
            elif filename.endswith('.txt'):
                examples = self._process_text_dataset(file_path)
            
            # Limit examples per file to avoid overwhelming
            if len(examples) > 1000:
                examples = examples[:1000]
                print(f"  ⚠️  Limited to 1000 examples")
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Processing error for {file_path}: {e}")
            return []
    
    def _process_json_dataset(self, file_path: str) -> List[Dict]:
        """Process JSON dataset files."""
        
        examples = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            for item in data[:500]:  # Limit processing
                example = self._extract_qa_from_item(item)
                if example:
                    examples.append(example)
        
        elif isinstance(data, dict):
            # Handle SQuAD format
            if 'data' in data:
                for article in data['data'][:50]:  # Limit articles
                    for paragraph in article.get('paragraphs', []):
                        for qa in paragraph.get('qas', []):
                            if qa.get('question') and qa.get('answers'):
                                answer = qa['answers'][0]['text'] if qa['answers'] else ""
                                if answer:
                                    examples.append({
                                        "category": "knowledge_qa",
                                        "input_text": qa['question'],
                                        "output_text": self._format_qa_response(qa['question'], answer),
                                        "quality_score": 0.85,
                                        "source": "internet_dataset"
                                    })
        
        return examples
    
    def _process_jsonl_dataset(self, file_path: str) -> List[Dict]:
        """Process JSONL dataset files."""
        
        examples = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= 500:  # Limit processing
                    break
                
                try:
                    item = json.loads(line.strip())
                    example = self._extract_qa_from_item(item)
                    if example:
                        examples.append(example)
                except:
                    continue
        
        return examples
    
    def _process_csv_dataset(self, file_path: str) -> List[Dict]:
        """Process CSV/TSV dataset files."""
        
        examples = []
        delimiter = '\t' if file_path.endswith('.tsv') else ','
        
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, nrows=500, encoding='utf-8', on_bad_lines='skip')
            
            for _, row in df.iterrows():
                # Try to find question and answer columns
                question_col = None
                answer_col = None
                
                for col in df.columns:
                    col_lower = col.lower()
                    if 'question' in col_lower or 'query' in col_lower:
                        question_col = col
                    elif 'answer' in col_lower or 'response' in col_lower or 'text' in col_lower:
                        answer_col = col
                
                if question_col and answer_col:
                    question = str(row[question_col]).strip()
                    answer = str(row[answer_col]).strip()
                    
                    if len(question) > 5 and len(answer) > 10:
                        examples.append({
                            "category": "general_qa",
                            "input_text": question,
                            "output_text": self._format_qa_response(question, answer),
                            "quality_score": 0.8,
                            "source": "internet_dataset"
                        })
        
        except Exception as e:
            self.logger.error(f"CSV processing error: {e}")
        
        return examples
    
    def _process_text_dataset(self, file_path: str) -> List[Dict]:
        """Process text dataset files."""
        
        examples = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split into conversations or Q&A pairs
        if 'Q:' in content and 'A:' in content:
            qa_pairs = re.findall(r'Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)', content, re.DOTALL)
            
            for question, answer in qa_pairs[:100]:  # Limit
                question = question.strip()
                answer = answer.strip()
                
                if len(question) > 5 and len(answer) > 10:
                    examples.append({
                        "category": "conversational",
                        "input_text": question,
                        "output_text": self._format_conversational_response(answer),
                        "quality_score": 0.75,
                        "source": "internet_dataset"
                    })
        
        return examples
    
    def _extract_qa_from_item(self, item: Dict) -> Dict:
        """Extract Q&A from various item formats."""
        
        # Common patterns for question-answer extraction
        question = None
        answer = None
        
        # Pattern 1: Direct question/answer
        if 'question' in item and 'answer' in item:
            question = item['question']
            answer = item['answer']
        
        # Pattern 2: Input/output format  
        elif 'input' in item and 'output' in item:
            question = item['input']
            answer = item['output']
        
        # Pattern 3: Instruction format
        elif 'instruction' in item and 'response' in item:
            question = item['instruction']
            answer = item['response']
        
        # Pattern 4: Text format
        elif 'text' in item and isinstance(item['text'], str):
            text = item['text']
            if ':' in text:
                parts = text.split(':', 1)
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
        
        if question and answer and len(question) > 5 and len(answer) > 10:
            return {
                "category": "general_knowledge",
                "input_text": question,
                "output_text": self._format_knowledge_response(answer),
                "quality_score": 0.8,
                "source": "internet_dataset"
            }
        
        return None
    
    def _format_qa_response(self, question: str, answer: str) -> str:
        """Format Q&A into ARK response style."""
        
        return f"""🎯 **Question: {question}**

**Answer:**
{answer}

💡 **Additional Context:**
This information is based on reliable sources and provides a comprehensive answer to your question. Feel free to ask for clarification or related topics if needed!"""
    
    def _format_knowledge_response(self, answer: str) -> str:
        """Format knowledge response into ARK style."""
        
        return f"""📚 **Knowledge Response**

{answer}

**Key Points:**
• Comprehensive information provided
• Based on reliable sources  
• Additional details available upon request

Would you like me to explain any specific aspect in more detail?"""
    
    def _format_conversational_response(self, response: str) -> str:
        """Format conversational response into ARK style."""
        
        return f"""💬 **Conversational Response**

{response}

I'm here to help with any questions or continue our conversation. What would you like to discuss next?"""
    
    def _save_training_examples(self, examples: List[Dict], source_file: str):
        """Save training examples to database."""
        
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
            except Exception as e:
                self.logger.error(f"Database insert error: {e}")
        
        conn.commit()
        conn.close()
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_training_statistics(self) -> Dict:
        """Get training statistics."""
        
        # Add database statistics
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM training_data")
            total_examples = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT category, COUNT(*) 
                FROM training_data 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            """)
            category_stats = cursor.fetchall()
            
            conn.close()
            
            self.training_stats.update({
                "total_training_examples": total_examples,
                "category_distribution": dict(category_stats),
                "end_time": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Statistics error: {e}")
        
        return self.training_stats
    
    def train_ark_with_internet_data(self):
        """Complete training pipeline with internet datasets."""
        
        print("🚀 ARK INTERNET DATASET TRAINING")
        print("=" * 40)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Download datasets
        if self.download_all_datasets():
            print("\n✅ Dataset download completed")
        else:
            print("\n⚠️  Some datasets failed to download")
        
        # Step 2: Process datasets
        if self.process_all_datasets():
            print("\n✅ Dataset processing completed")
        else:
            print("\n❌ Dataset processing failed")
            return False
        
        # Step 3: Show statistics
        stats = self.get_training_statistics()
        print(f"\n📊 TRAINING STATISTICS")
        print("-" * 25)
        print(f"   Datasets downloaded: {stats['datasets_downloaded']}")
        print(f"   Datasets processed: {stats['datasets_processed']}")
        print(f"   Training examples added: {stats['training_examples_added']}")
        print(f"   Total examples in DB: {stats.get('total_training_examples', 0)}")
        
        if stats.get('category_distribution'):
            print(f"\n📂 Category Distribution:")
            for category, count in list(stats['category_distribution'].items())[:10]:
                print(f"   {category}: {count} examples")
        
        print(f"\n🎉 ARK Internet training completed!")
        return True


def run_internet_training():
    """Run the complete internet training process."""
    
    trainer = InternetDatasetTrainer()
    success = trainer.train_ark_with_internet_data()
    
    if success:
        print("\n🎯 Testing ARK with new knowledge...")
        
        # Test ARK with the new training
        try:
            from ark_intelligent_brain import ARKIntelligentBrain
            
            ark = ARKIntelligentBrain()
            
            test_questions = [
                "What is machine learning?",
                "Explain quantum computing concepts",
                "How do neural networks work?",
                "What is artificial intelligence?",
                "Describe deep learning techniques"
            ]
            
            print("\n🧪 Testing enhanced ARK:")
            
            for question in test_questions:
                response = ark.process_input(question)
                quality = "Enhanced" if len(response) > 200 else "Standard"
                print(f"\nQ: {question}")
                print(f"A: {quality} response ({len(response)} chars)")
                print(f"Preview: {response[:100]}...")
        
        except Exception as e:
            print(f"❌ Testing error: {e}")
    
    return success


if __name__ == "__main__":
    run_internet_training()