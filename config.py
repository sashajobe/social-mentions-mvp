import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev")
DATABASE_URL = os.getenv("DATABASE_URL")

# Instagram / Meta
IG_USER_IDS = [s.strip() for s in os.getenv("IG_USER_IDS", "").split(",") if s.strip()]
META_APP_SECRET = os.getenv("META_APP_SECRET")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN")

# X (Twitter)
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Reddit
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mentions-mvp/0.2")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

# Monitor
MONITOR_HANDLES = [s.strip() for s in os.getenv("MONITOR_HANDLES", "").split(",") if s.strip()]
