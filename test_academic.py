"""
Test ARK with Academic Questions
===============================
Test the fixed ARK with proper academic training.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from ark_intelligent_brain import ARKIntelligentBrain

def test_ark_academic():
    """Test ARK with academic questions."""
    
    print("🎓 TESTING ARK ACADEMIC INTELLIGENCE")
    print("=" * 45)
    
    # Initialize ARK brain
    try:
        ark_brain = ARKIntelligentBrain()
        print("✅ ARK Brain initialized successfully")
        
        # Test academic questions
        academic_questions = [
            "create a study table for my exam",
            "help me with my homework", 
            "how to prepare for my final exam",
            "what are good study methods",
            "I need help understanding this concept"
        ]
        
        print(f"\nTesting {len(academic_questions)} academic questions:")
        print("-" * 45)
        
        for i, question in enumerate(academic_questions, 1):
            print(f"\n{i}. Question: '{question}'")
            print("-" * 30)
            
            try:
                # Use the correct method name
                response = ark_brain.process_input(question)
                
                # Check response quality
                if len(response) < 50:
                    print(f"⚠️  Short response: {response}")
                elif "quarterly business review" in response.lower():
                    print(f"❌ Wrong response type detected!")
                    print(f"Response: {response[:200]}...")
                elif any(keyword in response.lower() for keyword in ["study", "exam", "homework", "learning", "education"]):
                    print(f"✅ Relevant academic response!")
                    print(f"Response length: {len(response)} characters")
                    print(f"Preview: {response[:150]}...")
                else:
                    print(f"⚠️  Potentially irrelevant response")
                    print(f"Preview: {response[:150]}...")
                    
            except Exception as e:
                print(f"❌ Error processing question: {e}")
        
        print(f"\n🎉 ACADEMIC TESTING COMPLETE!")
        
    except Exception as e:
        print(f"❌ Failed to initialize ARK: {e}")

if __name__ == "__main__":
    test_ark_academic()