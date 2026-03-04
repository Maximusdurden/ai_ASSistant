import sqlite3
from datetime import datetime

DB_PATH = "agent_memory.db"

def init_db():
    """Initializes the SQLite database and creates the memories table."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create an index on the category for faster semantic filtering later
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON memories(category)')
        conn.commit()

def add_memory(category: str, content: str):
    """Inserts a new memory into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO memories (category, content) VALUES (?, ?)',
            (category, content)
        )
        conn.commit()

def get_all_memories() -> str:
    """Retrieves all memories, formatted as a string to inject into the prompt."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT category, content, created_at FROM memories ORDER BY created_at ASC')
        rows = cursor.fetchall()
        
    if not rows:
        return "No persistent memories found."
        
    memory_string = "## Persistent Memories\n"
    for row in rows:
        category, content, timestamp = row
        # Formatting it cleanly so the LLM understands the context
        memory_string += f"- [{timestamp}] ({category.upper()}): {content}\n"
        
    return memory_string

# Initialize the database when this module is imported
init_db()