"""Долгосрочная память агента — SQLite."""

import sqlite3
import json
import time
import logging
from config import DB_PATH, MAX_CONTEXT_MESSAGES

logger = logging.getLogger(__name__)


def init_db():
    """Создаёт таблицы если не существуют."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            text TEXT,
            is_agent BOOLEAN DEFAULT 0,
            timestamp REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            facts TEXT DEFAULT '[]',
            last_seen REAL
        );

        CREATE TABLE IF NOT EXISTS chat_missions (
            chat_id INTEGER PRIMARY KEY,
            mission TEXT NOT NULL DEFAULT 'observer',
            persona TEXT,
            style TEXT,
            goals TEXT DEFAULT '[]',
            triggers TEXT DEFAULT '[]',
            active BOOLEAN DEFAULT 1
        );

        CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
    """)
    conn.close()
    logger.info("Database initialized")


def save_message(chat_id: int, user_id: int, username: str, first_name: str,
                 text: str, is_agent: bool = False):
    """Сохраняет сообщение в БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (chat_id, user_id, username, first_name, text, is_agent, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (chat_id, user_id, username, first_name, text, is_agent, time.time())
    )

    # Обновляем профиль пользователя
    if not is_agent and user_id:
        conn.execute(
            "INSERT OR REPLACE INTO user_profiles (user_id, username, first_name, last_seen) "
            "VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, time.time())
        )

    conn.commit()
    conn.close()


def get_chat_history(chat_id: int, limit: int = None) -> list[dict]:
    """Получает историю чата."""
    if limit is None:
        limit = MAX_CONTEXT_MESSAGES

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT user_id, username, first_name, text, is_agent, timestamp "
        "FROM messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?",
        (chat_id, limit)
    ).fetchall()
    conn.close()

    messages = []
    for row in reversed(rows):
        messages.append({
            "user_id": row[0],
            "username": row[1],
            "first_name": row[2],
            "text": row[3],
            "is_agent": bool(row[4]),
            "timestamp": row[5],
        })
    return messages


def get_chat_mission(chat_id: int) -> dict | None:
    """Получает миссию для чата."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT mission, persona, style, goals, triggers, active FROM chat_missions WHERE chat_id = ?",
        (chat_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "mission": row[0],
        "persona": row[1],
        "style": row[2],
        "goals": json.loads(row[3]) if row[3] else [],
        "triggers": json.loads(row[4]) if row[4] else [],
        "active": bool(row[5]),
    }


def set_chat_mission(chat_id: int, mission: str, persona: str = None,
                     style: str = None, goals: list = None, triggers: list = None):
    """Устанавливает миссию для чата."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO chat_missions (chat_id, mission, persona, style, goals, triggers, active) "
        "VALUES (?, ?, ?, ?, ?, ?, 1)",
        (chat_id, mission, persona, style,
         json.dumps(goals or [], ensure_ascii=False),
         json.dumps(triggers or [], ensure_ascii=False))
    )
    conn.commit()
    conn.close()


def get_user_profile(user_id: int) -> dict | None:
    """Получает профиль пользователя."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT username, first_name, facts, last_seen FROM user_profiles WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "username": row[0],
        "first_name": row[1],
        "facts": json.loads(row[2]) if row[2] else [],
        "last_seen": row[3],
    }


def add_user_fact(user_id: int, fact: str):
    """Добавляет факт о пользователе."""
    profile = get_user_profile(user_id)
    if not profile:
        return

    facts = profile["facts"]
    if fact not in facts:
        facts.append(fact)
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE user_profiles SET facts = ? WHERE user_id = ?",
            (json.dumps(facts, ensure_ascii=False), user_id)
        )
        conn.commit()
        conn.close()


def get_all_missions() -> list[dict]:
    """Получает все миссии."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT chat_id, mission, persona, style, goals, triggers, active FROM chat_missions"
    ).fetchall()
    conn.close()

    return [
        {
            "chat_id": row[0],
            "mission": row[1],
            "persona": row[2],
            "style": row[3],
            "goals": json.loads(row[4]) if row[4] else [],
            "triggers": json.loads(row[5]) if row[5] else [],
            "active": bool(row[6]),
        }
        for row in rows
    ]


def toggle_mission(chat_id: int, active: bool):
    """Включить/выключить миссию."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE chat_missions SET active = ? WHERE chat_id = ?",
        (int(active), chat_id)
    )
    conn.commit()
    conn.close()


def delete_mission(chat_id: int):
    """Удалить миссию."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM chat_missions WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()


def get_chat_stats(chat_id: int) -> dict:
    """Статистика чата."""
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,)
    ).fetchone()[0]
    agent_msgs = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE chat_id = ? AND is_agent = 1", (chat_id,)
    ).fetchone()[0]
    unique_users = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM messages WHERE chat_id = ? AND is_agent = 0", (chat_id,)
    ).fetchone()[0]
    conn.close()

    return {
        "total_messages": total,
        "agent_messages": agent_msgs,
        "unique_users": unique_users,
    }
