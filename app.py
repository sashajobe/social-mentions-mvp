from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from datetime import datetime, timedelta
import httpx, os, json, psycopg2
from psycopg2.extras import Json
from config import META_VERIFY_TOKEN, META_PAGE_ACCESS_TOKEN, DATABASE_URL

app = FastAPI(title="Mentions Monitor")

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

# --- Meta/Instagram Webhook Verification (GET) ---
@app.get("/webhooks/meta", response_class=PlainTextResponse)
def verify(mode: str | None = None, challenge: str | None = None, verify_token: str | None = None):
    if mode == "subscribe" and verify_token == META_VERIFY_TOKEN:
        return challenge or ""
    raise HTTPException(status_code=403, detail="Verification failed.")

# --- Meta/Instagram Webhook Receiver (POST) ---
@app.post("/webhooks/meta")
async def meta_webhook(request: Request):
    payload = await request.json()
    # Save raw for debugging if needed
    # Extract relevant events: instagram mentions, messaging story mentions, etc.
    try:
        conn = get_db()
        cur = conn.cursor()
        # This is a generic catcher; different app subscriptions deliver different payload shapes.
        # We'll attempt to detect story mentions (messaging) and standard IG media mentions.
        def insert_mention(platform, url=None, text=None, media_type=None, media_id=None, is_story=False, expires_at=None, author_handle=None, author_id=None, raw=None):
            cur.execute(
                """INSERT INTO mention(platform, url, text_excerpt, media_type, media_id, is_story, expires_at, author_handle, author_id, raw)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                     ON CONFLICT (platform, media_id) DO NOTHING
                """,
                (platform, url, text, media_type, media_id, is_story, expires_at, author_handle, author_id, Json(raw))
            )

        # Minimal parsing examples (expand per your app subscriptions):
        entry_list = payload.get("entry", [])
        for entry in entry_list:
            changes = entry.get("changes") or []
            for ch in changes:
                field = ch.get("field")
                value = ch.get("value", {})
                # Example: instagram mentions/tags updates might appear here depending on subscription
                if field and "mention" in field:
                    media_id = value.get("media_id") or value.get("id")
                    permalink = value.get("permalink")
                    caption = value.get("caption")
                    insert_mention("instagram", url=permalink, text=caption, media_type=value.get("media_type"), media_id=media_id, is_story=False, raw=value)

        # Instagram Messaging (story mention) events often arrive under "entry.messaging" or via the Messenger webhook surface.
        # Different shapes exist; below is a generic pass-through attempt:
        for entry in entry_list:
            messaging = entry.get("messaging") or []
            for msg in messaging:
                story = msg.get("story")
                if story and story.get("mention"):
                    media_url = story.get("media_url")  # CDN URL if provided
                    expires_at = datetime.utcnow() + timedelta(hours=24)
                    insert_mention("instagram", url=media_url, text="Story mention", media_type="STORY", media_id=story.get("id"), is_story=True, expires_at=expires_at, raw=msg)

        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        # Swallow exceptions to avoid repeated retries from Meta; log locally
        print("Webhook error:", e)

    return {"received": True}
