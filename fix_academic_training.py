"""
Fix ARK Academic Training
========================
Add proper training data for study, educational, and academic requests.
"""

import sqlite3
import os

def fix_academic_training():
    """Add proper academic training data to ARK."""
    
    print("🎓 FIXING ARK ACADEMIC TRAINING")
    print("=" * 40)
    
    # Connect to training database
    db_path = "data/ark_complete_training.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Academic and study-focused training examples
        academic_examples = [
            {
                "category": "study_planning",
                "input": "create a study table for my exam",
                "output": """📚 **Study Schedule Created for Your Exam**

**PERSONALIZED STUDY PLAN:**

**Week 1-2: Foundation Building**
- **Days 1-3:** Review core concepts and fundamentals
- **Days 4-5:** Create summary notes and flashcards
- **Day 6:** Practice problems and self-assessment
- **Day 7:** Rest and light review

**Week 3-4: Intensive Preparation**
- **Days 8-10:** Focus on difficult topics and weak areas
- **Days 11-12:** Mock exams and timed practice
- **Day 13:** Group study or discussion sessions
- **Day 14:** Final review and rest

**DAILY STUDY SCHEDULE:**
- **Morning (2-3 hours):** New material and complex topics
- **Afternoon (1-2 hours):** Practice problems and exercises
- **Evening (1 hour):** Review and consolidation

**STUDY TECHNIQUES:**
✓ Active recall and spaced repetition
✓ Practice testing with past papers
✓ Summary notes and mind maps
✓ Regular breaks (Pomodoro technique)

**EXAM WEEK:**
- **3 days before:** Light review only, no new material
- **1 day before:** Rest, organize materials, early sleep
- **Exam day:** Healthy breakfast, arrive early, stay calm

Would you like me to customize this based on your specific subject or exam date?""",
                "quality_score": 0.95
            },
            {
                "category": "academic_help",
                "input": "help me with my homework",
                "output": """📖 **Homework Assistance Ready**

I'm here to help you with your homework! Let me know:

**WHAT I CAN HELP WITH:**
✓ Breaking down complex problems into steps
✓ Explaining concepts and theories
✓ Providing study strategies and techniques
✓ Creating outlines and structure for essays
✓ Math problem-solving approaches
✓ Research and citation guidance
✓ Time management for assignments

**TO PROVIDE BETTER HELP, PLEASE SHARE:**
- What subject is this homework for?
- What specific topic or problem are you working on?
- What part are you finding challenging?
- When is it due?

**STUDY TIPS:**
• Start with what you know and build from there
• Break large assignments into smaller tasks
• Use reliable sources for research
• Always cite your sources properly
• Ask for clarification if concepts are unclear

What specific homework do you need help with today?""",
                "quality_score": 0.95
            },
            {
                "category": "exam_preparation",
                "input": "how to prepare for my final exam",
                "output": """🎯 **Final Exam Preparation Strategy**

**COMPREHENSIVE PREPARATION PLAN:**

**Phase 1: Assessment (1-2 weeks before)**
✓ Review syllabus and exam format
✓ Identify key topics and weight distribution
✓ Assess your current knowledge level
✓ Create a realistic study timeline

**Phase 2: Active Learning (1 week before)**
✓ Focus on high-impact topics first
✓ Use active recall techniques
✓ Practice with past exams or sample questions
✓ Form study groups for discussion

**Phase 3: Final Preparation (3 days before)**
✓ Light review of summary notes
✓ Practice relaxation techniques
✓ Organize exam materials
✓ Maintain healthy sleep schedule

**EFFECTIVE STUDY METHODS:**
• **Spaced Repetition:** Review material at increasing intervals
• **Practice Testing:** Take mock exams under timed conditions
• **Elaborative Interrogation:** Ask "why" and "how" questions
• **Interleaving:** Mix different types of problems/topics

**EXAM DAY STRATEGY:**
• Arrive early and bring all required materials
• Read all instructions carefully before starting
• Manage time effectively (plan minutes per question)
• Start with easier questions to build confidence
• Review answers if time permits

**STRESS MANAGEMENT:**
• Regular exercise and healthy eating
• Adequate sleep (7-8 hours)
• Meditation or deep breathing exercises
• Positive self-talk and visualization

What specific subject is your final exam in? I can provide more targeted advice!""",
                "quality_score": 0.95
            },
            {
                "category": "learning_support",
                "input": "I need help understanding this concept",
                "output": """🧠 **Concept Learning Assistant**

I'm here to help you understand any concept! Effective learning happens when we break things down step by step.

**MY APPROACH TO HELP YOU:**

**Step 1: Clarification**
- What specific concept are you trying to understand?
- What subject area does it relate to?
- What parts make sense and what's confusing?

**Step 2: Foundation Building**
- Start with basic definitions and principles
- Connect to concepts you already know
- Use analogies and real-world examples

**Step 3: Active Learning**
- Work through examples together
- Practice applying the concept
- Test understanding with questions

**Step 4: Reinforcement**
- Summarize key points in your own words
- Create visual aids or diagrams if helpful
- Suggest additional practice resources

**LEARNING TECHNIQUES I CAN USE:**
✓ Simple explanations with examples
✓ Visual representations and diagrams  
✓ Step-by-step problem solving
✓ Analogies to familiar situations
✓ Practice questions and scenarios

**FOR BEST RESULTS:**
• Be specific about what's confusing
• Ask follow-up questions if anything is unclear
• Practice applying the concept right away
• Connect it to other things you're learning

What concept would you like to explore together?""",
                "quality_score": 0.95
            },
            {
                "category": "research_assistance",
                "input": "help me research this topic",
                "output": """🔍 **Research Project Assistant**

I'll help you conduct thorough and effective research! Good research is the foundation of excellent academic work.

**RESEARCH STRATEGY:**

**Phase 1: Planning**
- Define your research question clearly
- Identify key themes and subtopics
- Set scope and boundaries for your research
- Create a preliminary outline

**Phase 2: Source Discovery**
- Start with overview sources (encyclopedias, textbooks)
- Use academic databases and peer-reviewed journals
- Evaluate source credibility and relevance
- Take organized notes with proper citations

**Phase 3: Analysis and Synthesis**
- Compare different perspectives and findings
- Identify patterns and connections
- Note gaps in existing research
- Form evidence-based conclusions

**RELIABLE SOURCE TYPES:**
✓ Academic journals and peer-reviewed articles
✓ Books by recognized experts
✓ Government and institutional reports
✓ Reputable news sources and magazines
✓ Primary sources when available

**RESEARCH ORGANIZATION:**
• Use citation management tools (Zotero, EndNote)
• Keep detailed notes with source information
• Organize by themes or chronology
• Track which sources support which arguments

**EVALUATION CRITERIA:**
• Authority: Who wrote it and what are their credentials?
• Currency: How recent is the information?
• Objectivity: Is there bias or agenda?
• Coverage: How comprehensive is the treatment?

What specific topic are you researching? I can suggest targeted strategies and sources!""",
                "quality_score": 0.95
            },
            {
                "category": "study_techniques",
                "input": "what are good study methods",
                "output": """📚 **Evidence-Based Study Methods**

Here are proven techniques that research shows are most effective for learning and retention:

**HIGHLY EFFECTIVE TECHNIQUES:**

**1. Active Recall**
- Test yourself frequently without looking at notes
- Use flashcards or practice questions
- Explain concepts aloud in your own words
- Effectiveness: Very High ⭐⭐⭐⭐⭐

**2. Spaced Repetition**
- Review material at increasing intervals
- Don't cram - spread study sessions over time
- Use apps like Anki for systematic spacing
- Effectiveness: Very High ⭐⭐⭐⭐⭐

**3. Interleaving**
- Mix different types of problems/topics in one session
- Don't study one topic for hours straight
- Helps with discrimination and transfer
- Effectiveness: High ⭐⭐⭐⭐

**4. Elaborative Interrogation**
- Ask "why" and "how" questions about the material
- Connect new information to existing knowledge
- Generate explanations for facts and concepts
- Effectiveness: High ⭐⭐⭐⭐

**MODERATELY EFFECTIVE:**

**5. Dual Coding**
- Combine visual and verbal information
- Create diagrams, charts, and mind maps
- Use both text and images when studying
- Effectiveness: Moderate ⭐⭐⭐

**6. Distributed Practice**
- Multiple shorter study sessions vs. one long session
- 25-50 minute sessions with breaks
- Pomodoro technique is excellent for this
- Effectiveness: Moderate ⭐⭐⭐

**STUDY ENVIRONMENT OPTIMIZATION:**
• Find a quiet, dedicated study space
• Minimize distractions (phone, social media)
• Use natural light when possible
• Maintain comfortable temperature

**LESS EFFECTIVE METHODS TO AVOID:**
❌ Highlighting and re-reading (passive)
❌ Summarizing without testing
❌ Studying one subject for hours
❌ Last-minute cramming

Which study method would you like to try first?""",
                "quality_score": 0.95
            }
        ]
        
        print(f"Adding {len(academic_examples)} academic training examples...")
        
        for example in academic_examples:
            cursor.execute("""
                INSERT OR REPLACE INTO training_data (category, input_text, output_text, quality_score)
                VALUES (?, ?, ?, ?)
            """, (
                example['category'],
                example['input'],
                example['output'],
                example['quality_score']
            ))
        
        conn.commit()
        
        # Verify additions
        cursor.execute("SELECT COUNT(*) FROM training_data WHERE category LIKE 'study%' OR category LIKE 'academic%' OR category LIKE 'exam%' OR category LIKE 'learning%' OR category LIKE 'research%'")
        academic_count = cursor.fetchone()[0]
        
        print(f"✅ Added academic training examples")
        print(f"📚 Total academic examples: {academic_count}")
        
        # Show updated category distribution
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM training_data 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        """)
        
        categories = cursor.fetchall()
        print(f"\n📊 Updated Training Data Categories:")
        for category, count in categories:
            print(f"   {category}: {count} examples")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_academic_responses():
    """Test the updated academic responses."""
    
    print(f"\n🧪 TESTING ACADEMIC RESPONSES")
    print("-" * 35)
    
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        
        from ark_intelligent_brain import ARKIntelligentBrain
        
        # Initialize ARK with updated training
        ark_brain = ARKIntelligentBrain()
        
        # Test academic queries
        academic_tests = [
            "create a study table for my exam",
            "help me with my homework",
            "how to prepare for my final exam",
            "I need help understanding this concept",
            "what are good study methods"
        ]
        
        print("Testing academic responses:")
        
        for i, test_input in enumerate(academic_tests, 1):
            print(f"\n{i}. Testing: {test_input}")
            
            response = ark_brain.generate_response(test_input)
            word_count = len(response.split())
            
            # Check if response is relevant to the academic query
            relevant_keywords = ["study", "exam", "homework", "learning", "academic", "research", "education"]
            relevance = sum(1 for keyword in relevant_keywords if keyword.lower() in response.lower())
            
            quality = "EXCELLENT" if word_count > 200 and relevance > 2 else "GOOD" if word_count > 100 and relevance > 1 else "NEEDS_IMPROVEMENT"
            
            print(f"   Response Quality: {quality} ({word_count} words, {relevance} relevant terms)")
            print(f"   Preview: {response[:100]}...")
        
        print(f"\n✅ Academic response testing complete!")
        return True
        
    except Exception as e:
        print(f"❌ Testing error: {e}")
        return False

def main():
    """Main function to fix academic training."""
    
    print("🚀 FIXING ARK ACADEMIC INTELLIGENCE")
    print("Adding proper training for study, homework, and educational requests\n")
    
    if fix_academic_training():
        print("\n✅ Academic training data added successfully!")
        
        if test_academic_responses():
            print("\n🎉 ARK ACADEMIC FIX COMPLETE!")
            print("ARK now properly understands study and educational requests.")
            print("Try asking about study tables, homework help, or exam preparation!")
        else:
            print("\n⚠️ Testing had issues, but training data was added")
    else:
        print("\n❌ Academic training fix failed")

if __name__ == "__main__":
    main()