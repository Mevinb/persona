"""
Test Self-Learning Trigger
==========================
Test script to trigger actual learning from conversations.
"""

import sys
import time
from datetime import datetime

sys.path.append('.')

def test_learning_trigger():
    """Test learning trigger with sufficient conversations."""
    
    print("🧪 TESTING SELF-LEARNING TRIGGER")
    print("=" * 35)
    
    try:
        from ark_enhanced_self_learning import ARKEnhancedBot
        
        # Initialize ARK
        ark = ARKEnhancedBot()
        
        # Need to have multiple conversations to trigger learning
        test_conversations = [
            "create a study plan for my math exam",
            "help me with calculus homework", 
            "what are good study techniques for mathematics",
            "I need help organizing my study schedule",
            "explain differential equations concepts",
            "how to prepare for a physics test",
            "help me understand quantum mechanics",
            "create a revision timetable",
            "what are effective memory techniques",
            "I need academic help with chemistry"
        ]
        
        print(f"📚 Processing {len(test_conversations)} conversations to trigger learning...")
        
        for i, question in enumerate(test_conversations, 1):
            print(f"\n{i:2d}. Processing: {question[:40]}...")
            
            response = ark.chat(question)
            response_quality = "Good" if len(response) > 200 else "Short"
            print(f"    Response: {response_quality} ({len(response)} chars)")
            
            # Add some feedback to trigger learning
            if i == 3:
                ark.provide_feedback("positive", "Excellent study techniques, very helpful!")
            elif i == 6:
                ark.provide_feedback("suggestion", "Could you add more examples for physics concepts?")
            elif i == 8:
                ark.provide_feedback("negative", "Response was too generic, need more specifics")
        
        print(f"\n🔄 Forcing learning cycle to process conversations...")
        result = ark.force_learning_update()
        print(f"Learning result: {result}")
        
        # Show final learning progress
        print(f"\n📊 Final Learning Statistics:")
        ark.show_learning_progress()
        
        # Shutdown
        ark.shutdown()
        
        print(f"\n✅ Self-learning trigger test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_learning_trigger()