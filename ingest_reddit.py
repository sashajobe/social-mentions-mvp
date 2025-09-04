import os, httpx, psycopg2
from psycopg2.extras import Json
from urllib.parse import quote
from config import MONITOR_HANDLES, DATABASE_URL, REDDIT_USER_AGENT

SEARCH_URL = "https://www.reddit.com/search.json"

def run():
    if not MONITOR_HANDLES:
        print("No MONITOR_HANDLES set; skip.")
        return

    headers = {"User-Agent": REDDIT_USER_AGENT}
    conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()

    with httpx.Client(timeout=20, headers=headers) as client:
        for handle in MONITOR_HANDLES:
            q = f'"{handle}"'
            params = {"q": q, "sort": "new", "limit": 50}
            try:
                r = client.get(SEARCH_URL, params=params)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                print(f"[Reddit] query failed for {handle}: {e}")
                continue

            children = data.get("data", {}).get("children", [])
            for ch in children:
                d = ch.get("data", {})
                url = f"https://www.reddit.com{d.get('permalink','')}"
                media_id = d.get("id")
                text = d.get("title") or d.get("selftext")
                author = d.get("author")
                try:
                    cur.execute(
                        """INSERT INTO mention(platform, url, text_excerpt, media_type, media_id, author_handle, raw)
                             VALUES (%s,%s,%s,%s,%s,%s,%s)
                             ON CONFLICT (platform, media_id) DO NOTHING
                        """,
                        ("reddit", url, text, "POST", media_id, f"u/{author}" if author else None, Json({"handle": handle, "post": d}))
                    )
                except Exception as e:
                    print("Insert error:", e)

    conn.commit(); cur.close(); conn.close()

if __name__ == "__main__":
    run()
