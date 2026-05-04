# Automatic news fetcher — runs daily, no manual approval needed.
# Official sources (SEM, OSAR) are inserted directly into auto_news.
#
# HOW TO SCHEDULE ON WINDOWS (Task Scheduler):
# 1. Open Task Scheduler -> Create Basic Task
# 2. Name: "Refugee Assistant News Fetch"
# 3. Trigger: Daily, e.g. 07:00
# 4. Action: Start a program
#    Program:   .venv\Scripts\python.exe
#    Arguments: scripts\fetch_news.py
#    Start in:  C:\Users\KUNIGO\Desktop\PowerCoders\Refugee-Assistant-Switzerland
# 5. Finish -> Enable
#
# OR paste this in an Administrator Command Prompt (edit paths if needed):
#   schtasks /create /tn "RefugeeAssistantNews" ^
#     /tr "\"<project_root>\.venv\Scripts\python.exe\" \"<project_root>\scripts\fetch_news.py\"" ^
#     /sc daily /st 07:00 /f

import sys
from pathlib import Path

# Allow imports from project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import feedparser
from datetime import datetime, timezone

from backend.database import init_db, save_auto_news, record_fetch_time
from backend.resolver import _detect_topics

RSS_FEEDS = [
    {
        "url": "https://d-nsbc-p.admin.ch/NSBSubscriber/feeds/rss?lang=de&org-nr=405",
        "source_name": "SEM (Staatssekretariat für Migration)",
    },
    {
        "url": "https://d-nsbc-p.admin.ch/NSBSubscriber/feeds/rss?lang=fr&org-nr=405",
        "source_name": "SEM (Secrétariat d'État aux migrations)",
    },
    {
        "url": "https://d-nsbc-p.admin.ch/NSBSubscriber/feeds/rss?lang=en&org-nr=405",
        "source_name": "SEM (State Secretariat for Migration)",
    },
    {
        "url": "https://d-nsbc-p.admin.ch/NSBSubscriber/feeds/rss?lang=it&org-nr=405",
        "source_name": "SEM (Segreteria di Stato della migrazione)",
    },
    {
        "url": "https://www.osar.ch/rss.xml",
        "source_name": "OSAR (Swiss Refugee Council)",
    },
]


def _parse_date(entry) -> str:
    """Return ISO-format published date or empty string."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    return ""


def _summarise(entry) -> str:
    """Extract a short plain-text summary from the feed entry."""
    raw = ""
    if hasattr(entry, "summary"):
        raw = entry.summary
    elif hasattr(entry, "description"):
        raw = entry.description

    # Strip HTML tags simply
    import re
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def fetch_all() -> None:
    init_db()
    total_new = 0

    for feed_cfg in RSS_FEEDS:
        url = feed_cfg["url"]
        source_name = feed_cfg["source_name"]
        print(f"\nFetching: {source_name}")

        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            print(f"  ERROR: could not parse feed — {feed.bozo_exception}")
            continue

        new_count = 0
        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()

            if not title or not link:
                continue

            summary = _summarise(entry)
            published_at = _parse_date(entry)

            # Auto-detect topic from title + summary
            topics = _detect_topics(f"{title} {summary}")
            topic = topics[0] if topics else "general"

            inserted = save_auto_news(
                title=title,
                url=link,
                source_name=source_name,
                topic=topic,
                summary=summary,
                published_at=published_at,
            )
            if inserted:
                new_count += 1

        print(f"  {new_count} new article(s) saved (from {len(feed.entries)} in feed)")
        total_new += new_count

    record_fetch_time()
    print(f"\nDone. Total new articles today: {total_new}")


if __name__ == "__main__":
    fetch_all()
