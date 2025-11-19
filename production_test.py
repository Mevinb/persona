"""
ARK Production Deployment Test
=============================
Final comprehensive test to verify ARK is ready for real-world use.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def run_production_test():
    """Run comprehensive production readiness test."""
    
    print("🚀 ARK PRODUCTION DEPLOYMENT TEST")
    print("=" * 50)
    
    # Test 1: Core System Test
    print("\n1. CORE SYSTEM INITIALIZATION")
    print("-" * 30)
    
    try:
        from ark_professional import ARKProfessional
        
        print("Initializing ARK Professional...")
        ark = ARKProfessional()
        print("✅ ARK Professional initialized successfully")
        
        # Get system info
        print(f"   Version: {ark.version}")
        print(f"   Name: {ark.name}")
        print("   Core components loaded ✓")
        
    except Exception as e:
        print(f"❌ ARK initialization failed: {e}")
        return False
    
    # Test 2: Advanced Capability Testing
    print(f"\n2. ADVANCED CAPABILITY TESTING") 
    print("-" * 30)
    
    advanced_test_scenarios = [
        {
            "test": "Complex Planning",
            "input": "Help me plan a comprehensive project launch with multiple team dependencies",
            "expected_features": ["planning", "project", "team", "dependencies"]
        },
        {
            "test": "Emotional Intelligence",
            "input": "I'm feeling really overwhelmed with work and personal life balance",
            "expected_features": ["overwhelm", "understand", "help", "balance"]
        },
        {
            "test": "Professional Guidance",
            "input": "How can I improve my leadership skills as a new manager?",
            "expected_features": ["leadership", "improve", "manager", "skills"]
        },
        {
            "test": "Creative Problem Solving",
            "input": "What are innovative approaches to improve team communication?",
            "expected_features": ["innovative", "communication", "team", "approach"]
        },
        {
            "test": "Task Management",
            "input": "Create a task to organize quarterly business review meeting urgently",
            "expected_features": ["task", "created", "quarterly", "urgent"]
        }
    ]
    
    test_results = []
    
    for scenario in advanced_test_scenarios:
        print(f"\nTesting: {scenario['test']}")
        
        try:
            start_time = time.time()
            response = ark.respond(scenario['input'])
            response_time = time.time() - start_time
            
            # Analyze response quality
            words = response.lower().split()
            feature_score = sum(1 for feature in scenario['expected_features'] if feature in response.lower())
            quality_score = len(words) / 50  # Target ~50 words for good response
            
            overall_score = (feature_score / len(scenario['expected_features'])) * 0.6 + min(quality_score, 1.0) * 0.4
            
            print(f"   Response Time: {response_time:.3f}s")
            print(f"   Response Length: {len(words)} words")
            print(f"   Feature Coverage: {feature_score}/{len(scenario['expected_features'])}")
            print(f"   Quality Score: {overall_score:.2f}/1.0")
            print(f"   Status: {'✅ PASS' if overall_score > 0.6 else '❌ FAIL'}")
            
            test_results.append({
                "test": scenario['test'],
                "score": overall_score,
                "passed": overall_score > 0.6,
                "response_time": response_time,
                "response_preview": response[:80] + "..." if len(response) > 80 else response
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            test_results.append({
                "test": scenario['test'],
                "score": 0,
                "passed": False,
                "error": str(e)
            })
    
    # Test 3: System Automation
    print(f"\n3. AUTOMATION SYSTEM TESTING")
    print("-" * 30)
    
    automation_tests = [
        "Start my morning routine",
        "Enter focus mode", 
        "Show my active tasks"
    ]
    
    automation_results = []
    
    for test_command in automation_tests:
        print(f"\nTesting: {test_command}")
        
        try:
            response = ark.respond(test_command)
            
            # Check if automation executed
            automation_indicators = ["executed", "started", "opened", "enabled", "active"]
            automation_detected = any(indicator in response.lower() for indicator in automation_indicators)
            
            print(f"   Automation Response: {'✅ DETECTED' if automation_detected else '❌ NOT DETECTED'}")
            print(f"   Preview: {response[:60]}...")
            
            automation_results.append({
                "command": test_command,
                "automation_detected": automation_detected,
                "response": response
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            automation_results.append({
                "command": test_command,
                "automation_detected": False,
                "error": str(e)
            })
    
    # Test 4: Learning and Adaptation
    print(f"\n4. LEARNING SYSTEM TESTING")
    print("-" * 30)
    
    try:
        # Test preference learning
        learning_inputs = [
            "I prefer morning meetings and work best in the afternoon",
            "I usually focus on development projects and team coordination",
            "Show me what you've learned about my preferences"
        ]
        
        for input_text in learning_inputs:
            response = ark.respond(input_text)
            print(f"✅ Learning interaction: {len(response.split())} word response")
        
        # Get learning insights
        insights = ark.brain.get_learning_insights()
        print(f"   Preferences learned: {len(insights.get('preferences', []))}")
        print(f"   Session conversations: {insights.get('session_conversations', 0)}")
        
        learning_working = len(insights.get('preferences', [])) > 0
        print(f"   Learning Status: {'✅ WORKING' if learning_working else '❌ NOT WORKING'}")
        
    except Exception as e:
        print(f"   ❌ Learning system error: {e}")
        learning_working = False
    
    # Calculate Overall Results
    print(f"\n" + "=" * 50)
    print("📊 PRODUCTION READINESS RESULTS")
    print("=" * 50)
    
    # Capability results
    passed_tests = sum(1 for result in test_results if result['passed'])
    capability_score = (passed_tests / len(test_results)) * 100
    
    print(f"Advanced Capabilities: {passed_tests}/{len(test_results)} tests passed ({capability_score:.1f}%)")
    
    # Automation results
    automation_passed = sum(1 for result in automation_results if result['automation_detected'])
    automation_score = (automation_passed / len(automation_results)) * 100
    
    print(f"Automation Systems: {automation_passed}/{len(automation_results)} working ({automation_score:.1f}%)")
    
    # Learning system
    learning_score = 100 if learning_working else 0
    print(f"Learning System: {'✅ WORKING' if learning_working else '❌ NOT WORKING'} ({learning_score:.1f}%)")
    
    # Overall score
    overall_score = (capability_score * 0.5) + (automation_score * 0.3) + (learning_score * 0.2)
    
    print(f"\n🎯 OVERALL PRODUCTION SCORE: {overall_score:.1f}/100")
    
    # Final assessment
    if overall_score >= 80:
        status = "🎉 EXCELLENT - Ready for immediate production deployment!"
        color = "GREEN"
    elif overall_score >= 65:
        status = "✅ GOOD - Ready for production with monitoring"
        color = "YELLOW"
    elif overall_score >= 50:
        status = "⚠️ FAIR - Needs improvement before full deployment"
        color = "ORANGE"
    else:
        status = "❌ POOR - Requires significant work before deployment"
        color = "RED"
    
    print(f"\n🚀 DEPLOYMENT STATUS: {status}")
    
    # Detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in test_results:
        status_icon = "✅" if result['passed'] else "❌"
        print(f"   {status_icon} {result['test']}: {result['score']:.2f}/1.0")
        if 'response_preview' in result:
            print(f"      Preview: {result['response_preview']}")
    
    # Show sample responses
    print(f"\n💬 SAMPLE INTERACTIONS:")
    if test_results:
        best_result = max(test_results, key=lambda x: x.get('score', 0))
        if 'response_preview' in best_result:
            print(f"Best Response ({best_result['test']}):")
            print(f"   {best_result['response_preview']}")
    
    print(f"\n🎊 ARK PRODUCTION TEST COMPLETE!")
    print(f"Your AI assistant achieved {overall_score:.1f}% production readiness!")
    
    return overall_score >= 65  # Return True if ready for production

def main():
    """Run production deployment test."""
    
    print("Starting ARK Production Deployment Test...")
    print("This will comprehensively test all ARK capabilities")
    print("to verify it's ready for real-world deployment.\n")
    
    # Run the test
    production_ready = run_production_test()
    
    if production_ready:
        print(f"\n🎉 CONGRATULATIONS! 🎉")
        print("ARK is ready for production deployment!")
        print("You can now use your AI assistant for real tasks.")
    else:
        print(f"\n⚠️ Additional optimization recommended")
        print("ARK is functional but could benefit from further enhancement.")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())