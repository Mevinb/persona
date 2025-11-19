"""
ARK Large-Scale Data Processing Pipeline
======================================
Efficient data preprocessing and streaming for massive datasets used in enterprise AI training.
Includes data cleaning, tokenization, chunking, and distributed processing.
"""

import asyncio
import multiprocessing as mp
from multiprocessing import Pool, Queue, Process, Manager
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import torch
from torch.utils.data import IterableDataset, DataLoader
import numpy as np
import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Iterator, Generator
import sqlite3
from pathlib import Path
import pickle
import gzip
import lz4.frame
import hashlib
import mmap
from dataclasses import dataclass
import psutil
import gc
from transformers import AutoTokenizer
from datasets import load_dataset, Dataset
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import h5py
from tqdm import tqdm
import redis
import requests
from urllib.parse import urlparse
import shutil
import zipfile
import tarfile


@dataclass
class DataProcessingConfig:
    """Configuration for large-scale data processing."""
    
    # Input Configuration
    input_sources: List[str] = None  # URLs, file paths, or dataset names
    input_format: str = "auto"  # auto, json, jsonl, txt, csv, parquet, hdf5
    
    # Processing Configuration
    chunk_size: int = 10000  # Process in chunks
    max_sequence_length: int = 1024
    min_sequence_length: int = 50
    overlap: int = 128  # Overlap between chunks
    
    # Output Configuration
    output_dir: str = "data/processed"
    output_format: str = "parquet"  # parquet, hdf5, jsonl, binary
    compression: str = "lz4"  # none, gzip, lz4, snappy
    
    # Tokenization
    tokenizer_name: str = "microsoft/DialoGPT-medium"
    vocab_size: int = 50257
    add_special_tokens: bool = True
    
    # Quality Filtering
    min_quality_score: float = 0.5
    language: str = "en"
    remove_duplicates: bool = True
    remove_short_texts: bool = True
    remove_repetitive: bool = True
    
    # Processing
    num_workers: int = mp.cpu_count()
    batch_size: int = 1000
    cache_size_gb: float = 4.0
    use_distributed: bool = False
    
    # Monitoring
    log_every: int = 10000
    save_every: int = 100000
    progress_tracking: bool = True


class QualityFilter:
    """Text quality filtering for training data."""
    
    def __init__(self, config: DataProcessingConfig):
        self.config = config
        self.seen_hashes = set()
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate text quality score (0-1)."""
        if not text or len(text.strip()) == 0:
            return 0.0
        
        score = 1.0
        
        # Length penalty for very short texts
        if len(text) < self.config.min_sequence_length:
            score *= 0.1
        
        # Check for repetitive content
        if self.is_repetitive(text):
            score *= 0.3
        
        # Check character diversity
        unique_chars = len(set(text.lower()))
        total_chars = len(text)
        diversity = unique_chars / max(total_chars, 1)
        score *= min(diversity * 2, 1.0)
        
        # Check for meaningful content (not just symbols)
        alpha_ratio = sum(1 for c in text if c.isalpha()) / max(len(text), 1)
        score *= min(alpha_ratio * 1.5, 1.0)
        
        # Penalty for excessive uppercase
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if upper_ratio > 0.3:
            score *= 0.7
        
        return min(score, 1.0)
    
    def is_repetitive(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text is repetitive."""
        words = text.lower().split()
        if len(words) < 10:
            return False
        
        # Check for repeated phrases
        for phrase_len in [2, 3, 4]:
            phrases = []
            for i in range(len(words) - phrase_len + 1):
                phrase = " ".join(words[i:i+phrase_len])
                phrases.append(phrase)
            
            if phrases:
                unique_phrases = set(phrases)
                repetition_ratio = 1 - (len(unique_phrases) / len(phrases))
                if repetition_ratio > threshold:
                    return True
        
        return False
    
    def is_duplicate(self, text: str) -> bool:
        """Check if text is duplicate."""
        if not self.config.remove_duplicates:
            return False
        
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        if text_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(text_hash)
        return False
    
    def filter_text(self, text: str) -> Optional[str]:
        """Apply all filters to text."""
        if not text or not text.strip():
            return None
        
        # Remove duplicates
        if self.is_duplicate(text):
            return None
        
        # Quality score filtering
        quality_score = self.calculate_quality_score(text)
        if quality_score < self.config.min_quality_score:
            return None
        
        return text.strip()


