import sys
import os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Run from project root: python tests/test_search.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, seed_sources_from_json, search_sources

print("Loading model and seeding sources (first run may take ~15s)...")
init_db()
seed_sources_from_json()

tests = [
    ("English",   "What are my work rights with Permit F?"),
    ("Arabic",    "هل يمكنني العمل في سويسرا بتصريح إف"),
    ("Dari",      "حق کار در سوئیس چیست"),
    ("Ukrainian", "як отримати медичну допомогу в Швейцарії"),
    ("Turkish",   "İsviçre'de sığınma prosedürü nasıl işler"),
]

for lang, query in tests:
    print(f"\n{'='*60}")
    print(f"Language : {lang}")
    print(f"Query    : {query}")
    results = search_sources(query)
    if results:
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['topic'][:40]}] {r['title'][:55]}")
    else:
        print("  (no results found)")
