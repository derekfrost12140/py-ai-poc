import sqlite3
import os

def init_database():
    """Initialize SQLite database with sample data"""
    
    # Ensure db directory exists
    os.makedirs('db', exist_ok=True)
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('db/test.db')
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample users
        sample_users = [
            ('Alice Johnson', 'alice@example.com'),
            ('Bob Smith', 'bob@example.com'),
            ('Carol Davis', 'carol@example.com'),
            ('David Wilson', 'david@example.com'),
            ('Eva Brown', 'eva@example.com')
        ]
        
        # Use INSERT OR IGNORE to avoid duplicates
        cursor.executemany('''
            INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)
        ''', sample_users)
        
        # Commit changes
        conn.commit()
        
        print("✅ Database initialized successfully!")
        print(f"📁 Database file: {os.path.abspath('db/test.db')}")
        
        # Show created data
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        print(f"👥 Created {len(users)} users:")
        for user in users:
            print(f"  - {user[1]} ({user[2]})")
        
        # Show table schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Table schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 