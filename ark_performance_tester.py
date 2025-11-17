"""
ARK Performance Monitor - Advanced Testing & Validation
=====================================================
Comprehensive testing suite to validate ARK's capabilities
and monitor performance improvements.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
import sqlite3

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from ark_professional import ARKProfessional
from ark_intelligent_brain import ARKIntelligentBrain

class ARKPerformanceTester:
    """Comprehensive testing for ARK capabilities."""
    
    def __init__(self):
        self.test_results = []
        self.ark = None
        self.test_scenarios = self.load_test_scenarios()
    
    def load_test_scenarios(self):
        """Load comprehensive test scenarios."""
        return [
            # Basic Intelligence Tests
            {
                "category": "basic_intelligence",
                "input": "Hello ARK, how are you today?",
                "expected_capabilities": ["greeting_response", "conversational"],
                "complexity": 1
            },
            
            # Task Management Tests
            {
                "category": "task_management", 
                "input": "Create task: Review quarterly reports by Friday urgent",
                "expected_capabilities": ["task_creation", "priority_detection", "deadline_parsing"],
                "complexity": 3
            },
            
            # System Automation Tests
            {
                "category": "automation",
                "input": "Start my morning routine",
                "expected_capabilities": ["automation_execution", "multi_step_planning"],
                "complexity": 4
            },
            
            # Complex Problem Solving
            {
                "category": "complex_reasoning",
                "input": "I need to organize a team meeting urgently but I'm not sure about everyone's availability",
                "expected_capabilities": ["problem_analysis", "solution_planning", "context_understanding"],
                "complexity": 5
            },
            
            # Learning & Adaptation Tests
            {
                "category": "learning",
                "input": "I prefer meetings in the morning and I work on development projects mostly",
                "expected_capabilities": ["preference_learning", "memory_storage", "pattern_recognition"],
                "complexity": 4
            },
            
            # Productivity Analysis
            {
                "category": "productivity",
                "input": "Analyze my productivity patterns",
                "expected_capabilities": ["data_analysis", "insight_generation", "personalized_recommendations"],
                "complexity": 5
            },
            
            # Multi-Modal Understanding
            {
                "category": "understanding",
                "input": "I'm feeling overwhelmed with too many projects and tight deadlines",
                "expected_capabilities": ["sentiment_analysis", "stress_detection", "supportive_response"],
                "complexity": 4
            },
            
            # Professional Assistance
            {
                "category": "professional",
                "input": "Help me plan a project timeline with multiple dependencies",
                "expected_capabilities": ["project_planning", "dependency_management", "timeline_creation"],
                "complexity": 5
            }
        ]
    
    def setup_test_environment(self):
        """Setup clean test environment."""
        print("Setting up test environment...")
        
        try:
            self.ark = ARKProfessional()
            print("✓ ARK Professional initialized")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize ARK: {e}")
            return False
    
    def test_response_quality(self, input_text: str, expected_capabilities: list) -> dict:
        """Test the quality of ARK's response."""
        start_time = time.time()
        
        try:
            response = self.ark.respond(input_text)
            response_time = time.time() - start_time
            
            # Analyze response quality
            quality_score = self.analyze_response_quality(response, expected_capabilities)
            
            return {
                "success": True,
                "response": response,
                "response_time": response_time,
                "quality_score": quality_score,
                "capabilities_met": quality_score["capabilities_met"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "quality_score": {"total": 0, "capabilities_met": []},
                "capabilities_met": []
            }
    
    def analyze_response_quality(self, response: str, expected_capabilities: list) -> dict:
        """Analyze the quality of a response."""
        
        quality_indicators = {
            "greeting_response": ["hello", "hi", "good", "thanks", "thank you"],
            "conversational": ["i", "you", "we", "?", "!"],
            "task_creation": ["task", "created", "id:", "successfully"],
            "priority_detection": ["urgent", "important", "priority", "high"],
            "deadline_parsing": ["friday", "due", "deadline", "by"],
            "automation_execution": ["routine", "executed", "opened", "started"],
            "multi_step_planning": ["step", "action", "✓", "✗"],
            "problem_analysis": ["understand", "need", "help", "solution"],
            "solution_planning": ["plan", "organize", "suggest", "recommend"],
            "context_understanding": ["urgent", "team", "meeting", "availability"],
            "preference_learning": ["prefer", "learn", "remember", "noted"],
            "memory_storage": ["saved", "remember", "stored", "preference"],
            "pattern_recognition": ["pattern", "usually", "typically", "often"],
            "data_analysis": ["analysis", "patterns", "insights", "statistics"],
            "insight_generation": ["recommend", "suggest", "insight", "improve"],
            "personalized_recommendations": ["you", "your", "recommend", "based on"],
            "sentiment_analysis": ["understand", "feeling", "support", "help"],
            "stress_detection": ["overwhelmed", "stress", "pressure", "difficult"],
            "supportive_response": ["help", "support", "manage", "together"],
            "project_planning": ["project", "plan", "timeline", "schedule"],
            "dependency_management": ["depend", "prerequisite", "order", "sequence"],
            "timeline_creation": ["timeline", "schedule", "deadline", "phase"]
        }
        
        capabilities_met = []
        total_score = 0
        
        response_lower = response.lower()
        
        for capability in expected_capabilities:
            if capability in quality_indicators:
                indicators = quality_indicators[capability]
                
                # Check if any indicators are present
                if any(indicator in response_lower for indicator in indicators):
                    capabilities_met.append(capability)
                    total_score += 1
        
        # Additional quality factors
        length_bonus = min(len(response) / 100, 1.0)  # Bonus for appropriate length
        specificity_bonus = response.count('.') * 0.1  # Bonus for structured responses
        
        final_score = (total_score / len(expected_capabilities)) + (length_bonus * 0.2) + (specificity_bonus * 0.1)
        final_score = min(final_score, 1.0)  # Cap at 1.0
        
        return {
            "total": round(final_score, 2),
            "capabilities_met": capabilities_met,
            "length_score": round(length_bonus, 2),
            "structure_score": round(specificity_bonus, 2)
        }
    
    def run_comprehensive_tests(self):
        """Run all test scenarios."""
        print("\n" + "="*60)
        print("ARK PROFESSIONAL - COMPREHENSIVE TESTING SUITE")
        print("="*60)
        
        if not self.setup_test_environment():
            return False
        
        total_tests = len(self.test_scenarios)
        passed_tests = 0
        total_response_time = 0
        total_quality_score = 0
        
        print(f"\nRunning {total_tests} comprehensive tests...\n")
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"Test {i}/{total_tests}: {scenario['category'].title()}")
            print(f"Input: '{scenario['input']}'")
            print(f"Expected: {', '.join(scenario['expected_capabilities'])}")
            
            result = self.test_response_quality(
                scenario['input'], 
                scenario['expected_capabilities']
            )
            
            # Store detailed results
            test_record = {
                "test_number": i,
                "category": scenario['category'],
                "complexity": scenario['complexity'],
                "input": scenario['input'],
                "expected_capabilities": scenario['expected_capabilities'],
                "timestamp": datetime.now().isoformat(),
                **result
            }
            
            self.test_results.append(test_record)
            
            if result['success']:
                quality = result['quality_score']['total']
                capabilities_met = len(result['capabilities_met'])
                capabilities_expected = len(scenario['expected_capabilities'])
                
                print(f"Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
                print(f"Quality Score: {quality:.2f}/1.0")
                print(f"Capabilities Met: {capabilities_met}/{capabilities_expected}")
                print(f"Response Time: {result['response_time']:.3f}s")
                
                if quality >= 0.6 and capabilities_met >= capabilities_expected * 0.5:
                    print("✅ PASSED")
                    passed_tests += 1
                else:
                    print("❌ FAILED (Quality or capabilities below threshold)")
                
                total_quality_score += quality
                total_response_time += result['response_time']
            else:
                print(f"❌ ERROR: {result['error']}")
            
            print("-" * 40 + "\n")
            time.sleep(0.5)  # Brief pause between tests
        
        # Generate summary report
        self.generate_summary_report(passed_tests, total_tests, total_quality_score, total_response_time)
        
        return passed_tests / total_tests >= 0.7  # 70% pass rate for overall success
    
    def generate_summary_report(self, passed_tests: int, total_tests: int, total_quality: float, total_time: float):
        """Generate comprehensive summary report."""
        
        pass_rate = (passed_tests / total_tests) * 100
        avg_quality = total_quality / total_tests
        avg_response_time = total_time / total_tests
        
        print("="*60)
        print("TESTING SUMMARY REPORT")
        print("="*60)
        
        print(f"📊 Overall Results:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({pass_rate:.1f}%)")
        print(f"   Average Quality Score: {avg_quality:.2f}/1.0")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        
        # Performance by category
        category_stats = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in category_stats:
                category_stats[cat] = {'tests': 0, 'passed': 0, 'quality': 0}
            
            category_stats[cat]['tests'] += 1
            category_stats[cat]['quality'] += result['quality_score']['total']
            
            if (result['success'] and 
                result['quality_score']['total'] >= 0.6 and 
                len(result['capabilities_met']) >= len(result['expected_capabilities']) * 0.5):
                category_stats[cat]['passed'] += 1
        
        print(f"\n📈 Performance by Category:")
        for category, stats in category_stats.items():
            cat_pass_rate = (stats['passed'] / stats['tests']) * 100
            cat_avg_quality = stats['quality'] / stats['tests']
            print(f"   {category.replace('_', ' ').title()}: {stats['passed']}/{stats['tests']} ({cat_pass_rate:.1f}%) - Quality: {cat_avg_quality:.2f}")
        
        # Capability analysis
        all_capabilities = set()
        capability_success = {}
        
        for result in self.test_results:
            for cap in result['expected_capabilities']:
                all_capabilities.add(cap)
                if cap not in capability_success:
                    capability_success[cap] = {'tested': 0, 'met': 0}
                
                capability_success[cap]['tested'] += 1
                if cap in result['capabilities_met']:
                    capability_success[cap]['met'] += 1
        
        print(f"\n🎯 Capability Performance:")
        for capability in sorted(all_capabilities):
            stats = capability_success[capability]
            success_rate = (stats['met'] / stats['tested']) * 100
            print(f"   {capability.replace('_', ' ').title()}: {stats['met']}/{stats['tested']} ({success_rate:.1f}%)")
        
        # Overall assessment
        print(f"\n🏆 Overall Assessment:")
        if pass_rate >= 85:
            print("   EXCELLENT - ARK Professional demonstrates superior AI capabilities")
        elif pass_rate >= 70:
            print("   GOOD - ARK Professional shows strong performance with room for improvement")
        elif pass_rate >= 50:
            print("   FAIR - ARK Professional has basic functionality but needs enhancement")
        else:
            print("   NEEDS IMPROVEMENT - ARK Professional requires significant development")
        
        # Save detailed results
        self.save_test_results()
        
        print(f"\n📁 Detailed results saved to: data/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    def save_test_results(self):
        """Save test results to file."""
        filename = f"data/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)

def main():
    """Run the ARK Performance Testing Suite."""
    
    print("ARK Professional - Performance Testing & Validation")
    print("This will run comprehensive tests to validate ARK's capabilities.")
    print()
    
    response = input("Do you want to run the full test suite? (y/n): ")
    if response.lower().strip() != 'y':
        print("Test cancelled.")
        return
    
    tester = ARKPerformanceTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 ARK Professional has passed comprehensive testing!")
        print("The system demonstrates advanced AI capabilities and is ready for production use.")
    else:
        print("\n⚠️  ARK Professional needs additional development.")
        print("Some capabilities require improvement before production deployment.")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())