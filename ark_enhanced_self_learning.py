"""
ARK Enhanced with Self-Learning
===============================
Enhanced ARK that automatically learns and improves from every interaction.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add current directory for imports
sys.path.append(os.path.dirname(__file__))

class ARKEnhancedBot:
    """ARK with integrated self-learning capabilities."""
    
    def __init__(self):
        print("🧠 Initializing ARK Enhanced with Self-Learning...")
        
        # Import and initialize ARK brain
        try:
            from ark_intelligent_brain import ARKIntelligentBrain
            self.brain = ARKIntelligentBrain()
            print("✅ ARK Brain loaded successfully")
        except ImportError as e:
            print(f"❌ Error loading ARK Brain: {e}")
            self.brain = None
        
        # Initialize self-learning engine
        try:
            from ark_self_learning_engine import SelfLearningEngine
            self.learning_engine = SelfLearningEngine()
            print("✅ Self-Learning Engine loaded successfully")
        except ImportError as e:
            print(f"❌ Error loading Learning Engine: {e}")
            self.learning_engine = None
        
        # Initialize continuous monitor
        try:
            from continuous_learning_monitor import ContinuousLearningMonitor
            self.monitor = ContinuousLearningMonitor()
            self.monitor.start_monitoring()
            print("✅ Continuous Learning Monitor started")
        except ImportError as e:
            print(f"⚠️  Continuous Monitor not available: {e}")
            self.monitor = None
        
        # Conversation tracking
        self.conversation_count = 0
        self.session_start_time = datetime.now()
        
        print("\n🎉 ARK Enhanced is ready!")
        print("🔄 Self-learning is ACTIVE")
        print("📊 Continuous improvement enabled")
        print("🧠 Every conversation makes ARK smarter!\n")
    
    def chat(self, user_input: str) -> str:
        """Enhanced chat with automatic learning."""
        
        if not self.brain:
            return "❌ ARK brain not available"
        
        try:
            # Process input through ARK brain
            response = self.brain.process_input(user_input)
            
            # Log for learning if available
            if self.learning_engine:
                context = {
                    "session_time": (datetime.now() - self.session_start_time).total_seconds(),
                    "conversation_number": self.conversation_count + 1,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.learning_engine.log_conversation(user_input, response, context)
            
            # Increment conversation count
            self.conversation_count += 1
            
            # Provide learning feedback every 5 conversations
            if self.conversation_count % 5 == 0 and self.learning_engine:
                print(f"\n🧠 Learning Update: Processed {self.conversation_count} conversations this session")
                status = self.learning_engine.get_learning_status()
                print(f"📊 Total learning sessions: {status.get('learning_sessions', 0)}")
                print(f"📚 Training examples added: {status.get('training_examples_added', 0)}")
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error processing request: {e}"
            print(error_msg)
            return error_msg
    
    def provide_feedback(self, feedback_type: str, feedback_details: str) -> str:
        """Provide feedback to improve ARK."""
        
        if not self.learning_engine:
            return "⚠️  Learning engine not available"
        
        try:
            self.learning_engine.process_user_feedback(feedback_type, feedback_details)
            
            # Trigger immediate learning if negative feedback
            if feedback_type == "negative" and self.learning_engine:
                print("🔄 Processing negative feedback - triggering learning cycle...")
                self.learning_engine.force_learning_cycle()
            
            return f"✅ Thank you for the feedback! This will help me improve."
            
        except Exception as e:
            return f"❌ Error processing feedback: {e}"
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics."""
        
        stats = {
            "session_conversations": self.conversation_count,
            "session_duration_minutes": (datetime.now() - self.session_start_time).total_seconds() / 60,
            "learning_engine_available": self.learning_engine is not None,
            "monitor_active": self.monitor is not None and self.monitor.monitoring_active if self.monitor else False
        }
        
        if self.learning_engine:
            learning_stats = self.learning_engine.get_learning_status()
            stats.update(learning_stats)
        
        if self.monitor:
            monitor_stats = self.monitor.get_monitoring_status()
            stats.update(monitor_stats)
        
        return stats
    
    def force_learning_update(self) -> str:
        """Manually trigger learning update."""
        
        if not self.learning_engine:
            return "⚠️  Learning engine not available"
        
        try:
            print("🔄 Forcing learning cycle...")
            self.learning_engine.force_learning_cycle()
            return "✅ Learning cycle completed!"
            
        except Exception as e:
            return f"❌ Error during learning cycle: {e}"
    
    def show_learning_progress(self):
        """Display learning progress and statistics."""
        
        print("\n📊 ARK LEARNING PROGRESS REPORT")
        print("=" * 40)
        
        stats = self.get_learning_stats()
        
        print(f"🎯 Current Session:")
        print(f"   Conversations: {stats.get('session_conversations', 0)}")
        print(f"   Duration: {stats.get('session_duration_minutes', 0):.1f} minutes")
        
        print(f"\n🧠 Learning Engine:")
        print(f"   Status: {'Active' if stats.get('learning_engine_available') else 'Inactive'}")
        print(f"   Learning Sessions: {stats.get('learning_sessions', 0)}")
        print(f"   New Patterns: {stats.get('new_patterns_learned', 0)}")
        print(f"   Training Examples: {stats.get('training_examples_added', 0)}")
        
        print(f"\n🔄 Continuous Monitor:")
        print(f"   Status: {'Active' if stats.get('monitor_active') else 'Inactive'}")
        print(f"   Learning Interval: {stats.get('learning_interval', 0)} seconds")
        
        if stats.get('capability_improvements'):
            print(f"\n🎉 Recent Improvements:")
            for improvement in stats.get('capability_improvements', [])[-3:]:
                print(f"   • {improvement.get('type', 'Unknown')}: {improvement.get('category', 'General')}")
    
    def shutdown(self):
        """Shutdown ARK and learning systems."""
        
        print("\n🛑 Shutting down ARK Enhanced...")
        
        if self.monitor:
            self.monitor.stop_monitoring()
            print("✅ Learning monitor stopped")
        
        if self.learning_engine:
            self.learning_engine.stop_learning()
            print("✅ Learning engine stopped")
        
        # Show final stats
        self.show_learning_progress()
        
        print("\n👋 ARK Enhanced shutdown complete!")


