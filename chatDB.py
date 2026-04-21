import sqlite3

def init_chat_db():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        query TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_message(session_id, role, content, query=None):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chat_history (session_id, role, content, query)
    VALUES (?, ?, ?, ?)
    """, (session_id, role, content, query))

    conn.commit()
    conn.close()

def clear_messages(session_id):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM chat_history
    WHERE session_id = ?
    """, (session_id,))

    conn.commit()
    conn.close()

def load_messages(session_id):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, content, query
    FROM chat_history
    WHERE session_id = ?
    ORDER BY id ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    messages = []
    for r in rows:
        messages.append({
            "role": r[0],
            "content": r[1],
            "query": r[2]
        })

    return messages