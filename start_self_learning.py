"""
ARK Self-Learning Startup Script
================================
Quick start script for ARK with continuous learning capabilities.
"""

import subprocess
import sys
import time
import threading
from datetime import datetime

def print_banner():
    """Print startup banner."""
    
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    ARK SELF-LEARNING SYSTEM                 ║
║                  Continuous AI Improvement                  ║
╚══════════════════════════════════════════════════════════════╝

🧠 FEATURES:
  ✓ Continuous learning from conversations
  ✓ Automatic performance monitoring  
  ✓ Real-time capability enhancement
  ✓ User feedback integration
  ✓ Self-improving responses

🔄 LEARNING COMPONENTS:
  • Conversation Pattern Analysis
  • Performance Metrics Tracking
  • Knowledge Gap Detection
  • Training Data Generation
  • Capability Enhancement

🎯 RESULT: ARK gets smarter with every conversation!
"""
    
    print(banner)

def start_self_learning_ark():
    """Start ARK with self-learning capabilities."""
    
    print_banner()
    
    print("🚀 STARTING ARK SELF-LEARNING SYSTEM")
    print("=" * 45)
    
    try:
        # Test if all components are available
        print("🔍 Checking components...")
        
        # Check ARK brain
        try:
            from ark_intelligent_brain import ARKIntelligentBrain
            print("✅ ARK Intelligent Brain - Available")
        except ImportError:
            print("❌ ARK Intelligent Brain - Missing")
            return False
        
        # Check self-learning engine
        try:
            from ark_self_learning_engine import SelfLearningEngine
            print("✅ Self-Learning Engine - Available")
        except ImportError:
            print("❌ Self-Learning Engine - Missing")
            return False
        
        # Check continuous monitor
        try:
            from continuous_learning_monitor import ContinuousLearningMonitor
            print("✅ Continuous Learning Monitor - Available")
        except ImportError:
            print("❌ Continuous Learning Monitor - Missing")
        
        # Check enhanced bot
        try:
            from ark_enhanced_self_learning import ARKEnhancedBot
            print("✅ ARK Enhanced Bot - Available")
        except ImportError:
            print("❌ ARK Enhanced Bot - Missing")
            return False
        
        print(f"\n🎉 All components loaded successfully!")
        print(f"⏰ Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Start the enhanced ARK
        print(f"\n🔄 Initializing ARK Enhanced Bot...")
        
        # Import and start
        from ark_enhanced_self_learning import run_interactive_ark
        run_interactive_ark()
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting self-learning ARK: {e}")
        return False

def run_quick_demo():
    """Run a quick demonstration of self-learning."""
    
    print("🎯 QUICK SELF-LEARNING DEMO")
    print("=" * 30)
    
    try:
        from ark_enhanced_self_learning import demo_self_learning
        demo_self_learning()
        return True
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

def show_help():
    """Show help information."""
    
    help_text = """
📖 ARK SELF-LEARNING HELP
=========================

USAGE:
  python start_self_learning.py [mode]

MODES:
  interactive  - Start interactive ARK chat (default)
  demo        - Run quick demonstration
  help        - Show this help

FEATURES:
  🧠 Continuous Learning - ARK learns from every conversation
  📊 Performance Monitoring - Automatic quality assessment
  🔄 Real-time Improvement - Enhanced responses over time
  📝 Feedback Integration - User feedback improves ARK
  🎯 Adaptive Training - Custom training data generation

COMMANDS IN INTERACTIVE MODE:
  'stats'     - Show learning statistics
  'learn'     - Force learning update  
  'feedback [type]: [details]' - Provide feedback
  'quit'      - Exit ARK

FEEDBACK TYPES:
  positive    - Mark good responses
  negative    - Mark poor responses  
  suggestion  - Suggest improvements
  correction  - Correct mistakes

EXAMPLES:
  feedback positive: Great explanation, very helpful!
  feedback negative: Response was too technical
  feedback suggestion: Add more examples please
  feedback correction: The capital of France is Paris, not London

🎉 ARK gets smarter with every conversation!
"""
    
    print(help_text)

def main():
    """Main startup function."""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "demo":
            run_quick_demo()
            return
        elif mode == "help":
            show_help()
            return
        elif mode != "interactive":
            print(f"❌ Unknown mode: {mode}")
            print("Use 'python start_self_learning.py help' for usage information")
            return
    
    # Default to interactive mode
    success = start_self_learning_ark()
    
    if not success:
        print(f"\n💡 TIP: Try running the demo first:")
        print(f"   python start_self_learning.py demo")
        print(f"\n❓ For help:")
        print(f"   python start_self_learning.py help")

if __name__ == "__main__":
    main()