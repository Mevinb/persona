"""
Test ARK's Enhanced Specialized Domain Knowledge
=============================================
Test the newly added specialized domain expertise across multiple fields.
"""

from ark_professional import ARKProfessional
import time

def test_specialized_domains():
    """Test ARK's specialized domain knowledge."""
    
    print("🧪 TESTING ARK'S SPECIALIZED DOMAIN KNOWLEDGE")
    print("=" * 50)
    
    ark = ARKProfessional()
    
    # Test cases for each specialized domain
    test_cases = [
        {
            "domain": "Science - Physics",
            "query": "explain quantum mechanics principles",
            "expected_keywords": ["quantum", "wave-particle", "uncertainty", "superposition"]
        },
        {
            "domain": "Science - Biology", 
            "query": "how does photosynthesis work in plants",
            "expected_keywords": ["chlorophyll", "light-dependent", "calvin cycle", "glucose"]
        },
        {
            "domain": "Technology - Programming",
            "query": "explain python data structures and when to use them",
            "expected_keywords": ["lists", "dictionaries", "sets", "complexity"]
        },
        {
            "domain": "Technology - Machine Learning",
            "query": "what is machine learning and how does it work",
            "expected_keywords": ["supervised", "unsupervised", "training", "algorithms"]
        },
        {
            "domain": "Business - Management",
            "query": "explain project management methodologies and best practices",
            "expected_keywords": ["waterfall", "agile", "stakeholder", "risk"]
        },
        {
            "domain": "Arts - Creative Writing",
            "query": "how to improve creative writing skills",
            "expected_keywords": ["character", "plot", "dialogue", "revision"]
        },
        {
            "domain": "World Knowledge - History",
            "query": "explain the causes and effects of World War II",
            "expected_keywords": ["treaty", "totalitarian", "holocaust", "allies"]
        },
        {
            "domain": "Health - Immunology",
            "query": "explain the human immune system and how it works",
            "expected_keywords": ["innate", "adaptive", "antibodies", "lymphocytes"]
        }
    ]
    
    print(f"Testing {len(test_cases)} specialized domain queries...")
    print()
    
    results = {}
    total_time = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"🔬 Test {i}: {test['domain']}")
        print(f"❓ Query: {test['query']}")
        
        start_time = time.time()
        response = ark.respond(test['query'])
        response_time = time.time() - start_time
        total_time += response_time
        
        # Check for expected keywords (case insensitive)
        response_lower = response.lower()
        keywords_found = [kw for kw in test['expected_keywords'] 
                         if kw.lower() in response_lower]
        keyword_score = len(keywords_found) / len(test['expected_keywords'])
        
        # Response quality metrics
        word_count = len(response.split())
        has_formatting = any(marker in response for marker in ['**', '•', '###', '---'])
        has_sections = '**' in response and len(response.split('**')) > 3
        
        results[test['domain']] = {
            'response_time': response_time,
            'word_count': word_count,
            'keyword_score': keyword_score,
            'has_formatting': has_formatting,
            'has_sections': has_sections,
            'keywords_found': keywords_found,
            'response': response
        }
        
        print(f"✅ Response: {word_count} words, {response_time:.3f}s")
        print(f"🎯 Keywords found: {len(keywords_found)}/{len(test['expected_keywords'])} ({keyword_score:.1%})")
        print(f"📝 Formatted: {'Yes' if has_formatting else 'No'}, Sections: {'Yes' if has_sections else 'No'}")
        
        # Show first 200 characters of response
        preview = response[:200] + "..." if len(response) > 200 else response
        print(f"📖 Preview: {preview}")
        print()
    
    # Show summary statistics
    print("📊 SPECIALIZED DOMAIN TESTING SUMMARY")
    print("=" * 40)
    
    avg_response_time = total_time / len(test_cases)
    avg_word_count = sum(r['word_count'] for r in results.values()) / len(results)
    avg_keyword_score = sum(r['keyword_score'] for r in results.values()) / len(results)
    formatted_responses = sum(1 for r in results.values() if r['has_formatting'])
    sectioned_responses = sum(1 for r in results.values() if r['has_sections'])
    
    print(f"• Total domains tested: {len(test_cases)}")
    print(f"• Average response time: {avg_response_time:.3f} seconds")
    print(f"• Average word count: {avg_word_count:.1f} words")
    print(f"• Average keyword relevance: {avg_keyword_score:.1%}")
    print(f"• Formatted responses: {formatted_responses}/{len(test_cases)} ({formatted_responses/len(test_cases):.1%})")
    print(f"• Structured responses: {sectioned_responses}/{len(test_cases)} ({sectioned_responses/len(test_cases):.1%})")
    
    # Show detailed results for each domain
    print("\n📋 DETAILED DOMAIN RESULTS")
    print("-" * 30)
    
    for domain, result in results.items():
        print(f"🎯 {domain}:")
        print(f"   • Response time: {result['response_time']:.3f}s")
        print(f"   • Word count: {result['word_count']}")
        print(f"   • Keyword relevance: {result['keyword_score']:.1%}")
        print(f"   • Keywords found: {', '.join(result['keywords_found'])}")
        print()
    
    return results

if __name__ == "__main__":
    results = test_specialized_domains()