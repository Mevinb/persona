"""
Continuous Learning Monitor
==========================
Background service that monitors ARK's performance and continuously improves capabilities.
"""

import time
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import os
from collections import defaultdict

class ContinuousLearningMonitor:
    """Monitors ARK performance and triggers learning improvements."""
    
    def __init__(self):
        self.monitoring_active = False
        self.learning_interval = 600  # Learn every 10 minutes
        self.performance_threshold = 0.7
        
        # Performance tracking
        self.response_quality_scores = []
        self.user_satisfaction_scores = []
        self.capability_usage_stats = defaultdict(int)
        
        # Learning triggers
        self.learning_triggers = {
            "poor_performance": 3,  # After 3 poor responses
            "new_pattern": 5,       # After 5 similar queries
            "user_feedback": 1,     # Immediate on feedback
            "knowledge_gap": 2      # After 2 failed responses
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Start continuous monitoring."""
        
        if self.monitoring_active:
            print("⚠️  Monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        # Start learning thread
        learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        learning_thread.start()
        
        print("🔄 Continuous Learning Monitor started")
        print(f"📊 Learning interval: {self.learning_interval} seconds")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        
        self.monitoring_active = False
        print("🛑 Continuous Learning Monitor stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        
        while self.monitoring_active:
            try:
                # Monitor performance metrics
                self._check_performance_metrics()
                
                # Check for learning triggers
                self._check_learning_triggers()
                
                # Update capability statistics
                self._update_capability_stats()
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    def _learning_loop(self):
        """Dedicated learning loop."""
        
        while self.monitoring_active:
            try:
                # Trigger learning cycle
                self._trigger_learning_cycle()
                
                # Sleep for learning interval
                time.sleep(self.learning_interval)
                
            except Exception as e:
                self.logger.error(f"Learning loop error: {e}")
    
    def _check_performance_metrics(self):
        """Check current performance metrics."""
        
        try:
            db_path = "data/ark_complete_training.db"
            if not os.path.exists(db_path):
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check recent performance
            cursor.execute("""
                SELECT metric_type, value, date_measured 
                FROM performance_metrics 
                WHERE date_measured >= date('now', '-1 day')
                ORDER BY date_measured DESC
            """)
            
            recent_metrics = cursor.fetchall()
            
            if recent_metrics:
                # Analyze performance trends
                response_lengths = [m[1] for m in recent_metrics if m[0] == 'response_length']
                
                if response_lengths:
                    avg_response_length = sum(response_lengths) / len(response_lengths)
                    
                    if avg_response_length < 200:
                        self._trigger_improvement("short_responses", {
                            "avg_length": avg_response_length,
                            "sample_size": len(response_lengths)
                        })
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Performance check error: {e}")
    
    def _check_learning_triggers(self):
        """Check if learning should be triggered."""
        
        # Check conversation history for patterns
        try:
            conv_path = "data/conversation_history.json"
            if os.path.exists(conv_path):
                with open(conv_path, 'r') as f:
                    conversations = json.load(f)
                
                # Analyze recent conversations
                recent_convs = [c for c in conversations if self._is_recent(c['timestamp'])]
                
                if len(recent_convs) >= 10:
                    self._analyze_conversation_patterns(recent_convs)
        
        except Exception as e:
            self.logger.error(f"Learning trigger check error: {e}")
    
    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours."""
        
        try:
            conv_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            cutoff = datetime.now() - timedelta(hours=hours)
            return conv_time > cutoff
        except:
            return False
    
    def _analyze_conversation_patterns(self, conversations: List[Dict]):
        """Analyze conversation patterns for learning opportunities."""
        
        # Group by category
        category_groups = defaultdict(list)
        for conv in conversations:
            category = conv.get('category', 'general')
            category_groups[category].append(conv)
        
        # Check for patterns that need improvement
        for category, convs in category_groups.items():
            if len(convs) >= 5:
                
                # Check response quality
                short_responses = [c for c in convs if len(c['ark_response']) < 150]
                
                if len(short_responses) >= 3:
                    self._trigger_improvement("category_needs_enhancement", {
                        "category": category,
                        "poor_response_count": len(short_responses),
                        "total_responses": len(convs)
                    })
    
    def _trigger_improvement(self, trigger_type: str, context: Dict):
        """Trigger specific improvements."""
        
        print(f"🎯 Learning trigger: {trigger_type}")
        print(f"📝 Context: {context}")
        
        # Log the trigger
        self._log_learning_trigger(trigger_type, context)
        
        # Execute specific improvements
        if trigger_type == "short_responses":
            self._improve_response_depth(context)
        elif trigger_type == "category_needs_enhancement":
            self._enhance_category_training(context)
    
    def _improve_response_depth(self, context: Dict):
        """Improve response depth and quality."""
        
        # Add training data for more detailed responses
        enhanced_training = [
            {
                "category": "detailed_responses",
                "input_text": "provide comprehensive help with my request",
                "output_text": """🎯 **Comprehensive Assistance Framework**

**UNDERSTANDING YOUR REQUEST:**
• Detailed analysis of what you need
• Context consideration and background
• Multiple perspective assessment
• Goal clarification and scope definition

**COMPREHENSIVE SOLUTION APPROACH:**
✓ Step-by-step methodology
✓ Multiple solution options
✓ Detailed explanations and rationale
✓ Supporting resources and references
✓ Implementation guidance
✓ Troubleshooting considerations

**QUALITY ASSURANCE:**
• Thorough coverage of all aspects
• Clear and actionable guidance
• Relevant examples and illustrations
• Follow-up recommendations
• Success metrics and evaluation

**ADDITIONAL SUPPORT:**
• Related resources and tools
• Best practices and expert tips
• Common pitfalls to avoid
• Advanced techniques when applicable

Let me know what specific area you'd like comprehensive help with, and I'll provide detailed, thorough assistance tailored to your needs.""",
                "quality_score": 0.95,
                "learned_from": "depth_improvement"
            }
        ]
        
        self._save_improvement_training(enhanced_training)
        print(f"✅ Added depth improvement training")
    
    def _enhance_category_training(self, context: Dict):
        """Enhance training for specific categories."""
        
        category = context.get('category', 'general')
        
        # Category-specific enhancements
        category_enhancements = {
            "academic": {
                "input": f"advanced help with {category} topics",
                "output": f"""📚 **Advanced {category.title()} Support System**

**COMPREHENSIVE LEARNING APPROACH:**

**Foundation Assessment:**
• Current knowledge level evaluation
• Learning style identification
• Goal setting and milestone planning
• Resource requirement analysis

**Advanced Learning Strategy:**
✓ Multi-modal learning techniques
✓ Progressive complexity building
✓ Practical application focus
✓ Regular progress assessment
✓ Adaptive learning pathways

**EXPERT-LEVEL GUIDANCE:**
• In-depth concept explanations
• Advanced problem-solving techniques
• Critical thinking development
• Research methodology guidance
• Academic writing excellence

**PERFORMANCE OPTIMIZATION:**
• Study efficiency techniques
• Memory enhancement strategies
• Time management optimization
• Stress management during learning
• Motivation maintenance systems

**ONGOING SUPPORT:**
• Regular check-ins and adjustments
• Advanced resource recommendations
• Peer learning opportunities
• Expert consultation guidance
• Long-term learning planning

What specific advanced {category} topics would you like to explore in depth?"""
            },
            "task_management": {
                "input": f"comprehensive {category} system",
                "output": f"""⚡ **Advanced {category.title()} Framework**

**STRATEGIC PLANNING PHASE:**

**System Assessment:**
• Current workflow analysis
• Bottleneck identification
• Efficiency gap analysis
• Resource optimization opportunities

**ADVANCED ORGANIZATION:**
✓ Multi-level prioritization systems
✓ Dynamic scheduling frameworks
✓ Automated workflow integration
✓ Cross-platform synchronization
✓ Performance analytics tracking

**OPTIMIZATION TECHNIQUES:**
• Advanced time-blocking strategies
• Energy management alignment
• Cognitive load optimization
• Interruption management protocols
• Flow state cultivation methods

**SCALABILITY FEATURES:**
• Team collaboration integration
• Project portfolio management
• Long-term goal alignment
• Adaptive capacity planning
• Continuous improvement cycles

**MASTERY DEVELOPMENT:**
• Advanced productivity methodologies
• Custom system development
• Leadership and delegation skills
• Strategic thinking enhancement
• Innovation and creativity integration

How can I help you build a world-class {category} system?"""
            }
        }
        
        if category in category_enhancements:
            template = category_enhancements[category]
            
            enhanced_training = [{
                "category": f"enhanced_{category}",
                "input_text": template['input'],
                "output_text": template['output'],
                "quality_score": 0.9,
                "learned_from": f"category_enhancement_{category}"
            }]
            
            self._save_improvement_training(enhanced_training)
            print(f"✅ Enhanced {category} category training")
    
    def _save_improvement_training(self, training_data: List[Dict]):
        """Save improvement training to database."""
        
        try:
            db_path = "data/ark_complete_training.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for example in training_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO training_data (category, input_text, output_text, quality_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    example['category'],
                    example['input_text'],
                    example['output_text'],
                    example['quality_score']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving improvement training: {e}")
    
    def _log_learning_trigger(self, trigger_type: str, context: Dict):
        """Log learning triggers for analysis."""
        
        trigger_log = {
            "timestamp": datetime.now().isoformat(),
            "trigger_type": trigger_type,
            "context": context,
            "action_taken": True
        }
        
        # Save to learning insights
        try:
            db_path = "data/ark_complete_training.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO learning_insights (insight_type, description, confidence, supporting_evidence, action_taken)
                VALUES (?, ?, ?, ?, ?)
            """, (
                trigger_type,
                f"Triggered learning improvement for {trigger_type}",
                0.8,
                json.dumps(context),
                "Enhanced training data added"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging learning trigger: {e}")
    
    def _trigger_learning_cycle(self):
        """Trigger a complete learning cycle."""
        
        try:
            # Import and trigger learning engine
            from ark_self_learning_engine import SelfLearningEngine
            
            learning_engine = SelfLearningEngine()
            
            # Check if there's data to learn from
            status = learning_engine.get_learning_status()
            
            if (status.get('conversation_buffer_size', 0) > 0 or 
                status.get('feedback_buffer_size', 0) > 0):
                
                print(f"🔄 Triggering learning cycle...")
                learning_engine.force_learning_cycle()
                
                # Update statistics
                self._update_learning_stats()
        
        except Exception as e:
            self.logger.error(f"Learning cycle trigger error: {e}")
    
    def _update_capability_stats(self):
        """Update capability usage statistics."""
        
        # This would track which capabilities are used most
        # For now, we'll just log the update
        self.logger.info("Capability statistics updated")
    
    def _update_learning_stats(self):
        """Update learning statistics."""
        
        try:
            stats_path = "data/continuous_learning_stats.json"
            
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {
                    "total_learning_cycles": 0,
                    "improvements_made": 0,
                    "last_learning_time": None,
                    "performance_improvements": []
                }
            
            stats['total_learning_cycles'] += 1
            stats['improvements_made'] += 1
            stats['last_learning_time'] = datetime.now().isoformat()
            
            improvement_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "automatic_learning",
                "description": "Continuous learning cycle completed"
            }
            stats['performance_improvements'].append(improvement_entry)
            
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Error updating learning stats: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status."""
        
        return {
            "monitoring_active": self.monitoring_active,
            "learning_interval": self.learning_interval,
            "performance_threshold": self.performance_threshold,
            "response_quality_samples": len(self.response_quality_scores),
            "satisfaction_samples": len(self.user_satisfaction_scores)
        }


def start_continuous_learning():
    """Start the continuous learning system."""
    
    print("🚀 STARTING CONTINUOUS LEARNING SYSTEM")
    print("=" * 45)
    
    # Initialize and start monitor
    monitor = ContinuousLearningMonitor()
    monitor.start_monitoring()
    
    print("✅ Continuous learning system is now active!")
    print("🔄 ARK will automatically improve based on usage patterns")
    print("📊 Learning cycles will run every 10 minutes")
    print("🧠 Performance monitoring active")
    
    try:
        # Keep the system running
        while True:
            status = monitor.get_monitoring_status()
            print(f"\n📊 Monitor Status: {datetime.now().strftime('%H:%M:%S')}")
            for key, value in status.items():
                print(f"   {key}: {value}")
            
            time.sleep(300)  # Status update every 5 minutes
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping continuous learning...")
        monitor.stop_monitoring()
        print("✅ Continuous learning system stopped")


if __name__ == "__main__":
    start_continuous_learning()