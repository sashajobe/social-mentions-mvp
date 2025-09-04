import httpx, os, psycopg2
from psycopg2.extras import Json
from config import IG_USER_IDS, META_PAGE_ACCESS_TOKEN, DATABASE_URL

FIELDS = "id,caption,media_type,media_url,permalink,timestamp,owner"

def save_rows(rows, platform="instagram"):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    for r in rows:
        media_id = r.get("id")
        url = r.get("permalink") or r.get("media_url")
        text = r.get("caption")
        media_type = r.get("media_type")
        author_id = None
        author_handle = None
        try:
            cur.execute(
                """INSERT INTO mention(platform, url, text_excerpt, media_type, media_id, is_story, author_handle, author_id, raw)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                     ON CONFLICT (platform, media_id) DO NOTHING
                """,
                (platform, url, text, media_type, media_id, False, author_handle, author_id, Json(r))
            )
        except Exception as e:
            print("Insert error:", e)
    conn.commit()
    cur.close(); conn.close()

def fetch_endpoint(user_id, path):
    base = "https://graph.facebook.com/v19.0"
    url = f"{base}/{user_id}/{path}"
    params = {"access_token": META_PAGE_ACCESS_TOKEN, "fields": FIELDS, "limit": 50}
    with httpx.Client(timeout=20) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])

def run():
    if not IG_USER_IDS or not META_PAGE_ACCESS_TOKEN:
        print("IG creds missing; skip.")
        return
    for user_id in IG_USER_IDS:
        try:
            mm = fetch_endpoint(user_id, "mentioned_media")
            tg = fetch_endpoint(user_id, "tags")
            save_rows(mm + tg)
        except Exception as e:
            print(f"[IG] fetch failed for {user_id}: {e}")

if __name__ == "__main__":
    run()
