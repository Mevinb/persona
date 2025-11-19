#!/usr/bin/env python3
"""
Simple Wikipedia Training Module
=================================
Adds educational content from Wikipedia to the ARK AI training database.
"""

import sqlite3
import os
import json
from datetime import datetime
import wikipedia

def add_wikipedia_training_data():
    """Add educational content from Wikipedia to training database."""
    
    print("=" * 60)
    print("📚 Adding Wikipedia Educational Content")
    print("=" * 60)
    print()
    
    # Database setup
    db_path = "data/ark_complete_training.db"
    os.makedirs("data", exist_ok=True)
    
    # Educational topics to fetch
    topics = [
        "Artificial intelligence",
        "Machine learning",
        "Natural language processing",
        "Deep learning",
        "Neural network",
        "Computer science",
        "Programming",
        "Python (programming language)",
        "Data science",
        "Algorithm",
        "Software engineering",
        "Web development",
        "Database",
        "Operating system",
        "Computer network",
        "Cybersecurity",
        "Cloud computing",
        "Quantum computing",
        "Robotics",
        "Computer vision",
        "Speech recognition",
        "Knowledge representation",
        "Expert system",
        "Cognitive science",
        "Information theory"
    ]
    
    results = {
        "start_time": datetime.now().isoformat(),
        "topics_processed": 0,
        "examples_added": 0,
        "errors": []
    }
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input TEXT NOT NULL,
            output TEXT NOT NULL,
            category TEXT,
            source TEXT,
            quality_score REAL DEFAULT 0.8,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    print("📥 Fetching Wikipedia articles...")
    print()
    
    for i, topic in enumerate(topics, 1):
        try:
            print(f"[{i}/{len(topics)}] Processing: {topic}")
            
            # Fetch Wikipedia page
            page = wikipedia.page(topic, auto_suggest=False)
            
            # Create training examples from the content
            summary = page.summary
            
            # Add as Q&A pairs
            examples = [
                {
                    "input": f"What is {topic.lower()}?",
                    "output": summary[:500] + "..." if len(summary) > 500 else summary,
                    "category": "knowledge",
                    "source": f"Wikipedia:{topic}"
                },
                {
                    "input": f"Explain {topic.lower()}",
                    "output": summary[:800] + "..." if len(summary) > 800 else summary,
                    "category": "knowledge",
                    "source": f"Wikipedia:{topic}"
                },
                {
                    "input": f"Tell me about {topic.lower()}",
                    "output": summary,
                    "category": "knowledge",
                    "source": f"Wikipedia:{topic}"
                }
            ]
            
            # Insert into database
            for example in examples:
                cursor.execute("""
                    INSERT INTO training_data (input, output, category, source, quality_score)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    example["input"],
                    example["output"],
                    example["category"],
                    example["source"],
                    0.9
                ))
            
            conn.commit()
            results["examples_added"] += len(examples)
            results["topics_processed"] += 1
            
            print(f"   ✅ Added {len(examples)} examples")
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Try the first option from disambiguation
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                summary = page.summary
                
                example = {
                    "input": f"What is {topic.lower()}?",
                    "output": summary[:500] + "..." if len(summary) > 500 else summary,
                    "category": "knowledge",
                    "source": f"Wikipedia:{topic}"
                }
                
                cursor.execute("""
                    INSERT INTO training_data (input, output, category, source, quality_score)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    example["input"],
                    example["output"],
                    example["category"],
                    example["source"],
                    0.85
                ))
                
                conn.commit()
                results["examples_added"] += 1
                results["topics_processed"] += 1
                print(f"   ✅ Added 1 example (disambiguated)")
                
            except Exception as e2:
                results["errors"].append(f"{topic}: {str(e2)[:100]}")
                print(f"   ⚠️  Skipped (disambiguation issue)")
                
        except Exception as e:
            results["errors"].append(f"{topic}: {str(e)[:100]}")
            print(f"   ⚠️  Skipped ({str(e)[:50]})")
    
    conn.close()
    
    # Final statistics
    results["end_time"] = datetime.now().isoformat()
    
    # Get total examples in database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM training_data")
    total_examples = cursor.fetchone()[0]
    conn.close()
    
    results["total_examples_in_db"] = total_examples
    
    print()
    print("=" * 60)
    print("📊 WIKIPEDIA TRAINING SUMMARY")
    print("=" * 60)
    print(f"✅ Topics processed: {results['topics_processed']}/{len(topics)}")
    print(f"📚 Examples added: {results['examples_added']}")
    print(f"💾 Total in database: {results['total_examples_in_db']:,}")
    print()
    
    if results["errors"]:
        print(f"⚠️  Errors encountered: {len(results['errors'])}")
    
    # Save report
    report_path = f"wikipedia_training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Report saved: {report_path}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    try:
        result = add_wikipedia_training_data()
        print()
        print("✨ Wikipedia training completed successfully!")
        print(f"🧠 ARK AI now has {result['examples_added']} additional examples from Wikipedia")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
