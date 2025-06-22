import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import settings
from .logger import get_logger

logger = get_logger('database')


class DatabaseManager:
    """Manages SQLite database operations for AI Boardroom discussions."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with optional custom database path."""
        if db_path:
            self.db_path = db_path
        else:
            # Use database_url from config or default to local SQLite file
            db_url = getattr(settings, 'database_url', None)
            if db_url and db_url.startswith('sqlite:///'):
                self.db_path = db_url.replace('sqlite:///', '')
            else:
                # Default to local database file
                self.db_path = os.path.join(os.getcwd(), 'ai_boardroom.db')
        
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create discussions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS discussions (
                        id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        current_turn INTEGER DEFAULT 0,
                        current_phase TEXT DEFAULT 'opening',
                        phase_turns INTEGER DEFAULT 0,
                        phase_limits TEXT,  -- JSON string
                        turn_order TEXT,    -- JSON string
                        personas TEXT,      -- JSON string
                        status TEXT DEFAULT 'active'
                    )
                ''')
                
                # Create messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        discussion_id TEXT NOT NULL,
                        persona TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        phase TEXT NOT NULL,
                        turn_number INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (discussion_id) REFERENCES discussions (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_messages_discussion_id 
                    ON messages (discussion_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_messages_turn_number 
                    ON messages (discussion_id, turn_number)
                ''')
                
                conn.commit()
                logger.info(f"Database initialized successfully at: {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_discussion(self, discussion_data: Dict[str, Any]) -> bool:
        """Save or update a discussion in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract data
                discussion_id = discussion_data['id']
                topic = discussion_data['topic']
                current_turn = discussion_data.get('current_turn', 0)
                current_phase = discussion_data.get('current_phase')
                phase_turns = discussion_data.get('phase_turns', 0)
                phase_limits = json.dumps(discussion_data.get('phase_limits', {}))
                turn_order = json.dumps(discussion_data.get('turn_order', []))
                personas = json.dumps([
                    {
                        'name': p.name,
                        'model': p.model,
                        'role': p.role,
                        'personality': p.personality,
                        'expertise': p.expertise
                    } for p in discussion_data.get('personas', [])
                ])
                
                # Convert enum to string if needed
                current_phase_str = current_phase.value if hasattr(current_phase, 'value') else str(current_phase)
                
                # Check if discussion exists
                cursor.execute('SELECT id FROM discussions WHERE id = ?', (discussion_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing discussion
                    cursor.execute('''
                        UPDATE discussions 
                        SET topic = ?, current_turn = ?, current_phase = ?, 
                            phase_turns = ?, phase_limits = ?, turn_order = ?, 
                            personas = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (topic, current_turn, current_phase_str, phase_turns, 
                          phase_limits, turn_order, personas, discussion_id))
                else:
                    # Insert new discussion
                    cursor.execute('''
                        INSERT INTO discussions 
                        (id, topic, current_turn, current_phase, phase_turns, 
                         phase_limits, turn_order, personas)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (discussion_id, topic, current_turn, current_phase_str, 
                          phase_turns, phase_limits, turn_order, personas))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error saving discussion {discussion_id}: {e}")
            return False
    
    def save_message(self, discussion_id: str, message_data: Dict[str, Any]) -> bool:
        """Save a message to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO messages 
                    (discussion_id, persona, role, content, phase, turn_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    discussion_id,
                    message_data.get('persona', ''),
                    message_data.get('role', ''),
                    message_data.get('content', ''),
                    message_data.get('phase', ''),
                    int(message_data.get('turn', 0))
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error saving message for discussion {discussion_id}: {e}")
            return False
    
    def load_discussion(self, discussion_id: str) -> Optional[Dict[str, Any]]:
        """Load a discussion from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Load discussion data
                cursor.execute('''
                    SELECT id, topic, current_turn, current_phase, phase_turns,
                           phase_limits, turn_order, personas, created_at, updated_at
                    FROM discussions WHERE id = ?
                ''', (discussion_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                discussion_data = {
                    'id': row[0],
                    'topic': row[1],
                    'current_turn': row[2],
                    'current_phase': row[3],
                    'phase_turns': row[4],
                    'phase_limits': json.loads(row[5]) if row[5] else {},
                    'turn_order': json.loads(row[6]) if row[6] else [],
                    'personas_data': json.loads(row[7]) if row[7] else [],
                    'created_at': row[8],
                    'updated_at': row[9]
                }
                
                # Load messages
                cursor.execute('''
                    SELECT persona, role, content, phase, turn_number, created_at
                    FROM messages 
                    WHERE discussion_id = ?
                    ORDER BY turn_number
                ''', (discussion_id,))
                
                messages = []
                for msg_row in cursor.fetchall():
                    messages.append({
                        'persona': msg_row[0],
                        'role': msg_row[1],
                        'content': msg_row[2],
                        'phase': msg_row[3],
                        'turn': msg_row[4],
                        'timestamp': msg_row[5]
                    })
                
                discussion_data['messages'] = messages
                return discussion_data
                
        except sqlite3.Error as e:
            logger.error(f"Error loading discussion {discussion_id}: {e}")
            return None
    
    def list_discussions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent discussions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT d.id, d.topic, d.created_at, d.updated_at, d.status,
                           COUNT(m.id) as message_count
                    FROM discussions d
                    LEFT JOIN messages m ON d.id = m.discussion_id
                    GROUP BY d.id, d.topic, d.created_at, d.updated_at, d.status
                    ORDER BY d.updated_at DESC
                    LIMIT ?
                ''', (limit,))
                
                discussions = []
                for row in cursor.fetchall():
                    discussions.append({
                        'id': row[0],
                        'topic': row[1],
                        'created_at': row[2],
                        'updated_at': row[3],
                        'status': row[4],
                        'message_count': row[5]
                    })
                
                return discussions
                
        except sqlite3.Error as e:
            logger.error(f"Error listing discussions: {e}")
            return []
    
    def delete_discussion(self, discussion_id: str) -> bool:
        """Delete a discussion and all its messages."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first (foreign key constraint)
                cursor.execute('DELETE FROM messages WHERE discussion_id = ?', (discussion_id,))
                
                # Delete discussion
                cursor.execute('DELETE FROM discussions WHERE id = ?', (discussion_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting discussion {discussion_id}: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count discussions
                cursor.execute('SELECT COUNT(*) FROM discussions')
                discussion_count = cursor.fetchone()[0]
                
                # Count messages
                cursor.execute('SELECT COUNT(*) FROM messages')
                message_count = cursor.fetchone()[0]
                
                # Get database file size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'discussions': discussion_count,
                    'messages': message_count,
                    'db_size_bytes': db_size,
                    'db_size_mb': round(db_size / (1024 * 1024), 2)
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting database stats: {e}")
            return {'discussions': 0, 'messages': 0, 'db_size_bytes': 0, 'db_size_mb': 0}


def test_database():
    """Test database functionality."""
    print("Testing Database Manager")
    print("=" * 40)
    
    # Create test database
    db_manager = DatabaseManager("test_ai_boardroom.db")
    
    # Test saving discussion
    from .debate import DiscussionPhase
    from .personas import PersonaManager
    
    persona_manager = PersonaManager()
    personas = persona_manager.get_all_personas()
    
    test_discussion = {
        'id': 'test_discussion_1',
        'topic': 'Should we hire more developers?',
        'current_turn': 2,
        'current_phase': DiscussionPhase.DEBATE,
        'phase_turns': 1,
        'phase_limits': {
            DiscussionPhase.OPENING: 2,
            DiscussionPhase.DEBATE: 4,
            DiscussionPhase.SYNTHESIS: 2
        },
        'turn_order': ['CEO', 'CTO', 'CMO'],
        'personas': personas
    }
    
    print("1. Saving test discussion...")
    success = db_manager.save_discussion(test_discussion)
    print(f"Save result: {success}")
    
    # Test saving message
    test_message = {
        'persona': 'Alexandra Stone',
        'role': 'CEO',
        'content': 'We need to consider the strategic implications of this decision.',
        'phase': 'opening',
        'turn': 1
    }
    
    print("2. Saving test message...")
    success = db_manager.save_message('test_discussion_1', test_message)
    print(f"Save message result: {success}")
    
    # Test loading discussion
    print("3. Loading discussion...")
    loaded = db_manager.load_discussion('test_discussion_1')
    if loaded:
        print(f"Loaded discussion: {loaded['topic']}")
        print(f"Messages: {len(loaded['messages'])}")
    else:
        print("Failed to load discussion")
    
    # Test listing discussions
    print("4. Listing discussions...")
    discussions = db_manager.list_discussions()
    for disc in discussions:
        print(f"- {disc['id']}: {disc['topic']} ({disc['message_count']} messages)")
    
    # Test database stats
    print("5. Database stats...")
    stats = db_manager.get_database_stats()
    print(f"Discussions: {stats['discussions']}")
    print(f"Messages: {stats['messages']}")
    print(f"Database size: {stats['db_size_mb']} MB")
    
    # Cleanup
    db_manager.delete_discussion('test_discussion_1')
    if os.path.exists("test_ai_boardroom.db"):
        os.remove("test_ai_boardroom.db")
    print("Test completed and cleaned up.")


if __name__ == "__main__":
    test_database()