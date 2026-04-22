import json
import re
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
SOURCES_FILE = DATA_DIR / "official_sources.json"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            is_official INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def seed_sources_from_json() -> None:
    if not SOURCES_FILE.exists():
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sources")
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        return

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    for item in items:
        cursor.execute(
            """
            INSERT INTO sources (title, url, topic, content, is_official)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item["title"],
                item["url"],
                item["topic"],
                item["content"],
                int(item.get("is_official", 1)),
            ),
        )

    conn.commit()
    conn.close()


def create_conversation() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations DEFAULT VALUES")
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return int(conversation_id)


def save_message(conversation_id: int, role: str, content: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, content),
    )
    conn.commit()
    conn.close()


def get_conversation_messages(conversation_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"role": row[0], "content": row[1], "created_at": row[2]}
        for row in rows
    ]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]{2,}", text.lower()))


def _extract_permit_code(text: str) -> str | None:
    """
    Detect phrases like:
    - permit f
    - permit s
    - permit b
    """
    match = re.search(r"\bpermit\s+([a-z])\b", text.lower())
    if match:
        return match.group(1).upper()
    return None


def search_sources(query: str, limit: int = 3) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, url, topic, content, is_official
        FROM sources
        WHERE is_official = 1
        """
    )
    rows = cursor.fetchall()
    conn.close()

    all_sources = [
        {
            "id": row[0],
            "title": row[1],
            "url": row[2],
            "topic": row[3],
            "content": row[4],
            "is_official": row[5],
        }
        for row in rows
    ]

    query_lower = query.lower()
    query_tokens = _tokenize(query)
    permit_code = _extract_permit_code(query)

    # 1) STRICT permit matching first
    if permit_code:
        exact_permit_sources = []
        for src in all_sources:
            haystack = f"{src['title']} {src['topic']} {src['content']}".lower()

            # Must contain the exact same permit code
            if (
                f"permit {permit_code.lower()}" in haystack
                or f"ausweis {permit_code.lower()}" in haystack
            ):
                exact_permit_sources.append(src)

        if exact_permit_sources:
            # Rank exact permit sources
            scored = []
            for src in exact_permit_sources:
                haystack = f"{src['title']} {src['topic']} {src['content']}".lower()
                source_tokens = _tokenize(haystack)

                score = 0

                # Strong bonuses
                if f"permit {permit_code.lower()}" in src["title"].lower():
                    score += 100
                if f"permit {permit_code.lower()}" in src["topic"].lower():
                    score += 50
                if f"permit {permit_code.lower()}" in haystack:
                    score += 25

                # Token overlap bonus
                score += len(query_tokens.intersection(source_tokens)) * 3

                scored.append((score, src))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [src for _, src in scored[:limit]]

    # 2) General ranking for non-permit questions
    scored = []
    for src in all_sources:
        haystack = f"{src['title']} {src['topic']} {src['content']}".lower()
        source_tokens = _tokenize(haystack)

        score = 0

        # Exact phrase bonuses
        if query_lower in haystack:
            score += 30
        if query_lower in src["title"].lower():
            score += 40
        if query_lower in src["topic"].lower():
            score += 20

        # Token overlap
        overlap = query_tokens.intersection(source_tokens)
        score += len(overlap) * 3

        if score > 0:
            scored.append((score, src))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Return only actually relevant results
    filtered = [src for score, src in scored if score >= 3]
    return filtered[:limit]


# Legacy helpers
def save_interaction(user_input: str, response: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interactions (user_input, response) VALUES (?, ?)",
        (user_input, response)
    )
    conn.commit()
    conn.close()


def get_recent_interactions(limit: int = 5) -> list[tuple[str, str, str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT user_input, response, created_at
        FROM interactions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows