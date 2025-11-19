"""
Master Internet Training Script
===============================
Orchestrates the complete internet dataset training pipeline for ARK.
Combines multiple data sources for comprehensive knowledge enhancement.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List
import sqlite3
import json

class MasterInternetTrainer:
    """Master controller for internet-based ARK training."""
    
    def __init__(self):
        self.db_path = "data/ark_complete_training.db"
        self.training_log_path = "data/internet_training_log.json"
        
        # Training phases
        self.phases = [
            {
                "name": "Basic Internet Datasets",
                "module": "internet_dataset_trainer",
                "function": "run_internet_training",
                "description": "Download and process general internet datasets"
            },
            {
                "name": "Specialized Knowledge",
                "module": "advanced_dataset_processor", 
                "function": "run_advanced_dataset_processing",
                "description": "Process Wikipedia, ArXiv, GitHub, and technical resources"
            }
        ]
        
        self.training_results = {
            "start_time": datetime.now().isoformat(),
            "phases_completed": 0,
            "total_examples_added": 0,
            "training_phases": []
        }
    
    def run_complete_internet_training(self):
        """Run the complete internet training pipeline."""
        
        print("🌐 MASTER ARK INTERNET TRAINING")
        print("=" * 45)
        print(f"⏰ Training started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Training phases: {len(self.phases)}")
        
        # Check initial database state
        initial_count = self._get_training_count()
        print(f"📚 Initial training examples: {initial_count}")
        
        # Execute training phases
        for i, phase in enumerate(self.phases, 1):
            print(f"\n🚀 PHASE {i}: {phase['name']}")
            print("=" * 40)
            print(f"📝 {phase['description']}")
            
            phase_start = datetime.now()
            phase_success = self._execute_phase(phase)
            phase_duration = (datetime.now() - phase_start).total_seconds()
            
            # Log phase results
            phase_result = {
                "phase_number": i,
                "name": phase['name'],
                "success": phase_success,
                "duration_seconds": phase_duration,
                "timestamp": datetime.now().isoformat()
            }
            
            if phase_success:
                print(f"✅ Phase {i} completed successfully ({phase_duration:.1f}s)")
                self.training_results["phases_completed"] += 1
            else:
                print(f"❌ Phase {i} failed ({phase_duration:.1f}s)")
            
            self.training_results["training_phases"].append(phase_result)
            
            # Brief pause between phases
            if i < len(self.phases):
                print("⏳ Preparing next phase...")
                time.sleep(2)
        
        # Final results
        final_count = self._get_training_count()
        examples_added = final_count - initial_count
        
        self.training_results.update({
            "end_time": datetime.now().isoformat(),
            "initial_examples": initial_count,
            "final_examples": final_count,
            "total_examples_added": examples_added,
            "training_success": self.training_results["phases_completed"] == len(self.phases)
        })
        
        # Save training log
        self._save_training_log()
        
        # Display final summary
        self._display_training_summary()
        
        # Test enhanced ARK
        if examples_added > 0:
            self._test_enhanced_ark()
        
        return self.training_results["training_success"]
    
    def _execute_phase(self, phase: Dict) -> bool:
        """Execute a single training phase."""
        
        try:
            # Dynamic import and execution
            module_name = phase["module"]
            function_name = phase["function"]
            
            # Add current directory to path
            if '.' not in sys.path:
                sys.path.append('.')
            
            # Import module
            module = __import__(module_name)
            
            # Get function
            if hasattr(module, function_name):
                function = getattr(module, function_name)
                result = function()
                return result
            else:
                print(f"❌ Function {function_name} not found in {module_name}")
                return False
                
        except ImportError as e:
            print(f"❌ Could not import {phase['module']}: {e}")
            return False
        except Exception as e:
            print(f"❌ Phase execution error: {e}")
            return False
    
    def _get_training_count(self) -> int:
        """Get current number of training examples."""
        
        try:
            if not os.path.exists(self.db_path):
                return 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM training_data")
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            print(f"⚠️  Error counting training examples: {e}")
            return 0
    
    def _save_training_log(self):
        """Save training log for future reference."""
        
        try:
            os.makedirs(os.path.dirname(self.training_log_path), exist_ok=True)
            
            with open(self.training_log_path, 'w') as f:
                json.dump(self.training_results, f, indent=2)
            
            print(f"💾 Training log saved: {self.training_log_path}")
            
        except Exception as e:
            print(f"⚠️  Could not save training log: {e}")
    
    def _display_training_summary(self):
        """Display comprehensive training summary."""
        
        print(f"\n📊 INTERNET TRAINING SUMMARY")
        print("=" * 35)
        
        results = self.training_results
        
        # Overall statistics
        print(f"⏰ Training Duration:")
        start_time = datetime.fromisoformat(results['start_time'])
        end_time = datetime.fromisoformat(results['end_time'])
        duration = end_time - start_time
        print(f"   Total time: {duration.total_seconds()/60:.1f} minutes")
        
        print(f"\n📚 Data Statistics:")
        print(f"   Initial examples: {results['initial_examples']:,}")
        print(f"   Final examples: {results['final_examples']:,}")
        print(f"   Examples added: {results['total_examples_added']:,}")
        
        print(f"\n🎯 Training Phases:")
        print(f"   Completed: {results['phases_completed']}/{len(self.phases)}")
        
        for phase in results['training_phases']:
            status = "✅" if phase['success'] else "❌"
            print(f"   {status} {phase['name']} ({phase['duration_seconds']:.1f}s)")
        
        # Success assessment
        success_rate = (results['phases_completed'] / len(self.phases)) * 100
        print(f"\n🏆 Overall Success: {success_rate:.1f}%")
        
        if results['training_success']:
            print("🎉 All training phases completed successfully!")
        else:
            print("⚠️  Some training phases failed")
        
        # Database analysis
        self._analyze_training_database()
    
    def _analyze_training_database(self):
        """Analyze the training database composition."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Category distribution
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM training_data 
                GROUP BY category 
                ORDER BY count DESC
                LIMIT 10
            """)
            
            categories = cursor.fetchall()
            
            if categories:
                print(f"\n📂 Top Training Categories:")
                for category, count in categories:
                    percentage = (count / self.training_results['final_examples']) * 100
                    print(f"   {category}: {count:,} ({percentage:.1f}%)")
            
            # Quality score analysis
            cursor.execute("""
                SELECT AVG(quality_score) as avg_quality, 
                       MIN(quality_score) as min_quality,
                       MAX(quality_score) as max_quality
                FROM training_data
            """)
            
            quality_stats = cursor.fetchone()
            if quality_stats and quality_stats[0]:
                print(f"\n⭐ Quality Metrics:")
                print(f"   Average quality: {quality_stats[0]:.3f}")
                print(f"   Quality range: {quality_stats[1]:.3f} - {quality_stats[2]:.3f}")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Database analysis error: {e}")
    
    def _test_enhanced_ark(self):
        """Test ARK with enhanced training."""
        
        print(f"\n🧪 TESTING ENHANCED ARK")
        print("-" * 25)
        
        # Test questions covering different domains
        test_questions = [
            "What is machine learning and how does it work?",
            "Explain quantum computing principles",
            "How do neural networks process information?",
            "What are the latest developments in AI research?",
            "Describe deep learning architectures",
            "What programming resources are available for beginners?",
            "How do public APIs work for web development?",
            "What is the difference between supervised and unsupervised learning?"
        ]
        
        try:
            from ark_intelligent_brain import ARKIntelligentBrain
            ark = ARKIntelligentBrain()
            
            print(f"Testing {len(test_questions)} diverse questions...")
            
            enhanced_responses = 0
            total_response_length = 0
            
            for i, question in enumerate(test_questions, 1):
                try:
                    response = ark.process_input(question)
                    response_length = len(response)
                    total_response_length += response_length
                    
                    # Check if response seems enhanced
                    if response_length > 300:
                        enhanced_responses += 1
                        quality = "Enhanced"
                    elif response_length > 150:
                        quality = "Good"
                    else:
                        quality = "Basic"
                    
                    print(f"   {i}. {quality} response ({response_length} chars)")
                    
                except Exception as e:
                    print(f"   {i}. Error: {e}")
            
            # Summary
            avg_response_length = total_response_length / len(test_questions)
            enhancement_rate = (enhanced_responses / len(test_questions)) * 100
            
            print(f"\n📈 Test Results:")
            print(f"   Average response length: {avg_response_length:.0f} characters")
            print(f"   Enhanced responses: {enhancement_rate:.1f}%")
            
            if enhancement_rate >= 70:
                print("🎉 ARK shows significant improvement from internet training!")
            elif enhancement_rate >= 40:
                print("✅ ARK shows moderate improvement from internet training")
            else:
                print("⚠️  Limited improvement detected - may need more training")
        
        except Exception as e:
            print(f"❌ Testing error: {e}")
    
    def get_training_status(self) -> Dict:
        """Get current training status."""
        return self.training_results.copy()


def main():
    """Main execution function."""
    
    print("🌐 ARK MASTER INTERNET TRAINER")
    print("=" * 35)
    print("🎯 This will enhance ARK with knowledge from multiple internet sources")
    print("📊 Including: Wikipedia, ArXiv, GitHub, APIs, and programming resources")
    print("⏰ Estimated time: 10-20 minutes")
    
    # Confirm execution
    confirm = input("\n🤖 Proceed with internet training? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        print("\n🚀 Starting internet training...")
        
        trainer = MasterInternetTrainer()
        success = trainer.run_complete_internet_training()
        
        if success:
            print("\n🎉 Internet training completed successfully!")
            print("🧠 ARK now has enhanced knowledge from internet sources")
        else:
            print("\n⚠️  Internet training completed with some issues")
            print("💡 Check the training log for details")
        
        # Show final status
        status = trainer.get_training_status()
        print(f"\n📊 Final Status:")
        print(f"   Examples added: {status['total_examples_added']:,}")
        print(f"   Success rate: {(status['phases_completed']/len(trainer.phases))*100:.1f}%")
        
    else:
        print("❌ Internet training cancelled")


if __name__ == "__main__":
    main()