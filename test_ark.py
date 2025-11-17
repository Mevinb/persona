#!/usr/bin/env python3
"""
Test script for ARK enhanced fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ark_enhanced import EnhancedArk

def test_ark():
    print("=== Testing ARK Enhanced Fixes ===\n")
    
    ark = EnhancedArk()
    
    # Test cases
    test_cases = [
        ("what is 1 + 3", "Should detect as calculation and return '1 + 3 = 4'"),
        ("what can u do", "Should detect as help request"),
        ("calc 5 * 2", "Should calculate 5 * 2 = 10"),
        ("2+3", "Should detect math and calculate"),
        ("hello", "Should greet with memory"),
        ("my name is test", "Should store the name"),
    ]
    
    for test_input, expected in test_cases:
        print(f"Input: '{test_input}'")
        print(f"Expected: {expected}")
        
        intent = ark.intent_detector.detect_intent(test_input)
        response = ark.respond(test_input)
        
        print(f"Detected Intent: {intent}")
        print(f"Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_ark()