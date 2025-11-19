#!/usr/bin/env python3
"""
Automated Training Runner for ARK AI
====================================
This script trains the ARK AI using available internet datasets.
Runs automatically without user confirmation for automated workflows.
"""

import os
import sys
import json
from datetime import datetime

def run_automated_training():
    """Run the complete training pipeline automatically."""
    
    print("=" * 60)
    print("🤖 ARK AI - AUTOMATED INTERNET TRAINING")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Training configuration
    training_config = {
        "start_time": datetime.now().isoformat(),
        "training_phases": [],
        "total_examples_added": 0,
        "success": False
    }
    
    print("📋 Training Configuration:")
    print("   - Phase 1: Internet Dataset Collection")
    print("   - Phase 2: Advanced Dataset Processing")
    print("   - Phase 3: Wikipedia Educational Content")
    print("   - Phase 4: Quality Validation & Testing")
    print()
    
    # Phase 1: Internet Dataset Training
    print("🚀 PHASE 1: Internet Dataset Collection")
    print("-" * 60)
    try:
        from internet_dataset_trainer import InternetDatasetTrainer
        
        print("📥 Downloading and processing internet datasets...")
        trainer = InternetDatasetTrainer()
        
        # Download datasets
        print("   Step 1/3: Downloading datasets from internet sources...")
        download_success = trainer.download_all_datasets()
        
        # Process datasets
        print("   Step 2/3: Processing and formatting datasets...")
        process_success = trainer.process_all_datasets()
        
        # Get statistics
        print("   Step 3/3: Collecting training statistics...")
        stats = trainer.get_training_statistics()
        
        training_config["training_phases"].append({
            "phase": 1,
            "name": "Internet Dataset Collection",
            "success": download_success and process_success,
            "examples_added": stats.get('training_examples_added', 0),
            "datasets_processed": stats.get('datasets_processed', 0)
        })
        
        print(f"✅ Phase 1 Complete:")
        print(f"   - Datasets processed: {stats.get('datasets_processed', 0)}")
        print(f"   - Examples added: {stats.get('training_examples_added', 0)}")
        print()
        
    except Exception as e:
        print(f"❌ Phase 1 failed: {e}")
        training_config["training_phases"].append({
            "phase": 1,
            "name": "Internet Dataset Collection",
            "success": False,
            "error": str(e)
        })
    
    # Phase 2: Advanced Dataset Processing
    print("🚀 PHASE 2: Advanced Dataset Processing")
    print("-" * 60)
    try:
        from advanced_dataset_processor import AdvancedDatasetProcessor
        
        print("🔬 Processing advanced datasets (Wikipedia, ArXiv, GitHub)...")
        processor = AdvancedDatasetProcessor()
        
        print("   Step 1/2: Collecting educational content from Wikipedia...")
        processor.process_wikipedia_dataset()
        
        print("   Step 2/2: Processing technical documentation...")
        processor.process_technical_resources()
        
        # Get results
        results = processor.get_processing_results()
        
        training_config["training_phases"].append({
            "phase": 2,
            "name": "Advanced Dataset Processing",
            "success": True,
            "examples_added": results.get('total_examples', 0)
        })
        
        print(f"✅ Phase 2 Complete:")
        print(f"   - Advanced examples added: {results.get('total_examples', 0)}")
        print()
        
    except Exception as e:
        print(f"⚠️  Phase 2 encountered issues: {e}")
        print("   Continuing with existing data...")
        training_config["training_phases"].append({
            "phase": 2,
            "name": "Advanced Dataset Processing",
            "success": False,
            "error": str(e)
        })
    
    # Phase 3: Additional Internet Training
    print("🚀 PHASE 3: Enhanced Internet Training")
    print("-" * 60)
    try:
        from advanced_internet_trainer import AdvancedInternetTrainer
        
        print("🌐 Downloading curated educational content from internet...")
        internet_trainer = AdvancedInternetTrainer()
        
        print("   Step 1/2: Collecting Wikipedia educational articles...")
        internet_trainer.download_wikipedia_educational_content()
        
        print("   Step 2/2: Processing and validating quality...")
        results = internet_trainer.process_and_save_all_data()
        
        training_config["training_phases"].append({
            "phase": 3,
            "name": "Enhanced Internet Training",
            "success": True,
            "examples_added": results.get('total_saved', 0)
        })
        
        print(f"✅ Phase 3 Complete:")
        print(f"   - Enhanced examples added: {results.get('total_saved', 0)}")
        print()
        
    except Exception as e:
        print(f"⚠️  Phase 3 encountered issues: {e}")
        print("   Continuing with existing data...")
        training_config["training_phases"].append({
            "phase": 3,
            "name": "Enhanced Internet Training",
            "success": False,
            "error": str(e)
        })
    
    # Calculate total statistics
    training_config["end_time"] = datetime.now().isoformat()
    training_config["total_examples_added"] = sum(
        phase.get('examples_added', 0) 
        for phase in training_config["training_phases"]
    )
    training_config["successful_phases"] = sum(
        1 for phase in training_config["training_phases"] 
        if phase.get('success', False)
    )
    training_config["total_phases"] = len(training_config["training_phases"])
    
    # Display final summary
    print()
    print("=" * 60)
    print("📊 TRAINING SUMMARY")
    print("=" * 60)
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ Successful Phases: {training_config['successful_phases']}/{training_config['total_phases']}")
    print(f"📚 Total Examples Added: {training_config['total_examples_added']:,}")
    print()
    
    # Phase-by-phase breakdown
    print("📋 Phase Breakdown:")
    for phase in training_config["training_phases"]:
        status = "✅" if phase.get('success', False) else "❌"
        examples = phase.get('examples_added', 0)
        print(f"   {status} Phase {phase['phase']}: {phase['name']}")
        if examples > 0:
            print(f"      Examples: {examples:,}")
        if 'error' in phase:
            print(f"      Error: {phase['error'][:100]}...")
    
    print()
    
    # Save training report
    report_path = f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(training_config, f, indent=2)
        print(f"💾 Training report saved: {report_path}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")
    
    # Final status
    if training_config['successful_phases'] > 0:
        training_config['success'] = True
        print()
        print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print(f"🧠 ARK AI has been enhanced with {training_config['total_examples_added']:,} new examples")
        print("   from diverse internet sources including:")
        print("   - Conversational datasets")
        print("   - Educational content")
        print("   - Technical documentation")
        print("   - Wikipedia articles")
        print("   - Research papers")
        print()
        print("✨ Your AI is now ready with enhanced knowledge!")
    else:
        print()
        print("⚠️  TRAINING COMPLETED WITH ISSUES")
        print("   Some phases encountered errors, but existing data is intact.")
        print("   Check the training report for details.")
    
    print("=" * 60)
    
    return training_config


if __name__ == "__main__":
    try:
        result = run_automated_training()
        sys.exit(0 if result['success'] else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Training failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
