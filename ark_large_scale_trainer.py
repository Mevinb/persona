"""
ARK Large-Scale Dataset Training Loop
====================================
Enterprise-grade training system for massive datasets using techniques from leading AI companies.
Includes distributed training, gradient accumulation, mixed precision, and advanced optimization.
"""

import asyncio
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from torch.cuda.amp import GradScaler, autocast
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR, OneCycleLR
import numpy as np
import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import sqlite3
from dataclasses import dataclass
from pathlib import Path
import pickle
import gc
import psutil
from transformers import AutoTokenizer, AutoModel, AdamW, get_linear_schedule_with_warmup
import wandb
from tqdm import tqdm
import math

# Import ARK components
from ark_advanced_intelligence import ARKAdvancedIntelligence


@dataclass
class TrainingConfig:
    """Configuration for large-scale training."""
    
    # Model Configuration
    model_name: str = "microsoft/DialoGPT-medium"
    max_sequence_length: int = 1024
    vocab_size: int = 50257
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    
    # Training Configuration
    batch_size: int = 32
    gradient_accumulation_steps: int = 4
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_steps: int = 1000
    max_epochs: int = 10
    max_steps: int = 100000
    
    # Optimization
    optimizer: str = "adamw"  # adamw, adam, sgd
    scheduler: str = "linear"  # linear, cosine, onecycle
    mixed_precision: bool = True
    gradient_clipping: float = 1.0
    
    # Data Configuration
    dataset_path: str = "data/training_dataset"
    validation_split: float = 0.1
    num_workers: int = 4
    pin_memory: bool = True
    
    # Distributed Training
    distributed: bool = False
    local_rank: int = 0
    world_size: int = 1
    
    # Checkpointing
    save_every: int = 1000  # Save checkpoint every N steps
    checkpoint_dir: str = "checkpoints"
    max_checkpoints: int = 5
    
    # Monitoring
    log_every: int = 10
    eval_every: int = 500
    use_wandb: bool = False
    wandb_project: str = "ark-training"
    
    # Memory Management
    gradient_checkpointing: bool = True
    dataloader_drop_last: bool = True
    empty_cache_every: int = 100


class LargeScaleDataset(torch.utils.data.Dataset):
    """Efficient dataset class for large-scale training."""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 1024, cache_size: int = 10000):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.cache_size = cache_size
        self.cache = {}
        self.cache_order = []
        
        # Load data indices
        self.data_files = self._discover_data_files()
        self.total_samples = self._count_samples()
        
        logging.info(f"Dataset initialized with {self.total_samples} samples from {len(self.data_files)} files")
    
    def _discover_data_files(self) -> List[str]:
        """Discover all data files in the dataset directory."""
        data_path = Path(self.data_path)
        if not data_path.exists():
            # Create sample data if path doesn't exist
            self._create_sample_data()
        
        files = []
        for ext in ['*.txt', '*.json', '*.jsonl']:
            files.extend(list(data_path.glob(ext)))
        
        return [str(f) for f in files]
    
    def _create_sample_data(self):
        """Create sample training data."""
        os.makedirs(self.data_path, exist_ok=True)
        
        # Generate diverse training examples
        sample_conversations = [
            "What is machine learning? Machine learning is a subset of AI that enables computers to learn patterns from data.",
            "How do neural networks work? Neural networks process information through interconnected nodes that mimic brain neurons.",
            "Explain deep learning. Deep learning uses multi-layered neural networks to automatically discover data representations.",
            "What is natural language processing? NLP enables computers to understand, interpret, and generate human language.",
            "How does reinforcement learning work? RL agents learn optimal actions through trial and error in an environment.",
            "What are transformer models? Transformers use attention mechanisms to process sequential data efficiently.",
            "Explain gradient descent. Gradient descent optimizes neural networks by iteratively adjusting parameters.",
            "What is computer vision? Computer vision enables machines to interpret and understand visual information.",
            "How do GANs work? Generative Adversarial Networks train two models competitively to generate realistic data.",
            "What is federated learning? Federated learning trains models across decentralized data without centralizing it."
        ]
        
        # Create training files
        for i in range(10):  # Create 10 sample files
            file_path = Path(self.data_path) / f"training_data_{i}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                for j in range(1000):  # 1000 samples per file
                    conv = sample_conversations[j % len(sample_conversations)]
                    f.write(f"{conv}\n")
    
    def _count_samples(self) -> int:
        """Count total number of samples in dataset."""
        total = 0
        for file_path in self.data_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                total += sum(1 for _ in f)
        return total
    
    def __len__(self):
        return self.total_samples
    
    def __getitem__(self, idx):
        # Check cache first
        if idx in self.cache:
            return self.cache[idx]
        
        # Find the file and line for this index
        current_idx = 0
        for file_path in self.data_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if current_idx + len(lines) > idx:
                    line_idx = idx - current_idx
                    text = lines[line_idx].strip()
                    break
                current_idx += len(lines)
        else:
            raise IndexError(f"Index {idx} out of range")
        
        # Tokenize
        encoded = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Create labels (for language modeling, labels = input_ids shifted)
        labels = encoded['input_ids'].clone()
        
        result = {
            'input_ids': encoded['input_ids'].squeeze(),
            'attention_mask': encoded['attention_mask'].squeeze(),
            'labels': labels.squeeze()
        }
        
        # Cache management
        if len(self.cache) >= self.cache_size:
            # Remove oldest item
            oldest_key = self.cache_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[idx] = result
        self.cache_order.append(idx)
        
        return result


