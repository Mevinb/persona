"""
ARK Enterprise AI Training System
================================
Complete large-scale AI training system combining data processing and model training
used by leading AI companies. Includes distributed processing, advanced optimization,
and production-ready monitoring.
"""

import asyncio
import torch
import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

# Import ARK components
from ark_large_scale_trainer import ARKLargeScaleTrainer, TrainingConfig, run_large_scale_training
from ark_data_pipeline import StreamingDataProcessor, DataProcessingConfig, process_large_dataset, LargeScaleDataLoader
from ark_advanced_intelligence import ARKAdvancedIntelligence


class ARKEnterpriseTrainingSystem:
    """Complete enterprise training system orchestrator."""
    
    def __init__(self):
        self.training_config = None
        self.processing_config = None
        self.system_stats = {
            "start_time": datetime.now(),
            "data_processing_time": 0,
            "training_time": 0,
            "total_samples_processed": 0,
            "total_training_steps": 0,
            "peak_memory_mb": 0,
            "system_efficiency": 0.0
        }
        
        # Setup logging
        self._setup_enterprise_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_enterprise_logging(self):
        """Setup enterprise-grade logging."""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"ark_enterprise_training_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def create_data_processing_config(
        self,
        sources: List[str],
        output_dir: str = "data/enterprise_processed",
        batch_size: int = 2000,
        max_sequence_length: int = 1024,
        quality_threshold: float = 0.7,
        use_compression: bool = True
    ) -> DataProcessingConfig:
        """Create optimized data processing configuration."""
        
        config = DataProcessingConfig()
        config.input_sources = sources
        config.output_dir = output_dir
        config.batch_size = batch_size
        config.max_sequence_length = max_sequence_length
        config.min_quality_score = quality_threshold
        config.remove_duplicates = True
        config.remove_repetitive = True
        config.compression = "lz4" if use_compression else "none"
        config.output_format = "parquet"
        config.num_workers = min(os.cpu_count(), 16)
        config.log_every = 5000
        config.save_every = 50000
        
        return config
    
    def create_training_config(
        self,
        processed_data_dir: str,
        model_name: str = "microsoft/DialoGPT-medium",
        batch_size: int = 32,
        max_steps: int = 50000,
        learning_rate: float = 5e-5,
        use_distributed: bool = False,
        use_mixed_precision: bool = True,
        checkpoint_dir: str = "checkpoints/enterprise"
    ) -> TrainingConfig:
        """Create optimized training configuration."""
        
        config = TrainingConfig()
        config.model_name = model_name
        config.dataset_path = processed_data_dir
        config.batch_size = batch_size
        config.max_steps = max_steps
        config.learning_rate = learning_rate
        config.distributed = use_distributed
        config.mixed_precision = use_mixed_precision
        config.checkpoint_dir = checkpoint_dir
        
        # Enterprise optimizations
        config.gradient_accumulation_steps = 8
        config.gradient_clipping = 1.0
        config.warmup_steps = min(2000, max_steps // 10)
        config.save_every = min(2000, max_steps // 25)
        config.eval_every = min(1000, max_steps // 50)
        config.log_every = 50
        config.gradient_checkpointing = True
        config.scheduler = "linear"
        config.optimizer = "adamw"
        config.weight_decay = 0.01
        
        return config
    
    async def run_data_processing_phase(self, sources: List[str], config: Optional[DataProcessingConfig] = None) -> str:
        """Run enterprise data processing phase."""
        
        self.logger.info("🔄 PHASE 1: ENTERPRISE DATA PROCESSING")
        self.logger.info("=" * 50)
        
        start_time = time.time()
        
        if config is None:
            config = self.create_data_processing_config(sources)
        
        self.processing_config = config
        
        # Log processing configuration
        self.logger.info(f"📊 Processing {len(sources)} data sources")
        self.logger.info(f"📁 Output directory: {config.output_dir}")
        self.logger.info(f"🔢 Batch size: {config.batch_size}")
        self.logger.info(f"📏 Max sequence length: {config.max_sequence_length}")
        self.logger.info(f"⚡ Workers: {config.num_workers}")
        self.logger.info(f"🎯 Quality threshold: {config.min_quality_score}")
        
        # Initialize processor
        processor = StreamingDataProcessor(config)
        
        # Process data
        try:
            summary = await processor.process_data_stream(sources)
            
            processing_time = time.time() - start_time
            self.system_stats["data_processing_time"] = processing_time
            self.system_stats["total_samples_processed"] = summary["total_texts_processed"]
            
            self.logger.info(f"✅ Data processing completed in {processing_time/60:.1f} minutes")
            self.logger.info(f"📊 Processed {summary['total_texts_processed']} samples")
            self.logger.info(f"💾 Created {summary['total_batches']} training batches")
            
            return config.output_dir
            
        except Exception as e:
            self.logger.error(f"❌ Data processing failed: {str(e)}")
            raise
    
    async def run_training_phase(self, processed_data_dir: str, config: Optional[TrainingConfig] = None) -> Dict:
        """Run enterprise training phase."""
        
        self.logger.info("🚀 PHASE 2: ENTERPRISE MODEL TRAINING")
        self.logger.info("=" * 50)
        
        start_time = time.time()
        
        if config is None:
            config = self.create_training_config(processed_data_dir)
        
        self.training_config = config
        
        # Log training configuration
        self.logger.info(f"🤖 Model: {config.model_name}")
        self.logger.info(f"📊 Dataset: {config.dataset_path}")
        self.logger.info(f"🔢 Batch size: {config.batch_size}")
        self.logger.info(f"📈 Max steps: {config.max_steps}")
        self.logger.info(f"⚡ Learning rate: {config.learning_rate}")
        self.logger.info(f"🌐 Distributed: {config.distributed}")
        self.logger.info(f"💾 Mixed precision: {config.mixed_precision}")
        
        # Initialize trainer
        trainer = ARKLargeScaleTrainer(config)
        
        try:
            # Run training
            await trainer.train()
            
            training_time = time.time() - start_time
            self.system_stats["training_time"] = training_time
            self.system_stats["total_training_steps"] = trainer.current_step
            self.system_stats["peak_memory_mb"] = trainer.memory_tracker["peak_memory_mb"]
            
            self.logger.info(f"✅ Training completed in {training_time/3600:.1f} hours")
            self.logger.info(f"📈 Completed {trainer.current_step} training steps")
            self.logger.info(f"🏆 Best validation loss: {trainer.best_val_loss:.4f}")
            self.logger.info(f"💾 Peak memory: {trainer.memory_tracker['peak_memory_mb']:.0f}MB")
            
            return {
                "trainer": trainer,
                "final_step": trainer.current_step,
                "best_val_loss": trainer.best_val_loss,
                "training_time_hours": training_time / 3600,
                "checkpoint_dir": config.checkpoint_dir
            }
            
        except Exception as e:
            self.logger.error(f"❌ Training failed: {str(e)}")
            raise
    
    async def run_complete_pipeline(
        self,
        data_sources: List[str],
        output_model_dir: str = "models/ark_enterprise",
        data_config: Optional[DataProcessingConfig] = None,
        training_config: Optional[TrainingConfig] = None,
        skip_data_processing: bool = False,
        processed_data_dir: Optional[str] = None
    ) -> Dict:
        """Run complete enterprise AI training pipeline."""
        
        self.logger.info("🏢 ARK ENTERPRISE AI TRAINING SYSTEM")
        self.logger.info("=" * 60)
        self.logger.info("🎯 Running complete training pipeline...")
        self.logger.info(f"📅 Started: {self.system_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_start_time = time.time()
        
        try:
            # Phase 1: Data Processing
            if not skip_data_processing:
                processed_data_dir = await self.run_data_processing_phase(data_sources, data_config)
            else:
                if not processed_data_dir or not os.path.exists(processed_data_dir):
                    raise ValueError("Processed data directory not found. Cannot skip data processing.")
                self.logger.info(f"⏭️  Skipping data processing, using: {processed_data_dir}")
            
            # Phase 2: Model Training
            training_results = await self.run_training_phase(processed_data_dir, training_config)
            
            # Calculate system efficiency
            total_time = time.time() - total_start_time
            samples_per_second = self.system_stats["total_samples_processed"] / max(total_time, 1)
            self.system_stats["system_efficiency"] = samples_per_second
            
            # Create final model directory
            os.makedirs(output_model_dir, exist_ok=True)
            
            # Copy best model to output directory
            if os.path.exists(os.path.join(training_results["checkpoint_dir"], "best_model.pt")):
                import shutil
                shutil.copy(
                    os.path.join(training_results["checkpoint_dir"], "best_model.pt"),
                    os.path.join(output_model_dir, "final_model.pt")
                )
                self.logger.info(f"💾 Final model saved to: {output_model_dir}")
            
            # Generate comprehensive report
            final_report = self._generate_training_report(training_results, total_time)
            
            # Save report
            report_path = os.path.join(output_model_dir, "training_report.json")
            with open(report_path, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            self.logger.info(f"📋 Training report saved to: {report_path}")
            
            # Final summary
            self.logger.info("🎉 ENTERPRISE TRAINING COMPLETED SUCCESSFULLY!")
            self.logger.info("=" * 60)
            self.logger.info(f"⏱️  Total time: {total_time/3600:.2f} hours")
            self.logger.info(f"📊 Samples processed: {self.system_stats['total_samples_processed']:,}")
            self.logger.info(f"📈 Training steps: {self.system_stats['total_training_steps']:,}")
            self.logger.info(f"🚀 System efficiency: {self.system_stats['system_efficiency']:.1f} samples/sec")
            self.logger.info(f"🏆 Final model: {output_model_dir}")
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"💥 ENTERPRISE TRAINING FAILED: {str(e)}")
            raise
    
    def _generate_training_report(self, training_results: Dict, total_time: float) -> Dict:
        """Generate comprehensive training report."""
        
        report = {
            "system_info": {
                "start_time": self.system_stats["start_time"].isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_duration_hours": total_time / 3600,
                "system_efficiency_samples_per_sec": self.system_stats["system_efficiency"],
                "peak_memory_mb": self.system_stats["peak_memory_mb"]
            },
            "data_processing": {
                "processing_time_minutes": self.system_stats["data_processing_time"] / 60,
                "total_samples_processed": self.system_stats["total_samples_processed"],
                "processing_config": self.processing_config.__dict__ if self.processing_config else None
            },
            "training": {
                "training_time_hours": self.system_stats["training_time"] / 3600,
                "total_steps": self.system_stats["total_training_steps"],
                "best_validation_loss": training_results["best_val_loss"],
                "final_checkpoint": training_results["checkpoint_dir"],
                "training_config": self.training_config.__dict__ if self.training_config else None
            },
            "performance_metrics": {
                "samples_per_hour": (self.system_stats["total_samples_processed"] / max(total_time / 3600, 1)),
                "steps_per_hour": (self.system_stats["total_training_steps"] / max(self.system_stats["training_time"] / 3600, 1)),
                "training_efficiency": (self.system_stats["total_training_steps"] / max(self.system_stats["training_time"], 1)),
                "overall_throughput": self.system_stats["system_efficiency"]
            },
            "resource_utilization": {
                "peak_memory_usage_mb": self.system_stats["peak_memory_mb"],
                "data_processing_memory_efficiency": "optimized",
                "training_memory_efficiency": "mixed_precision_enabled",
                "cpu_utilization": "multi_worker_processing"
            }
        }
        
        return report


# Preset configurations for different use cases
class EnterprisePresets:
    """Predefined configurations for common enterprise scenarios."""
    
    @staticmethod
    def research_development() -> tuple[DataProcessingConfig, TrainingConfig]:
        """Configuration for R&D experimentation."""
        data_config = DataProcessingConfig()
        data_config.batch_size = 1000
        data_config.max_sequence_length = 512
        data_config.min_quality_score = 0.6
        data_config.output_format = "parquet"
        
        training_config = TrainingConfig()
        training_config.batch_size = 16
        training_config.max_steps = 10000
        training_config.learning_rate = 3e-4
        training_config.mixed_precision = True
        
        return data_config, training_config
    
    @staticmethod
    def production_deployment() -> tuple[DataProcessingConfig, TrainingConfig]:
        """Configuration for production model deployment."""
        data_config = DataProcessingConfig()
        data_config.batch_size = 5000
        data_config.max_sequence_length = 1024
        data_config.min_quality_score = 0.8
        data_config.compression = "lz4"
        data_config.remove_duplicates = True
        
        training_config = TrainingConfig()
        training_config.batch_size = 64
        training_config.max_steps = 100000
        training_config.learning_rate = 1e-4
        training_config.gradient_accumulation_steps = 16
        training_config.mixed_precision = True
        training_config.gradient_checkpointing = True
        
        return data_config, training_config
    
    @staticmethod
    def large_scale_enterprise() -> tuple[DataProcessingConfig, TrainingConfig]:
        """Configuration for large-scale enterprise deployment."""
        data_config = DataProcessingConfig()
        data_config.batch_size = 10000
        data_config.max_sequence_length = 2048
        data_config.min_quality_score = 0.9
        data_config.compression = "lz4"
        data_config.num_workers = 32
        
        training_config = TrainingConfig()
        training_config.batch_size = 128
        training_config.max_steps = 500000
        training_config.learning_rate = 5e-5
        training_config.gradient_accumulation_steps = 32
        training_config.distributed = True
        training_config.mixed_precision = True
        training_config.use_wandb = True
        
        return data_config, training_config


async def run_enterprise_training(
    data_sources: List[str],
    preset: str = "research",  # research, production, enterprise
    output_dir: str = "models/ark_enterprise",
    custom_data_config: Optional[DataProcessingConfig] = None,
    custom_training_config: Optional[TrainingConfig] = None
):
    """Run enterprise training with preset or custom configuration."""
    
    # Initialize system
    system = ARKEnterpriseTrainingSystem()
    
    # Get preset configuration
    if preset == "research":
        data_config, training_config = EnterprisePresets.research_development()
    elif preset == "production":
        data_config, training_config = EnterprisePresets.production_deployment()
    elif preset == "enterprise":
        data_config, training_config = EnterprisePresets.large_scale_enterprise()
    else:
        data_config, training_config = EnterprisePresets.research_development()
    
    # Use custom configs if provided
    if custom_data_config:
        data_config = custom_data_config
    if custom_training_config:
        training_config = custom_training_config
    
    # Run complete pipeline
    results = await system.run_complete_pipeline(
        data_sources=data_sources,
        output_model_dir=output_dir,
        data_config=data_config,
        training_config=training_config
    )
    
    return results


if __name__ == "__main__":
    # Example usage with command line interface
    
    # Default data sources - add your own here
    default_sources = [
        "hf:wikitext",
        "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
    ]
    
    # Parse command line arguments
    preset = "research"  # Default preset
    batch_size = None
    max_steps = None
    
    if len(sys.argv) > 1:
        preset = sys.argv[1].lower()
        if preset not in ["research", "production", "enterprise"]:
            preset = "research"
    
    if len(sys.argv) > 2:
        try:
            batch_size = int(sys.argv[2])
        except ValueError:
            pass
    
    if len(sys.argv) > 3:
        try:
            max_steps = int(sys.argv[3])
        except ValueError:
            pass
    
    print("🏢 ARK ENTERPRISE AI TRAINING SYSTEM")
    print("=" * 50)
    print(f"🎯 Preset: {preset}")
    print(f"📊 Data sources: {len(default_sources)}")
    if batch_size:
        print(f"🔢 Custom batch size: {batch_size}")
    if max_steps:
        print(f"📈 Custom max steps: {max_steps}")
    print("=" * 50)
    
    # Override configs if specified
    custom_training_config = None
    if batch_size or max_steps:
        custom_training_config = TrainingConfig()
        if batch_size:
            custom_training_config.batch_size = batch_size
        if max_steps:
            custom_training_config.max_steps = max_steps
    
    # Run training
    asyncio.run(run_enterprise_training(
        data_sources=default_sources,
        preset=preset,
        custom_training_config=custom_training_config
    ))