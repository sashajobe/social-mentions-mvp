# Social Mentions Monitor — MVP (Python/FastAPI)

This starter packs:
- A **unified DB schema** for mentions
- **FastAPI server** with Instagram **webhook endpoints** (for @mentions + Story mentions via Messaging webhook)
- **Polling scripts** for X (Twitter) and Reddit
- A simple **scheduler** (APScheduler) to run polling jobs
- A **Postman collection** to test endpoints
- Docker Compose (optional) for Postgres

> This is an MVP scaffold; you still need API keys/permissions and to deploy it somewhere reachable for Instagram webhooks (e.g., Render, Fly.io, Railway, or a server with HTTPS + a public URL via Cloudflare Tunnel/NGROK).

## Quickstart

1) **Python setup**
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill your API keys/tokens in .env
```

2) **Local Postgres (optional via Docker)**
```bash
docker compose up -d
# then apply schema:
psql postgresql://postgres:postgres@localhost:5432/mentions -f schema.sql
```

3) **Run the server (webhooks + health)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

4) **Run the scheduler (polling for X + Reddit + IG Graph pull)**
```bash
python worker.py
```

5) **Expose your server for Instagram (DEV)**
- Use **Cloudflare Tunnel** or **ngrok** to expose `http://localhost:8000` to a public **HTTPS** URL.
- Add that public URL as your **Webhook Callback URL** in your Meta App settings.
- Verify webhook with the GET challenge endpoint (included).

6) **Try requests with Postman**
- Import `postman/SashaMentions.postman_collection.json`
- Test **health** and **manual poll** endpoints.

## Notes
- **Instagram Stories**: IG sends story-mention webhook events with a CDN URL **only when someone mentions *your* business/creator account**. Save immediately; stories expire.
- **X (Twitter)**: Requires paid API tier for recent search at meaningful volume.
- **Reddit**: Public search endpoint is used here; upgrade/extend as needed.
- **Compliance**: Stick to official APIs/ToS. No scraping.

## Folder Structure
```
social-mentions-mvp/
  app.py                 # FastAPI server + IG webhook routes
  worker.py              # APScheduler: polls X/Reddit/IG pull
  ingest_x.py            # Poll recent @mentions on X
  ingest_reddit.py       # Poll Reddit for "@handle"
  ingest_instagram_pull.py  # Poll IG Graph 'mentioned_media' and 'tags'
  config.py              # Env + common helpers
  schema.sql             # Postgres schema
  requirements.txt
  docker-compose.yml
  .env.example
  postman/SashaMentions.postman_collection.json
```


## Multiple handles
- Set `MONITOR_HANDLES` in `.env` to a comma-separated list, e.g. `@sophiabush,@abbeycowen,@odetteannable`.
- For Instagram Graph pulls, you must **own/manage** the IG accounts you list in `IG_USER_IDS`; otherwise IG Graph will not return mentions/tags for them.