class ARKLargeScaleTrainer:
    """Enterprise-grade trainer for large-scale datasets."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.local_rank = config.local_rank
        self.world_size = config.world_size
        
        # Initialize distributed training
        if config.distributed:
            self._init_distributed()
        
        # Set up logging
        self._setup_logging()
        
        # Initialize model, tokenizer, and datasets
        self.tokenizer = None
        self.model = None
        self.train_loader = None
        self.val_loader = None
        self.optimizer = None
        self.scheduler = None
        self.scaler = None
        
        # Training state
        self.current_epoch = 0
        self.current_step = 0
        self.best_val_loss = float('inf')
        self.training_history = []
        
        # Memory tracking
        self.memory_tracker = {
            'peak_memory_mb': 0,
            'current_memory_mb': 0,
            'memory_history': []
        }
        
        # Initialize monitoring
        if config.use_wandb and (not config.distributed or self.local_rank == 0):
            wandb.init(project=config.wandb_project, config=config.__dict__)
    
    def _init_distributed(self):
        """Initialize distributed training."""
        dist.init_process_group(backend='nccl')
        torch.cuda.set_device(self.local_rank)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_model_and_data(self):
        """Initialize model, tokenizer, and data loaders."""
        self.logger.info("Setting up model and data...")
        
        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Initialize model
        self.model = AutoModel.from_pretrained(self.config.model_name)
        
        # Add language modeling head
        self.model.lm_head = nn.Linear(self.model.config.hidden_size, self.model.config.vocab_size, bias=False)
        
        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
        
        # Move model to device
        self.model.to(self.device)
        
        # Wrap with DDP if distributed
        if self.config.distributed:
            self.model = DDP(self.model, device_ids=[self.local_rank])
        
        # Setup datasets
        full_dataset = LargeScaleDataset(
            self.config.dataset_path, 
            self.tokenizer, 
            self.config.max_sequence_length
        )
        
        # Split dataset
        val_size = int(len(full_dataset) * self.config.validation_split)
        train_size = len(full_dataset) - val_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            full_dataset, [train_size, val_size]
        )
        
        # Create samplers for distributed training
        train_sampler = DistributedSampler(train_dataset) if self.config.distributed else None
        val_sampler = DistributedSampler(val_dataset) if self.config.distributed else None
        
        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=(train_sampler is None),
            sampler=train_sampler,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            drop_last=self.config.dataloader_drop_last
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            sampler=val_sampler,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory
        )
        
        self.logger.info(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")
    
    def _setup_optimization(self):
        """Setup optimizer, scheduler, and mixed precision."""
        # Get model parameters
        model = self.model.module if hasattr(self.model, 'module') else self.model
        
        # Setup optimizer
        if self.config.optimizer.lower() == 'adamw':
            self.optimizer = AdamW(
                model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        elif self.config.optimizer.lower() == 'adam':
            self.optimizer = optim.Adam(
                model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        else:
            self.optimizer = optim.SGD(
                model.parameters(),
                lr=self.config.learning_rate,
                momentum=0.9,
                weight_decay=self.config.weight_decay
            )
        
        # Setup scheduler
        total_steps = min(self.config.max_steps, len(self.train_loader) * self.config.max_epochs)
        
        if self.config.scheduler.lower() == 'linear':
            self.scheduler = get_linear_schedule_with_warmup(
                self.optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=total_steps
            )
        elif self.config.scheduler.lower() == 'cosine':
            self.scheduler = CosineAnnealingLR(
                self.optimizer,
                T_max=total_steps
            )
        elif self.config.scheduler.lower() == 'onecycle':
            self.scheduler = OneCycleLR(
                self.optimizer,
                max_lr=self.config.learning_rate,
                total_steps=total_steps
            )
        
        # Setup mixed precision
        if self.config.mixed_precision:
            self.scaler = GradScaler()
    
    def _track_memory(self):
        """Track GPU/CPU memory usage."""
        if torch.cuda.is_available():
            current_memory = torch.cuda.memory_allocated() / (1024**2)  # MB
            peak_memory = torch.cuda.max_memory_allocated() / (1024**2)  # MB
        else:
            current_memory = psutil.virtual_memory().used / (1024**2)  # MB
            peak_memory = current_memory
        
        self.memory_tracker['current_memory_mb'] = current_memory
        self.memory_tracker['peak_memory_mb'] = max(self.memory_tracker['peak_memory_mb'], peak_memory)
        self.memory_tracker['memory_history'].append({
            'step': self.current_step,
            'memory_mb': current_memory,
            'timestamp': datetime.now().isoformat()
        })
    
    def _forward_pass(self, batch):
        """Perform forward pass with mixed precision."""
        if self.config.mixed_precision:
            with autocast():
                outputs = self.model(**batch)
                if hasattr(outputs, 'logits'):
                    # Calculate loss for language modeling
                    shift_logits = outputs.logits[..., :-1, :].contiguous()
                    shift_labels = batch['labels'][..., 1:].contiguous()
                    loss_fct = nn.CrossEntropyLoss()
                    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
                else:
                    loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
                return loss
        else:
            outputs = self.model(**batch)
            if hasattr(outputs, 'logits'):
                shift_logits = outputs.logits[..., :-1, :].contiguous()
                shift_labels = batch['labels'][..., 1:].contiguous()
                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            else:
                loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
            return loss
    
    def _backward_pass(self, loss):
        """Perform backward pass with gradient accumulation."""
        # Scale loss for gradient accumulation
        loss = loss / self.config.gradient_accumulation_steps
        
        if self.config.mixed_precision:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
    
    def _optimizer_step(self):
        """Perform optimizer step with gradient clipping."""
        if self.config.mixed_precision:
            # Unscale gradients for clipping
            self.scaler.unscale_(self.optimizer)
            
            # Clip gradients
            if self.config.gradient_clipping > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clipping)
            
            # Optimizer step
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            # Clip gradients
            if self.config.gradient_clipping > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clipping)
            
            # Optimizer step
            self.optimizer.step()
        
        # Scheduler step
        if self.scheduler:
            self.scheduler.step()
        
        # Zero gradients
        self.optimizer.zero_grad()
    
    def _evaluate(self):
        """Evaluate model on validation set."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in tqdm(self.val_loader, desc="Evaluating", disable=(self.local_rank != 0)):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                loss = self._forward_pass(batch)
                total_loss += loss.item()
                num_batches += 1
        
        avg_loss = total_loss / max(num_batches, 1)
        
        # Aggregate across all processes if distributed
        if self.config.distributed:
            avg_loss_tensor = torch.tensor(avg_loss, device=self.device)
            dist.all_reduce(avg_loss_tensor, op=dist.ReduceOp.SUM)
            avg_loss = avg_loss_tensor.item() / self.world_size
        
        self.model.train()
        return avg_loss
    
    def _save_checkpoint(self, is_best: bool = False):
        """Save training checkpoint."""
        if self.local_rank != 0:  # Only save on main process
            return
        
        os.makedirs(self.config.checkpoint_dir, exist_ok=True)
        
        # Prepare checkpoint data
        model_state = self.model.module.state_dict() if hasattr(self.model, 'module') else self.model.state_dict()
        
        checkpoint = {
            'epoch': self.current_epoch,
            'step': self.current_step,
            'model_state_dict': model_state,
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'scaler_state_dict': self.scaler.state_dict() if self.scaler else None,
            'best_val_loss': self.best_val_loss,
            'config': self.config.__dict__,
            'training_history': self.training_history,
            'memory_tracker': self.memory_tracker
        }
        
        # Save checkpoint
        checkpoint_path = os.path.join(self.config.checkpoint_dir, f'checkpoint_step_{self.current_step}.pt')
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model separately
        if is_best:
            best_path = os.path.join(self.config.checkpoint_dir, 'best_model.pt')
            torch.save(checkpoint, best_path)
            self.logger.info(f"💎 New best model saved at step {self.current_step}")
        
        # Cleanup old checkpoints
        self._cleanup_old_checkpoints()
        
        self.logger.info(f"💾 Checkpoint saved: {checkpoint_path}")
    
    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints to save disk space."""
        checkpoint_dir = Path(self.config.checkpoint_dir)
        checkpoints = list(checkpoint_dir.glob('checkpoint_step_*.pt'))
        checkpoints.sort(key=lambda x: int(x.stem.split('_')[-1]))
        
        if len(checkpoints) > self.config.max_checkpoints:
            for old_checkpoint in checkpoints[:-self.config.max_checkpoints]:
                old_checkpoint.unlink()
                self.logger.info(f"🗑️  Removed old checkpoint: {old_checkpoint}")
    
    def _log_metrics(self, metrics: Dict, step: int):
        """Log training metrics."""
        # Console logging
        metrics_str = " | ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
        self.logger.info(f"Step {step} | {metrics_str}")
        
        # Wandb logging
        if self.config.use_wandb and (not self.config.distributed or self.local_rank == 0):
            wandb.log(metrics, step=step)
        
        # Save to history
        metrics['step'] = step
        metrics['timestamp'] = datetime.now().isoformat()
        self.training_history.append(metrics)
    
    async def train_epoch(self, epoch: int):
        """Train for one epoch."""
        self.model.train()
        
        if self.config.distributed:
            self.train_loader.sampler.set_epoch(epoch)
        
        epoch_loss = 0.0
        accumulated_loss = 0.0
        epoch_start_time = time.time()
        
        progress_bar = tqdm(
            self.train_loader, 
            desc=f"Epoch {epoch+1}/{self.config.max_epochs}",
            disable=(self.local_rank != 0)
        )
        
        for batch_idx, batch in enumerate(progress_bar):
            if self.current_step >= self.config.max_steps:
                break
            
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass
            loss = self._forward_pass(batch)
            accumulated_loss += loss.item()
            
            # Backward pass
            self._backward_pass(loss)
            
            # Optimizer step (if gradient accumulation complete)
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                self._optimizer_step()
                
                # Update progress
                avg_accumulated_loss = accumulated_loss / self.config.gradient_accumulation_steps
                epoch_loss += avg_accumulated_loss
                
                # Track memory
                self._track_memory()
                
                # Logging
                if self.current_step % self.config.log_every == 0:
                    current_lr = self.scheduler.get_last_lr()[0] if self.scheduler else self.config.learning_rate
                    
                    metrics = {
                        'train_loss': avg_accumulated_loss,
                        'learning_rate': current_lr,
                        'epoch': epoch,
                        'memory_mb': self.memory_tracker['current_memory_mb'],
                        'steps_per_sec': self.config.log_every / (time.time() - epoch_start_time) if epoch_start_time else 0
                    }
                    
                    self._log_metrics(metrics, self.current_step)
                    epoch_start_time = time.time()
                
                # Evaluation
                if self.current_step % self.config.eval_every == 0:
                    val_loss = self._evaluate()
                    
                    eval_metrics = {'val_loss': val_loss}
                    self._log_metrics(eval_metrics, self.current_step)
                    
                    # Save best model
                    is_best = val_loss < self.best_val_loss
                    if is_best:
                        self.best_val_loss = val_loss
                    
                    # Save checkpoint
                    if self.current_step % self.config.save_every == 0 or is_best:
                        self._save_checkpoint(is_best)
                
                # Clear cache periodically
                if self.current_step % self.config.empty_cache_every == 0:
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    gc.collect()
                
                # Reset accumulated loss
                accumulated_loss = 0.0
                self.current_step += 1
                
                # Update progress bar
                progress_bar.set_postfix({
                    'loss': f'{avg_accumulated_loss:.4f}',
                    'lr': f'{current_lr:.2e}',
                    'mem': f'{self.memory_tracker["current_memory_mb"]:.0f}MB'
                })
                
                # Small async yield for responsiveness
                await asyncio.sleep(0)
        
        return epoch_loss / max(len(self.train_loader), 1)
    
    async def train(self):
        """Main training loop."""
        self.logger.info("🚀 Starting large-scale training...")
        
        # Setup model and data
        self._setup_model_and_data()
        self._setup_optimization()
        
        # Training loop
        training_start_time = time.time()
        
        try:
            for epoch in range(self.config.max_epochs):
                if self.current_step >= self.config.max_steps:
                    break
                
                self.current_epoch = epoch
                
                # Train epoch
                epoch_loss = await self.train_epoch(epoch)
                
                self.logger.info(f"✅ Epoch {epoch+1} completed | Average Loss: {epoch_loss:.4f}")
                
                # Save checkpoint at end of epoch
                self._save_checkpoint()
        
        except KeyboardInterrupt:
            self.logger.info("⚠️  Training interrupted by user")
            self._save_checkpoint()
        
        except Exception as e:
            self.logger.error(f"❌ Training failed with error: {str(e)}")
            raise
        
        finally:
            total_time = time.time() - training_start_time
            
            # Final evaluation
            final_val_loss = self._evaluate()
            
            # Final metrics
            final_metrics = {
                'final_val_loss': final_val_loss,
                'total_training_time_hours': total_time / 3600,
                'total_steps': self.current_step,
                'peak_memory_mb': self.memory_tracker['peak_memory_mb']
            }
            
            self._log_metrics(final_metrics, self.current_step)
            
            self.logger.info(f"🎉 Training completed!")
            self.logger.info(f"📊 Total time: {total_time/3600:.2f} hours")
            self.logger.info(f"📈 Total steps: {self.current_step}")
            self.logger.info(f"🏆 Best validation loss: {self.best_val_loss:.4f}")
            self.logger.info(f"💾 Peak memory usage: {self.memory_tracker['peak_memory_mb']:.0f}MB")
            
            # Cleanup
            if self.config.use_wandb:
                wandb.finish()
            
            if self.config.distributed:
                dist.destroy_process_group()


async def run_large_scale_training(config: Optional[TrainingConfig] = None):
    """Run large-scale training with the specified configuration."""
    
    if config is None:
        config = TrainingConfig()
    
    print("🔥 ARK LARGE-SCALE TRAINING SYSTEM")
    print("=" * 50)
    print(f"🎯 Model: {config.model_name}")
    print(f"📊 Dataset: {config.dataset_path}")
    print(f"🔧 Batch size: {config.batch_size} (accumulation: {config.gradient_accumulation_steps})")
    print(f"⚡ Mixed precision: {config.mixed_precision}")
    print(f"🌐 Distributed: {config.distributed}")
    print(f"💾 Max steps: {config.max_steps}")
    print("=" * 50)
    
    # Initialize trainer
    trainer = ARKLargeScaleTrainer(config)
    
    # Start training
    await trainer.train()
    
    return trainer


def create_distributed_config(
    local_rank: int = 0,
    world_size: int = 1,
    batch_size: int = 16,
    max_steps: int = 10000
) -> TrainingConfig:
    """Create configuration for distributed training."""
    
    config = TrainingConfig()
    config.distributed = world_size > 1
    config.local_rank = local_rank
    config.world_size = world_size
    config.batch_size = batch_size
    config.max_steps = max_steps
    config.use_wandb = local_rank == 0  # Only main process logs to wandb
    
    return config


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    batch_size = 16
    max_steps = 5000
    distributed = False
    mixed_precision = True
    
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            batch_size = 16
    
    if len(sys.argv) > 2:
        try:
            max_steps = int(sys.argv[2])
        except ValueError:
            max_steps = 5000
    
    if len(sys.argv) > 3:
        distributed = sys.argv[3].lower() in ['true', 'dist', 'd', '1']
    
    if len(sys.argv) > 4:
        mixed_precision = sys.argv[4].lower() in ['true', 'mp', 'm', '1']
    
    # Create configuration
    config = TrainingConfig()
    config.batch_size = batch_size
    config.max_steps = max_steps
    config.distributed = distributed
    config.mixed_precision = mixed_precision
    config.max_epochs = 3  # Reduced for demo
    config.save_every = 500
    config.eval_every = 250
    
    print(f"🚀 Configuration: batch_size={batch_size}, max_steps={max_steps}, distributed={distributed}, mixed_precision={mixed_precision}")
    
    # Run training
    asyncio.run(run_large_scale_training(config))