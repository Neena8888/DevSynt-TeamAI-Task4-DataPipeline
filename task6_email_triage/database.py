import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "triage_logs.db")

def init_db():
    """Initializes the SQLite database with duplicate detection & audit trail."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            thread_id TEXT,
            sender TEXT,
            subject TEXT,
            category TEXT,
            priority TEXT,
            requires_human BOOLEAN,
            action_taken TEXT,
            rag_used BOOLEAN,
            response_body TEXT,
            forwarded_to TEXT,
            discord_status TEXT,
            timestamp TEXT,
            execution_status TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_duplicate(message_id: str) -> bool:
    """Duplicate protection: checks if message_id has already been processed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM email_logs WHERE message_id = ?", (message_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def log_email(data: Dict[str, Any]):
    """Logs an email processing record into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_logs (
            message_id, thread_id, sender, subject, category, priority,
            requires_human, action_taken, rag_used, response_body,
            forwarded_to, discord_status, timestamp, execution_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("message_id"),
        data.get("thread_id"),
        data.get("sender"),
        data.get("subject"),
        data.get("category"),
        data.get("priority"),
        data.get("requires_human", False),
        data.get("action_taken"),
        data.get("rag_used", False),
        data.get("response_body", ""),
        data.get("forwarded_to", "None"),
        data.get("discord_status", "Skipped"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("execution_status", "SUCCESS")
    ))
    conn.commit()
    conn.close()

def fetch_recent_logs(limit: int = 15) -> List[Dict[str, Any]]:
    """Fetches recent triage records for dashboard/reporting."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)