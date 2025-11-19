#!/usr/bin/env python3
"""
Curated Training Data Generator
================================
Generates high-quality training examples for ARK AI based on documented
dataset patterns and categories.
"""

import sqlite3
import os
import json
from datetime import datetime

def generate_curated_training_data():
    """Generate curated training examples for ARK AI."""
    
    print("=" * 60)
    print("🎯 Generating Curated Training Data for ARK AI")
    print("=" * 60)
    print()
    
    # Database setup
    db_path = "data/ark_complete_training.db"
    os.makedirs("data", exist_ok=True)
    
    # Curated training examples based on documented dataset patterns
    training_examples = [
        # Conversational AI examples (PersonaChat style)
        {
            "input": "Tell me about yourself",
            "output": "I'm ARK, your personal AI assistant. I've been trained on diverse internet datasets including conversational data, educational content, and technical documentation. I'm here to help you with questions, tasks, and to have meaningful conversations.",
            "category": "conversational",
            "source": "curated_persona",
            "quality": 0.95
        },
        {
            "input": "What can you help me with?",
            "output": "I can assist you with a wide range of tasks: answering questions, explaining concepts, helping with problem-solving, providing information on various topics including technology, science, and education, and having natural conversations. My knowledge comes from training on over 370 million examples from sources like Stack Overflow, Wikipedia, educational datasets, and conversational AI data.",
            "category": "conversational",
            "source": "curated_capability",
            "quality": 0.95
        },
        
        # Educational content (SQuAD style Q&A)
        {
            "input": "What is machine learning?",
            "output": "Machine learning is a subset of artificial intelligence that focuses on building systems that can learn from and make decisions based on data. Instead of being explicitly programmed for every task, machine learning algorithms use statistical techniques to identify patterns in data and improve their performance over time through experience.",
            "category": "educational",
            "source": "curated_knowledge",
            "quality": 0.92
        },
        {
            "input": "Explain neural networks",
            "output": "Neural networks are computing systems inspired by biological neural networks in animal brains. They consist of interconnected nodes (neurons) organized in layers. Information flows through the network, with each connection having a weight that adjusts as learning proceeds. Neural networks excel at pattern recognition, classification, and can learn complex relationships in data through a process called backpropagation.",
            "category": "educational",
            "source": "curated_knowledge",
            "quality": 0.92
        },
        {
            "input": "What is natural language processing?",
            "output": "Natural Language Processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and human language. It involves teaching machines to understand, interpret, and generate human language in a valuable way. NLP powers applications like chatbots, translation services, sentiment analysis, and text summarization.",
            "category": "educational",
            "source": "curated_knowledge",
            "quality": 0.92
        },
        
        # Technical problem-solving (Stack Overflow style)
        {
            "input": "How do I optimize Python code performance?",
            "output": "To optimize Python code performance: 1) Use built-in functions and libraries (they're implemented in C), 2) Use list comprehensions instead of loops when appropriate, 3) Avoid global variables, 4) Use generators for large datasets to save memory, 5) Profile your code to identify bottlenecks using tools like cProfile, 6) Consider using NumPy for numerical operations, and 7) Use multiprocessing or async for I/O-bound operations.",
            "category": "technical",
            "source": "curated_programming",
            "quality": 0.90
        },
        {
            "input": "What are the best practices for writing clean code?",
            "output": "Clean code best practices include: 1) Write clear, descriptive variable and function names, 2) Keep functions small and focused on a single task, 3) Follow the DRY principle (Don't Repeat Yourself), 4) Add meaningful comments for complex logic, 5) Use consistent formatting and style, 6) Write unit tests, 7) Handle errors gracefully, 8) Keep code simple and avoid premature optimization, and 9) Review and refactor regularly.",
            "category": "technical",
            "source": "curated_programming",
            "quality": 0.90
        },
        
        # Professional guidance (Harvard Business Review style)
        {
            "input": "How can I improve my productivity?",
            "output": "To improve productivity: 1) Prioritize tasks using methods like Eisenhower Matrix, 2) Use time-blocking to focus on specific tasks, 3) Eliminate distractions during deep work sessions, 4) Take regular breaks (Pomodoro technique), 5) Maintain a consistent sleep schedule, 6) Exercise regularly for mental clarity, 7) Use tools to automate repetitive tasks, 8) Set clear, achievable goals, and 9) Review and adjust your workflow regularly.",
            "category": "professional",
            "source": "curated_productivity",
            "quality": 0.88
        },
        {
            "input": "What makes an effective leader?",
            "output": "Effective leaders demonstrate: 1) Clear communication and active listening, 2) Emotional intelligence and empathy, 3) Vision and strategic thinking, 4) Ability to inspire and motivate others, 5) Integrity and ethical decision-making, 6) Adaptability to change, 7) Delegation and trust in team members, 8) Continuous learning and self-improvement, 9) Accountability for results, and 10) Recognition and development of team potential.",
            "category": "professional",
            "source": "curated_leadership",
            "quality": 0.88
        },
        
        # Reasoning and problem-solving (CommonsenseQA style)
        {
            "input": "Why is it important to back up data regularly?",
            "output": "Regular data backups are crucial because: 1) They protect against hardware failures that can occur unexpectedly, 2) They safeguard against accidental deletion or corruption, 3) They provide recovery options after ransomware or malware attacks, 4) They ensure business continuity during disasters, 5) They preserve important memories and work, and 6) Recovery from a backup is much faster and cheaper than trying to reconstruct lost data.",
            "category": "reasoning",
            "source": "curated_commonsense",
            "quality": 0.90
        },
        {
            "input": "What should I consider when learning a new skill?",
            "output": "When learning a new skill, consider: 1) Start with clear, specific goals, 2) Break the skill into smaller, manageable components, 3) Practice consistently rather than in long, irregular sessions, 4) Seek feedback from experts or peers, 5) Use multiple learning methods (reading, doing, teaching), 6) Be patient with yourself and expect initial struggles, 7) Track your progress to stay motivated, 8) Apply what you learn through real projects, and 9) Connect with a community of learners.",
            "category": "reasoning",
            "source": "curated_learning",
            "quality": 0.90
        },
        
        # Instruction following (Alpaca style)
        {
            "input": "List 5 ways to reduce stress",
            "output": "Here are 5 effective ways to reduce stress:\n\n1. Practice deep breathing exercises or meditation for 10-15 minutes daily\n2. Engage in regular physical exercise, even just a 30-minute walk\n3. Maintain a consistent sleep schedule with 7-9 hours of quality sleep\n4. Connect with friends and family for social support\n5. Take breaks from screens and practice mindfulness or hobbies you enjoy\n\nThese techniques help activate your body's relaxation response and build resilience against stress.",
            "category": "instruction",
            "source": "curated_instruction",
            "quality": 0.92
        },
        {
            "input": "Explain the steps to debug a program",
            "output": "Steps to debug a program:\n\n1. Reproduce the bug: Identify the exact steps that cause the problem\n2. Isolate the issue: Narrow down which part of the code is causing the error\n3. Read error messages: Understand what the error is telling you\n4. Use print statements or a debugger: Track variable values and program flow\n5. Form a hypothesis: Based on evidence, guess what's causing the problem\n6. Test your hypothesis: Make small changes and test them\n7. Fix the bug: Implement the solution\n8. Verify the fix: Ensure the bug is resolved and no new issues were introduced\n9. Document: Note what caused the bug and how you fixed it",
            "category": "instruction",
            "source": "curated_instruction",
            "quality": 0.92
        },
        
        # Knowledge base examples
        {
            "input": "What is cloud computing?",
            "output": "Cloud computing is the delivery of computing services over the internet, including servers, storage, databases, networking, software, and analytics. Instead of owning and maintaining physical servers, users can access these resources on-demand from cloud providers like AWS, Azure, or Google Cloud. Benefits include scalability, cost-effectiveness, accessibility from anywhere, automatic updates, and disaster recovery. Common models include IaaS (Infrastructure as a Service), PaaS (Platform as a Service), and SaaS (Software as a Service).",
            "category": "knowledge",
            "source": "curated_technology",
            "quality": 0.92
        },
        {
            "input": "What is the difference between AI and machine learning?",
            "output": "AI (Artificial Intelligence) is the broader concept of machines being able to carry out tasks in a way that we would consider 'smart' or intelligent. Machine Learning is a specific subset of AI that trains machines to learn from data without being explicitly programmed. Think of it this way: AI is the goal of creating intelligent machines, while machine learning is one of the methods to achieve that goal. Deep learning is a further subset of machine learning using neural networks with multiple layers.",
            "category": "knowledge",
            "source": "curated_technology",
            "quality": 0.92
        },
        
        # Additional diverse examples
        {
            "input": "How do I stay motivated while working on long-term projects?",
            "output": "To stay motivated on long-term projects: 1) Break the project into smaller milestones with clear deadlines, 2) Celebrate small wins along the way, 3) Visualize the end result and benefits regularly, 4) Find an accountability partner or join a community, 5) Track progress visibly (charts, checklists), 6) Maintain work-life balance to avoid burnout, 7) Adjust your approach if progress stalls, 8) Focus on the 'why' behind the project, and 9) Schedule regular reviews to assess and appreciate progress made.",
            "category": "professional",
            "source": "curated_motivation",
            "quality": 0.88
        },
        {
            "input": "What are common data structures in programming?",
            "output": "Common data structures include: 1) Arrays: Fixed-size collections of elements, 2) Linked Lists: Nodes connected by pointers, 3) Stacks: LIFO (Last-In-First-Out) structures, 4) Queues: FIFO (First-In-First-Out) structures, 5) Hash Tables: Key-value pair storage with O(1) average access, 6) Trees: Hierarchical structures (Binary Trees, BST, AVL, etc.), 7) Graphs: Networks of nodes and edges, 8) Heaps: Specialized tree-based structures, and 9) Tries: Tree structures for string operations. Each has specific use cases and performance characteristics.",
            "category": "technical",
            "source": "curated_computer_science",
            "quality": 0.92
        }
    ]
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table already exists with columns: id, category, input_text, output_text, quality_score, created_at
    
    # Get initial count
    cursor.execute("SELECT COUNT(*) FROM training_data")
    initial_count = cursor.fetchone()[0]
    
    print(f"📊 Initial training examples: {initial_count:,}")
    print()
    print(f"📝 Adding {len(training_examples)} curated examples...")
    print()
    
    # Insert training examples
    for i, example in enumerate(training_examples, 1):
        cursor.execute("""
            INSERT INTO training_data (category, input_text, output_text, quality_score)
            VALUES (?, ?, ?, ?)
        """, (
            example["category"],
            example["input"],
            example["output"],
            example["quality"]
        ))
        
        print(f"[{i}/{len(training_examples)}] Added: {example['category']} - {example['input'][:50]}...")
    
    conn.commit()
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM training_data")
    final_count = cursor.fetchone()[0]
    
    # Get category breakdown
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM training_data 
        GROUP BY category 
        ORDER BY count DESC
    """)
    categories = cursor.fetchall()
    
    conn.close()
    
    # Results
    results = {
        "timestamp": datetime.now().isoformat(),
        "initial_count": initial_count,
        "examples_added": len(training_examples),
        "final_count": final_count,
        "categories": dict(categories)
    }
    
    print()
    print("=" * 60)
    print("📊 TRAINING DATA SUMMARY")
    print("=" * 60)
    print(f"✅ Examples added: {len(training_examples)}")
    print(f"💾 Total in database: {final_count:,}")
    print()
    print("📋 Category Breakdown:")
    for category, count in categories:
        print(f"   - {category}: {count} examples")
    print()
    
    # Save report
    report_path = f"curated_training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Report saved: {report_path}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    try:
        result = generate_curated_training_data()
        print()
        print("✨ Curated training data generation completed!")
        print(f"🧠 ARK AI now has {result['final_count']:,} total training examples")
        print()
        print("🎯 Training data includes:")
        print("   - Conversational patterns")
        print("   - Educational Q&A")
        print("   - Technical problem-solving")
        print("   - Professional guidance")
        print("   - Reasoning and common sense")
        print("   - Instruction following")
        print("   - Knowledge base content")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
