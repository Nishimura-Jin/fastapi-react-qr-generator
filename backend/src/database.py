import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("/app/data/history.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                qr_type TEXT NOT NULL DEFAULT 'url',
                content TEXT NOT NULL,
                label_text TEXT,
                label_position TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)


def create_user(username: str, hashed_password: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (username, hashed_password),
        )


def get_user_by_username(username: str):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, username, hashed_password FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if not row:
        return None
    return {"id": row[0], "username": row[1], "hashed_password": row[2]}


def delete_user(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def save_history(
    user_id: int,
    qr_type: str,
    content: str,
    label_text: str,
    label_position: str,
    expires_at: str | None,
):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO history
                (user_id, qr_type, content, label_text, label_position, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, qr_type, content, label_text, label_position, expires_at),
        )


def get_history(user_id: int):
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT id, qr_type, content, label_text, label_position, expires_at, created_at
            FROM history
            WHERE user_id = ?
              AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (user_id, now),
        ).fetchall()
    return [
        {
            "id": row[0],
            "qr_type": row[1],
            "content": row[2],
            "label_text": row[3],
            "label_position": row[4],
            "expires_at": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


def delete_history(history_id: int, user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM history WHERE id = ? AND user_id = ?",
            (history_id, user_id),
        )


def delete_all_history(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
