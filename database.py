import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

DB_PATH = "resume_analyzer.db"

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """
    Initializes the SQLite database schema if tables don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create History table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            ats_score INTEGER NOT NULL,
            analysis_results TEXT NOT NULL,  -- JSON serialized string
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
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username: str) -> Optional[Dict]:
    """
    Retrieves user profile data by username.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_user_password(user_id: int, new_password_hash: str) -> bool:
    """
    Updates the password hash for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

# Resume Analysis History Operations

def save_analysis(user_id: int, resume_name: str, job_title: str, job_description: str, ats_score: int, analysis_results: Dict) -> bool:
    """
    Saves a resume analysis result to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO history (user_id, resume_name, job_title, job_description, ats_score, analysis_results)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
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
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, resume_name, job_title, job_description, ats_score, analysis_results, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    history_list = []
    for row in rows:
        item = dict(row)
        # Deserialize JSON results
        item["analysis_results"] = json.loads(item["analysis_results"])
        history_list.append(item)
    return history_list

def delete_history_item(user_id: int, history_id: int) -> bool:
    """
    Deletes a specific history record belonging to the user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ? AND user_id = ?", (history_id, user_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
