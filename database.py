import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Try importing psycopg2 for cloud PostgreSQL support
try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES_LIB = True
except ImportError:
    HAS_POSTGRES_LIB = False

DB_PATH = "resume_analyzer.db"
DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = HAS_POSTGRES_LIB and len(DATABASE_URL.strip()) > 0

def get_db_connection():
    """
    Establishes a connection to the SQLite database locally,
    or PostgreSQL database (Supabase) in production.
    """
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name locally
        return conn

def get_cursor(conn):
    """
    Returns a cursor. If in PostgreSQL, returns a cursor 
    that auto-serializes output rows into dictionaries.
    """
    if IS_POSTGRES:
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn.cursor()

def format_query(query: str) -> str:
    """
    Dynamically translates query parameter placeholders.
    SQLite uses '?', PostgreSQL uses '%s'.
    """
    if IS_POSTGRES:
        return query.replace("?", "%s")
    return query

def init_db():
    """
    Initializes the database schema for users and history.
    Detects whether to use SQLite or PostgreSQL syntax.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        # Create Users table (PostgreSQL syntax)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create History table (PostgreSQL syntax)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                resume_name VARCHAR(255) NOT NULL,
                job_title VARCHAR(255) NOT NULL,
                job_description TEXT NOT NULL,
                ats_score INTEGER NOT NULL,
                analysis_results TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
    else:
        # Create Users table (SQLite syntax)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create History table (SQLite syntax)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resume_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                job_description TEXT NOT NULL,
                ats_score INTEGER NOT NULL,
                analysis_results TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
    conn.commit()
    conn.close()

# User Management Database Operations

def create_user(username: str, email: str, password_hash: str) -> bool:
    """
    Inserts a new user into the database. Returns True if successful, False if username exists.
    """
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        query = format_query("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)")
        cursor.execute(query, (username, email, password_hash))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def get_user(username: str) -> Optional[Dict]:
    """
    Retrieves user profile data by username.
    """
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        query = format_query("SELECT * FROM users WHERE username = ?")
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()

def update_user_password(user_id: int, new_password_hash: str) -> bool:
    """
    Updates the password hash for a user.
    """
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        query = format_query("UPDATE users SET password_hash = ? WHERE id = ?")
        cursor.execute(query, (new_password_hash, user_id))
        conn.commit()
        rows_affected = cursor.rowcount
        return rows_affected > 0
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        conn.close()

# Resume Analysis History Operations

def save_analysis(user_id: int, resume_name: str, job_title: str, job_description: str, ats_score: int, analysis_results: Dict) -> bool:
    """
    Saves a resume analysis result to the database.
    """
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        query = format_query("""
            INSERT INTO history (user_id, resume_name, job_title, job_description, ats_score, analysis_results)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        cursor.execute(
            query,
            (user_id, resume_name, job_title, job_description, ats_score, json.dumps(analysis_results))
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return False
    finally:
        conn.close()

def get_user_history(user_id: int) -> List[Dict]:
    """
    Retrieves all resume analyses saved by a user, ordered from newest to oldest.
    """
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        query = format_query("""
            SELECT id, resume_name, job_title, job_description, ats_score, analysis_results, created_at 
            FROM history WHERE user_id = ? ORDER BY created_at DESC
        """)
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        history_list = []
        for row in rows:
            item = dict(row)
            # Deserialize JSON results
            item["analysis_results"] = json.loads(item["analysis_results"])
            history_list.append(item)
        return history_list
    except Exception as e:
        print(f"Error loading user history: {e}")
        return []
    finally:
        conn.close()

def delete_history_item(user_id: int, history_id: int) -> bool:
    """
    Deletes a specific history record belonging to the user.
    """
    conn = get_db_connection()
    cursor = get_cursor(conn)
    try:
        query = format_query("DELETE FROM history WHERE id = ? AND user_id = ?")
        cursor.execute(query, (history_id, user_id))
        conn.commit()
        rows_affected = cursor.rowcount
        return rows_affected > 0
    except Exception as e:
        print(f"Error deleting history: {e}")
        return False
    finally:
        conn.close()