def run_interactive_ark():
    """Run interactive ARK with self-learning."""
    
    print("🚀 ARK ENHANCED - SELF-LEARNING INTERACTIVE MODE")
    print("=" * 50)
    print("💡 Commands:")
    print("   'quit' or 'exit' - Exit")
    print("   'stats' - Show learning statistics")
    print("   'learn' - Force learning update")
    print("   'feedback [positive/negative/suggestion]: [details]' - Provide feedback")
    print("=" * 50)
    
    # Initialize enhanced ARK
    ark = ARKEnhancedBot()
    
    try:
        while True:
            print(f"\n🤖 ARK Enhanced (Conversation #{ark.conversation_count + 1})")
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                break
            elif user_input.lower() == 'stats':
                ark.show_learning_progress()
                continue
            elif user_input.lower() == 'learn':
                result = ark.force_learning_update()
                print(f"🔄 {result}")
                continue
            elif user_input.lower().startswith('feedback'):
                # Parse feedback command
                parts = user_input[8:].split(':', 1)  # Remove 'feedback '
                if len(parts) == 2:
                    feedback_type = parts[0].strip()
                    feedback_details = parts[1].strip()
                    result = ark.provide_feedback(feedback_type, feedback_details)
                    print(f"📝 {result}")
                else:
                    print("📝 Format: feedback [positive/negative/suggestion]: [your feedback]")
                continue
            
            # Regular conversation
            print("\nARK: ", end="")
            response = ark.chat(user_input)
            print(response)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        ark.shutdown()


def demo_self_learning():
    """Demonstrate self-learning capabilities."""
    
    print("🎯 ARK SELF-LEARNING DEMO")
    print("=" * 30)
    
    # Initialize ARK
    ark = ARKEnhancedBot()
    
    # Demo conversations
    demo_conversations = [
        "create a study schedule for my chemistry exam",
        "help me organize my work tasks better",
        "what are effective learning strategies",
        "I need help with time management",
        "explain machine learning concepts"
    ]
    
    print(f"\n📚 Running {len(demo_conversations)} demo conversations...")
    
    for i, question in enumerate(demo_conversations, 1):
        print(f"\n{i}. Demo Question: {question}")
        response = ark.chat(question)
        print(f"ARK Response: {response[:150]}...")
        
        # Simulate some feedback
        if i == 2:
            ark.provide_feedback("positive", "Great explanation, very helpful!")
        elif i == 4:
            ark.provide_feedback("suggestion", "Could you add more practical examples?")
    
    # Show learning progress
    print(f"\n📊 Learning Results:")
    ark.show_learning_progress()
    
    # Shutdown
    ark.shutdown()


if __name__ == "__main__":
    # Choose demo mode or interactive mode
    mode = input("Choose mode - (1) Interactive or (2) Demo: ").strip()
    
    if mode == "2":
        demo_self_learning()
    else:
        run_interactive_ark()