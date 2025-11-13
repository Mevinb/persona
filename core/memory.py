"""
ARK Memory Module
=================
Manages conversation history, user preferences, and persistent memory storage.
Supports both short-term (session) and long-term (persistent) memory using SQLite.
"""

import sqlite3
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: Optional[int] = None
    timestamp: Optional[str] = None
    type: str = "conversation"  # conversation, preference, fact, reminder
    user_input: str = ""
    assistant_response: str = ""
    context: Dict[str, Any] = None
    importance: int = 1  # 1-5, 5 being most important
    tags: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now().isoformat()
        if self.context is None:
            self.context = {}
        if self.tags is None:
            self.tags = []


class MemoryManager:
    """
    Manages ARK's memory system including conversation history,
    user preferences, and long-term memories.
    """
    
    def __init__(self, db_path: str = "data/memory.db"):
        """
        Initialize the Memory Manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Session memory (temporary)
        self.session_memory: List[MemoryEntry] = []
        self.current_context: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {}
        
        # Initialize database
        self._init_database()
        self._load_user_preferences()
        
        self.logger.info(f"Memory Manager initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Main memory table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        type TEXT NOT NULL DEFAULT 'conversation',
                        user_input TEXT,
                        assistant_response TEXT,
                        context TEXT,  -- JSON string
                        importance INTEGER DEFAULT 1,
                        tags TEXT,     -- JSON array of tags
                        memory_hash TEXT UNIQUE  -- For deduplication
                    )
                ''')
                
                # User preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        category TEXT DEFAULT 'general',
                        last_updated TEXT
                    )
                ''')
                
                # User facts table (for remembering user details)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fact_type TEXT NOT NULL,  -- name, age, job, hobby, etc.
                        fact_value TEXT NOT NULL,
                        confidence REAL DEFAULT 1.0,
                        last_updated TEXT,
                        source TEXT  -- how we learned this fact
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_facts_type ON user_facts(fact_type)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add_conversation(self, user_input: str, assistant_response: str, 
                        context: Dict[str, Any] = None, importance: int = 1,
                        tags: List[str] = None) -> int:
        """
        Add a conversation exchange to memory.
        
        Args:
            user_input: What the user said
            assistant_response: How Ark responded
            context: Additional context information
            importance: Importance level (1-5)
            tags: List of relevant tags
            
        Returns:
            ID of the stored memory entry
        """
        entry = MemoryEntry(
            type="conversation",
            user_input=user_input,
            assistant_response=assistant_response,
            context=context or {},
            importance=importance,
            tags=tags or []
        )
        
        # Add to session memory
        self.session_memory.append(entry)
        
        # Store in database
        return self._store_memory(entry)
    
    def add_user_fact(self, fact_type: str, fact_value: str, 
                     confidence: float = 1.0, source: str = "conversation"):
        """
        Store a fact about the user.
        
        Args:
            fact_type: Type of fact (name, age, job, hobby, etc.)
            fact_value: The actual fact
            confidence: How confident we are in this fact (0.0-1.0)
            source: How we learned this fact
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update if exists, insert if new
                cursor.execute('''
                    INSERT OR REPLACE INTO user_facts 
                    (fact_type, fact_value, confidence, last_updated, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    fact_type, 
                    fact_value, 
                    confidence, 
                    datetime.datetime.now().isoformat(),
                    source
                ))
                
                conn.commit()
                self.logger.info(f"Stored user fact: {fact_type} = {fact_value}")
                
                # Update session context
                self.current_context[f"user_{fact_type}"] = fact_value
                
        except Exception as e:
            self.logger.error(f"Failed to store user fact: {e}")
    
    def get_user_fact(self, fact_type: str) -> Optional[str]:
        """
        Retrieve a specific user fact.
        
        Args:
            fact_type: Type of fact to retrieve
            
        Returns:
            Fact value if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT fact_value FROM user_facts WHERE fact_type = ? ORDER BY last_updated DESC LIMIT 1',
                    (fact_type,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve user fact {fact_type}: {e}")
            return None
    
    def get_all_user_facts(self) -> Dict[str, str]:
        """Get all known facts about the user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT fact_type, fact_value, confidence 
                    FROM user_facts 
                    WHERE confidence > 0.5
                    ORDER BY last_updated DESC
                ''')
                
                facts = {}
                for row in cursor.fetchall():
                    facts[row[0]] = row[1]
                
                return facts
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve user facts: {e}")
            return {}
    
    def set_preference(self, key: str, value: Any, category: str = "general"):
        """
        Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
            category: Category of preference
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (key, value, category, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (
                    key, 
                    json.dumps(value), 
                    category, 
                    datetime.datetime.now().isoformat()
                ))
                conn.commit()
                
            # Update session preferences
            self.user_preferences[key] = value
            self.logger.info(f"Set preference: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set preference {key}: {e}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        return self.user_preferences.get(key, default)
    
    def _load_user_preferences(self):
        """Load user preferences from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT key, value FROM user_preferences')
                
                for row in cursor.fetchall():
                    key, value_json = row
                    try:
                        self.user_preferences[key] = json.loads(value_json)
                    except json.JSONDecodeError:
                        self.user_preferences[key] = value_json
                        
                self.logger.info(f"Loaded {len(self.user_preferences)} user preferences")
                
        except Exception as e:
            self.logger.error(f"Failed to load user preferences: {e}")
    
    def _store_memory(self, entry: MemoryEntry) -> int:
        """Store a memory entry in the database."""
        try:
            # Create memory hash for deduplication
            memory_hash = self._create_memory_hash(entry)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO memories 
                    (timestamp, type, user_input, assistant_response, context, importance, tags, memory_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.timestamp,
                    entry.type,
                    entry.user_input,
                    entry.assistant_response,
                    json.dumps(entry.context),
                    entry.importance,
                    json.dumps(entry.tags),
                    memory_hash
                ))
                
                memory_id = cursor.lastrowid
                conn.commit()
                
                if memory_id:
                    entry.id = memory_id
                    self.logger.debug(f"Stored memory entry with ID: {memory_id}")
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            return 0
    
    def _create_memory_hash(self, entry: MemoryEntry) -> str:
        """Create a hash for memory deduplication."""
        content = f"{entry.user_input}|{entry.assistant_response}|{entry.type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations from memory.
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        conversations = []
        
        # Add session memory first
        for entry in self.session_memory[-limit:]:
            if entry.type == "conversation":
                conversations.append({
                    "user": entry.user_input,
                    "assistant": entry.assistant_response,
                    "timestamp": entry.timestamp,
                    "context": entry.context
                })
        
        # Fill from database if needed
        if len(conversations) < limit:
            remaining = limit - len(conversations)
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT user_input, assistant_response, timestamp, context
                        FROM memories 
                        WHERE type = 'conversation' AND user_input IS NOT NULL
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (remaining,))
                    
                    for row in cursor.fetchall():
                        context = {}
                        try:
                            context = json.loads(row[3]) if row[3] else {}
                        except json.JSONDecodeError:
                            pass
                            
                        conversations.append({
                            "user": row[0],
                            "assistant": row[1],
                            "timestamp": row[2],
                            "context": context
                        })
                        
            except Exception as e:
                self.logger.error(f"Failed to retrieve conversations: {e}")
        
        return conversations[-limit:]  # Most recent first
    
    def search_memories(self, query: str, memory_type: str = None, 
                       limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search through memories using simple text matching.
        
        Args:
            query: Search query
            memory_type: Filter by memory type
            limit: Maximum results to return
            
        Returns:
            List of matching memories
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                sql = '''
                    SELECT id, timestamp, type, user_input, assistant_response, context, importance, tags
                    FROM memories 
                    WHERE (user_input LIKE ? OR assistant_response LIKE ?)
                '''
                params = [f"%{query}%", f"%{query}%"]
                
                if memory_type:
                    sql += " AND type = ?"
                    params.append(memory_type)
                
                sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                
                results = []
                for row in cursor.fetchall():
                    context = {}
                    tags = []
                    try:
                        context = json.loads(row[5]) if row[5] else {}
                        tags = json.loads(row[7]) if row[7] else []
                    except json.JSONDecodeError:
                        pass
                    
                    results.append({
                        "id": row[0],
                        "timestamp": row[1],
                        "type": row[2],
                        "user_input": row[3],
                        "assistant_response": row[4],
                        "context": context,
                        "importance": row[6],
                        "tags": tags
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_context_for_prompt(self) -> Dict[str, Any]:
        """
        Get relevant context for prompt generation.
        
        Returns:
            Dictionary containing user facts, preferences, and recent context
        """
        context = {
            "user_facts": self.get_all_user_facts(),
            "preferences": self.user_preferences.copy(),
            "session_context": self.current_context.copy()
        }
        
        return context
    
    def update_session_context(self, key: str, value: Any):
        """Update the current session context."""
        self.current_context[key] = value
        self.logger.debug(f"Updated session context: {key} = {value}")
    
    def clear_session_memory(self):
        """Clear the current session memory."""
        self.session_memory.clear()
        self.current_context.clear()
        self.logger.info("Session memory cleared")
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about stored memories."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total memories
                cursor.execute('SELECT COUNT(*) FROM memories')
                total_memories = cursor.fetchone()[0]
                
                # Memories by type
                cursor.execute('SELECT type, COUNT(*) FROM memories GROUP BY type')
                by_type = dict(cursor.fetchall())
                
                # User facts
                cursor.execute('SELECT COUNT(*) FROM user_facts')
                user_facts_count = cursor.fetchone()[0]
                
                # Preferences
                cursor.execute('SELECT COUNT(*) FROM user_preferences')
                preferences_count = cursor.fetchone()[0]
                
                return {
                    "total_memories": total_memories,
                    "conversation_memories": by_type.get("conversation", 0),
                    "other_memories": sum(v for k, v in by_type.items() if k != "conversation"),
                    "user_facts": user_facts_count,
                    "preferences": preferences_count,
                    "session_memories": len(self.session_memory)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {}


if __name__ == "__main__":
    # Test the Memory Manager
    logging.basicConfig(level=logging.INFO)
    
    memory = MemoryManager("test_memory.db")
    
    # Test conversation storage
    memory.add_conversation(
        "Hello, my name is John",
        "Nice to meet you, John! I'm Ark.",
        context={"intent": "greeting"},
        importance=3,
        tags=["greeting", "introduction"]
    )
    
    # Test user fact storage
    memory.add_user_fact("name", "John", confidence=1.0, source="direct_statement")
    memory.add_user_fact("job", "software developer", confidence=0.8, source="conversation")
    
    # Test preference storage
    memory.set_preference("preferred_voice", "female", "speech")
    memory.set_preference("temperature_unit", "celsius", "general")
    
    # Test retrieval
    print("User's name:", memory.get_user_fact("name"))
    print("User facts:", memory.get_all_user_facts())
    print("Recent conversations:", memory.get_recent_conversations(2))
    print("Memory stats:", memory.get_memory_stats())
    print("Context for prompt:", memory.get_context_for_prompt())