class StreamingDataProcessor:
    """High-performance streaming data processor."""
    
    def __init__(self, config: DataProcessingConfig):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.tokenizer_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.quality_filter = QualityFilter(config)
        
        # Processing stats
        self.stats = {
            "total_processed": 0,
            "total_filtered": 0,
            "total_tokens": 0,
            "processing_speed": 0.0,
            "start_time": time.time()
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
    
    def download_dataset(self, url: str, cache_dir: str = "cache") -> str:
        """Download dataset from URL."""
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create filename from URL
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or "dataset"
        local_path = os.path.join(cache_dir, filename)
        
        if os.path.exists(local_path):
            self.logger.info(f"Using cached dataset: {local_path}")
            return local_path
        
        self.logger.info(f"Downloading dataset from {url}")
        
        # Download with progress bar
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(local_path, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        # Extract if compressed
        if local_path.endswith(('.zip', '.tar.gz', '.tgz')):
            extract_dir = local_path.rsplit('.', 1)[0]
            if local_path.endswith('.zip'):
                with zipfile.ZipFile(local_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            else:
                with tarfile.open(local_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)
            
            return extract_dir
        
        return local_path
    
    def detect_format(self, file_path: str) -> str:
        """Auto-detect file format."""
        extension = Path(file_path).suffix.lower()
        
        format_map = {
            '.json': 'json',
            '.jsonl': 'jsonl',
            '.txt': 'txt',
            '.csv': 'csv',
            '.parquet': 'parquet',
            '.h5': 'hdf5',
            '.hdf5': 'hdf5'
        }
        
        return format_map.get(extension, 'txt')
    
    def read_data_stream(self, source: str) -> Generator[str, None, None]:
        """Create streaming reader for various data sources."""
        
        # Download if URL
        if source.startswith(('http://', 'https://')):
            source = self.download_dataset(source)
        
        # Handle HuggingFace datasets
        if source.startswith('hf:'):
            dataset_name = source[3:]
            self.logger.info(f"Loading HuggingFace dataset: {dataset_name}")
            dataset = load_dataset(dataset_name, streaming=True)
            
            for split in dataset:
                for item in dataset[split]:
                    # Extract text field (common names)
                    text = None
                    for field in ['text', 'content', 'body', 'message', 'input']:
                        if field in item:
                            text = item[field]
                            break
                    
                    if text:
                        yield text
            return
        
        # Determine format
        file_format = self.config.input_format
        if file_format == "auto":
            file_format = self.detect_format(source)
        
        # Handle directories
        if os.path.isdir(source):
            for root, _, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    yield from self._read_file_stream(file_path, file_format)
        else:
            yield from self._read_file_stream(source, file_format)
    
    def _read_file_stream(self, file_path: str, file_format: str) -> Generator[str, None, None]:
        """Read individual file with streaming."""
        try:
            if file_format == 'txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            yield line
            
            elif file_format == 'jsonl':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            text = self._extract_text_from_json(data)
                            if text:
                                yield text
                        except json.JSONDecodeError:
                            continue
            
            elif file_format == 'json':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                text = self._extract_text_from_json(item)
                                if text:
                                    yield text
                        else:
                            text = self._extract_text_from_json(data)
                            if text:
                                yield text
                    except json.JSONDecodeError:
                        pass
            
            elif file_format == 'csv':
                df = pd.read_csv(file_path, chunksize=self.config.chunk_size)
                for chunk in df:
                    for _, row in chunk.iterrows():
                        for col in chunk.columns:
                            if isinstance(row[col], str) and len(row[col]) > 10:
                                yield row[col]
            
            elif file_format == 'parquet':
                table = pq.read_table(file_path)
                for batch in table.to_batches(max_chunksize=self.config.chunk_size):
                    df = batch.to_pandas()
                    for _, row in df.iterrows():
                        for col in df.columns:
                            if isinstance(row[col], str) and len(row[col]) > 10:
                                yield row[col]
        
        except Exception as e:
            self.logger.warning(f"Error reading {file_path}: {str(e)}")
    
    def _extract_text_from_json(self, data: Union[dict, list, str]) -> Optional[str]:
        """Extract text from JSON data."""
        if isinstance(data, str):
            return data
        
        if isinstance(data, dict):
            # Common text fields
            for field in ['text', 'content', 'body', 'message', 'input', 'output', 'response']:
                if field in data and isinstance(data[field], str):
                    return data[field]
            
            # Concatenate all string values
            texts = []
            for value in data.values():
                if isinstance(value, str) and len(value) > 10:
                    texts.append(value)
            return " ".join(texts) if texts else None
        
        return None
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= self.config.max_sequence_length:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + self.config.max_sequence_length
            chunk_tokens = tokens[start:end]
            
            # Decode chunk back to text
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.config.overlap
        
        return chunks
    
    def tokenize_batch(self, texts: List[str]) -> Dict[str, torch.Tensor]:
        """Tokenize a batch of texts efficiently."""
        # Filter and chunk texts
        processed_texts = []
        for text in texts:
            filtered_text = self.quality_filter.filter_text(text)
            if filtered_text:
                chunks = self.chunk_text(filtered_text)
                processed_texts.extend(chunks)
        
        if not processed_texts:
            return {"input_ids": torch.empty(0, self.config.max_sequence_length, dtype=torch.long)}
        
        # Tokenize batch
        encoding = self.tokenizer(
            processed_texts,
            max_length=self.config.max_sequence_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return encoding
    
    def save_batch(self, batch_data: Dict[str, torch.Tensor], batch_idx: int):
        """Save processed batch to disk."""
        if self.config.output_format == 'parquet':
            # Convert to pandas DataFrame
            df_data = {}
            for key, tensor in batch_data.items():
                if tensor.numel() > 0:
                    df_data[key] = tensor.numpy().tolist()
            
            if df_data:
                df = pd.DataFrame(df_data)
                output_file = os.path.join(self.config.output_dir, f'batch_{batch_idx:06d}.parquet')
                df.to_parquet(output_file, compression=self.config.compression)
        
        elif self.config.output_format == 'hdf5':
            output_file = os.path.join(self.config.output_dir, f'batch_{batch_idx:06d}.h5')
            with h5py.File(output_file, 'w') as f:
                for key, tensor in batch_data.items():
                    if tensor.numel() > 0:
                        f.create_dataset(key, data=tensor.numpy(), compression='gzip')
        
        elif self.config.output_format == 'binary':
            output_file = os.path.join(self.config.output_dir, f'batch_{batch_idx:06d}.pt')
            torch.save(batch_data, output_file)
    
    async def process_data_stream(self, sources: List[str]):
        """Process data from multiple sources with streaming."""
        self.logger.info(f"🚀 Starting data processing for {len(sources)} sources")
        
        batch_texts = []
        batch_idx = 0
        total_processed = 0
        
        for source in sources:
            self.logger.info(f"📁 Processing source: {source}")
            
            try:
                for text in self.read_data_stream(source):
                    batch_texts.append(text)
                    total_processed += 1
                    
                    # Process batch when full
                    if len(batch_texts) >= self.config.batch_size:
                        batch_data = self.tokenize_batch(batch_texts)
                        
                        if batch_data["input_ids"].numel() > 0:
                            self.save_batch(batch_data, batch_idx)
                            batch_idx += 1
                        
                        # Update stats
                        self.stats["total_processed"] = total_processed
                        self.stats["total_tokens"] += batch_data["input_ids"].numel()
                        
                        # Log progress
                        if total_processed % self.config.log_every == 0:
                            elapsed = time.time() - self.stats["start_time"]
                            speed = total_processed / max(elapsed, 1)
                            
                            self.logger.info(f"📊 Processed {total_processed} texts | "
                                           f"Speed: {speed:.1f} texts/sec | "
                                           f"Batches: {batch_idx}")
                        
                        # Clear batch
                        batch_texts = []
                        
                        # Memory management
                        if batch_idx % 100 == 0:
                            gc.collect()
                        
                        # Small async yield
                        await asyncio.sleep(0)
            
            except Exception as e:
                self.logger.error(f"❌ Error processing source {source}: {str(e)}")
        
        # Process remaining texts
        if batch_texts:
            batch_data = self.tokenize_batch(batch_texts)
            if batch_data["input_ids"].numel() > 0:
                self.save_batch(batch_data, batch_idx)
                batch_idx += 1
        
        # Save processing summary
        summary = {
            "total_sources": len(sources),
            "total_texts_processed": total_processed,
            "total_batches": batch_idx,
            "total_tokens": self.stats["total_tokens"],
            "processing_time_seconds": time.time() - self.stats["start_time"],
            "config": self.config.__dict__
        }
        
        summary_path = os.path.join(self.config.output_dir, 'processing_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"✅ Processing completed!")
        self.logger.info(f"📊 Processed {total_processed} texts into {batch_idx} batches")
        self.logger.info(f"💾 Output saved to: {self.config.output_dir}")
        
        return summary


class LargeScaleDataLoader(IterableDataset):
    """Memory-efficient data loader for processed datasets."""
    
    def __init__(self, data_dir: str, shuffle: bool = True, cache_size: int = 1000):
        self.data_dir = data_dir
        self.shuffle = shuffle
        self.cache_size = cache_size
        self.cache = {}
        self.cache_order = []
        
        # Find all batch files
        self.batch_files = list(Path(data_dir).glob('batch_*.parquet'))
        if not self.batch_files:
            self.batch_files = list(Path(data_dir).glob('batch_*.h5'))
        if not self.batch_files:
            self.batch_files = list(Path(data_dir).glob('batch_*.pt'))
        
        self.batch_files.sort()
        
        if shuffle:
            np.random.shuffle(self.batch_files)
    
    def __iter__(self):
        for batch_file in self.batch_files:
            # Load batch
            if batch_file.suffix == '.parquet':
                df = pd.read_parquet(batch_file)
                for _, row in df.iterrows():
                    yield {
                        'input_ids': torch.tensor(row['input_ids']),
                        'attention_mask': torch.tensor(row['attention_mask'])
                    }
            
            elif batch_file.suffix == '.h5':
                with h5py.File(batch_file, 'r') as f:
                    input_ids = torch.tensor(f['input_ids'][:])
                    attention_mask = torch.tensor(f['attention_mask'][:])
                    
                    for i in range(len(input_ids)):
                        yield {
                            'input_ids': input_ids[i],
                            'attention_mask': attention_mask[i]
                        }
            
            elif batch_file.suffix == '.pt':
                batch_data = torch.load(batch_file)
                for i in range(len(batch_data['input_ids'])):
                    yield {
                        'input_ids': batch_data['input_ids'][i],
                        'attention_mask': batch_data['attention_mask'][i]
                    }


async def process_large_dataset(
    sources: List[str],
    output_dir: str = "data/processed_large",
    batch_size: int = 1000,
    max_sequence_length: int = 1024,
    num_workers: int = None
):
    """Process large-scale dataset with optimal configuration."""
    
    if num_workers is None:
        num_workers = min(mp.cpu_count(), 8)
    
    # Create configuration
    config = DataProcessingConfig(
        input_sources=sources,
        output_dir=output_dir,
        batch_size=batch_size,
        max_sequence_length=max_sequence_length,
        num_workers=num_workers,
        chunk_size=10000,
        output_format="parquet",
        compression="lz4"
    )
    
    print("🔄 ARK LARGE-SCALE DATA PROCESSING")
    print("=" * 40)
    print(f"📊 Sources: {len(sources)}")
    print(f"📁 Output: {output_dir}")
    print(f"🔢 Batch size: {batch_size}")
    print(f"📏 Max length: {max_sequence_length}")
    print(f"⚡ Workers: {num_workers}")
    print("=" * 40)
    
    # Initialize processor
    processor = StreamingDataProcessor(config)
    
    # Process data
    summary = await processor.process_data_stream(sources)
    
    return summary


if __name__ == "__main__":
    import sys
    
    # Example usage
    sources = [
        "hf:wikitext",  # HuggingFace dataset
        "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
        # Add your own data sources here
    ]
    
    # Parse command line arguments
    batch_size = 1000
    max_length = 512
    
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            batch_size = 1000
    
    if len(sys.argv) > 2:
        try:
            max_length = int(sys.argv[2])
        except ValueError:
            max_length = 512
    
    print(f"🎯 Configuration: batch_size={batch_size}, max_length={max_length}")
    
    # Run processing
    asyncio.run(process_large_dataset(
        sources=sources,
        batch_size=batch_size,
        max_sequence_length=max_length
    ))