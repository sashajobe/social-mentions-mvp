import os, httpx, psycopg2
from psycopg2.extras import Json
from urllib.parse import quote
from config import X_BEARER_TOKEN, MONITOR_HANDLES, DATABASE_URL

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"

def run():
    if not X_BEARER_TOKEN or not MONITOR_HANDLES:
        print("X creds/handles missing; skip.")
        return
    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    conn = psycopg2.connect(DATABASE_URL); cur = conn.cursor()

    with httpx.Client(timeout=20, headers=headers) as client:
        for handle in MONITOR_HANDLES:
            query = quote(handle)
            params = {
                "query": query,
                "max_results": 50,
                "tweet.fields": "author_id,created_at",
                "expansions": "author_id",
                "user.fields": "username,name"
            }
            try:
                r = client.get(SEARCH_URL, params=params)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                print(f"[X] query failed for {handle}: {e}")
                continue

            users_index = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            tweets = data.get("data", [])

            for t in tweets:
                author = users_index.get(t["author_id"], {})
                url = f"https://x.com/{author.get('username','')}/status/{t['id']}"
                try:
                    cur.execute(
                        """INSERT INTO mention(platform, url, text_excerpt, media_type, media_id, author_handle, author_id, raw)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                             ON CONFLICT (platform, media_id) DO NOTHING
                        """,
                        ("x", url, t.get("text"), "TWEET", t["id"], f"@{author.get('username','')}", author.get("id"), Json({"handle": handle, "tweet": t}))
                    )
                except Exception as e:
                    print("Insert error:", e)

    conn.commit(); cur.close(); conn.close()

if __name__ == "__main__":
    run()
