import json
import re
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
SOURCES_FILE = DATA_DIR / "official_sources.json"


RETENTION_DAYS = 30


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def delete_old_conversations() -> int:
    """Delete conversations and their messages older than RETENTION_DAYS. Returns count deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id IN (
            SELECT id FROM conversations
            WHERE created_at < datetime('now', ? || ' days')
        )
        """,
        (f"-{RETENTION_DAYS}",),
    )
    cursor.execute(
        """
        DELETE FROM conversations
        WHERE created_at < datetime('now', ? || ' days')
        """,
        (f"-{RETENTION_DAYS}",),
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            assistant_message TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating IN (1, -1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auto_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            source_name TEXT NOT NULL,
            topic TEXT,
            summary TEXT,
            published_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def seed_sources_from_json() -> None:
    if not SOURCES_FILE.exists():
        return

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    conn = get_connection()
    cursor = conn.cursor()

    # Always replace sources so additions to the JSON file take effect on restart
    cursor.execute("DELETE FROM sources")
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


def save_auto_news(
    title: str,
    url: str,
    source_name: str,
    topic: str,
    summary: str,
    published_at: str,
) -> bool:
    """Insert a news article. Returns True if new, False if URL already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO auto_news (title, url, source_name, topic, summary, published_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, url, source_name, topic, summary, published_at),
    )
    conn.commit()
    inserted = cursor.rowcount > 0
    conn.close()
    return inserted


def count_auto_news() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auto_news")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_last_fetch_time() -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(created_at) FROM auto_news")
    result = cursor.fetchone()[0]
    conn.close()
    return result[:10] if result else None


def save_feedback(
    conversation_id: int,
    user_message: str,
    assistant_message: str,
    rating: int,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO feedback (conversation_id, user_message, assistant_message, rating)
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, user_message, assistant_message, rating),
    )
    conn.commit()
    conn.close()


_STOP_WORDS = {
    "do", "you", "know", "is", "in", "of", "to", "an", "or", "the",
    "and", "me", "my", "we", "it", "at", "be", "he", "she", "so",
    "if", "no", "on", "as", "up", "by", "go", "us", "can", "are",
    "was", "for", "but", "not", "with", "this", "that", "from",
    "have", "has", "had", "will", "would", "could", "should", "about",
    "what", "when", "where", "who", "how", "why", "which", "there",
    "their", "they", "been", "also", "more", "some", "than", "then",
    "its", "any", "all", "out", "get", "one", "may", "use", "your",
}


def _tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    return tokens - _STOP_WORDS


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


def search_sources(query: str, limit: int = 3, canton: str | None = None) -> list[dict[str, Any]]:
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

    # Include automatically fetched official news (no approval needed — trusted source)
    cursor.execute(
        "SELECT id, title, url, topic, summary, published_at FROM auto_news ORDER BY id DESC LIMIT 200"
    )
    news_rows = cursor.fetchall()
    conn.close()

    all_sources = [
        {
            "id": row[0],
            "title": row[1],
            "url": row[2],
            "topic": row[3],
            "content": row[4],
            "is_official": 1,
            "published_at": "",  # static sources have no meaningful publication date
        }
        for row in rows
    ] + [
        {
            "id": f"news_{row[0]}",
            "title": row[1],
            "url": row[2],
            "topic": row[3] or "",
            "content": row[4] or "",
            "is_official": 1,
            "published_at": row[5] or "",
        }
        for row in news_rows
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

    # Detect canton name mentioned directly in the query text
    _CANTON_ALIASES: dict[str, str] = {
        "zurich": "zurich", "zürich": "zurich", "zuerich": "zurich",
        "bern": "bern", "berne": "bern",
        "geneva": "geneva", "geneve": "geneva", "genève": "geneva",
        "vaud": "vaud", "lausanne": "vaud",
        "lucerne": "lucerne", "luzern": "lucerne",
        "aargau": "aargau", "argovia": "aargau",
        "basel": "basel",
        "fribourg": "fribourg", "freiburg": "fribourg",
        "valais": "valais", "wallis": "valais",
        "ticino": "ticino", "tessin": "ticino",
        "graubünden": "graubünden", "grisons": "graubünden", "graubuenden": "graubünden",
        "thurgau": "thurgau",
        "solothurn": "solothurn",
        "schaffhausen": "schaffhausen",
        "schwyz": "schwyz",
        "zug": "zug",
        "jura": "jura",
        "neuchatel": "neuchâtel", "neuchâtel": "neuchâtel", "neuenburg": "neuchâtel",
        "genf": "geneva",
        "saint-gall": "st. gallen",
        "glarus": "glarus",
        "nidwalden": "nidwalden",
        "obwalden": "obwalden",
        "uri": "uri",
        "appenzell": "appenzell",
        "st. gallen": "st. gallen", "st gallen": "st. gallen", "saint gallen": "st. gallen",
    }
    query_canton_name: str | None = None
    for alias, canonical in _CANTON_ALIASES.items():
        if alias in query_lower:
            query_canton_name = canonical
            break

    # Detect country name in query for country-specific source boosting
    _COUNTRY_NAMES = [
        "syria", "ukraine", "afghanistan", "eritrea",
        "somalia", "ethiopia", "iraq", "turkey",
    ]
    query_country: str | None = next(
        (c for c in _COUNTRY_NAMES if c in query_lower), None
    )

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

        # Strong boost when a specific country matches a country-specific source
        if query_country and query_country in haystack:
            score += 40

        # Strong boost when canton is mentioned in the query text
        if query_canton_name and query_canton_name in haystack:
            score += 100

        # Additional boost from dropdown canton selection
        if canton:
            canton_lower = canton.lower()
            if canton_lower in haystack:
                score += 60

        if score > 0:
            scored.append((score, src))

    scored.sort(key=lambda x: x[0], reverse=True)

    # If a specific canton was mentioned, only return canton-matching sources
    # (prevents other cantons from appearing as results)
    if query_canton_name:
        canton_filtered = [
            src for score, src in scored
            if query_canton_name in f"{src['title']} {src['topic']} {src['content']}".lower()
            and score >= 12
        ]
        if canton_filtered:
            return canton_filtered[:limit]

    # Return only actually relevant results — threshold prevents junk sources
    filtered = [src for score, src in scored if score >= 12]
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