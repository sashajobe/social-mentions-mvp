-- Unified mentions table
CREATE TABLE IF NOT EXISTS mention (
  id SERIAL PRIMARY KEY,
  platform TEXT NOT NULL,
  detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  author_handle TEXT,
  author_id TEXT,
  url TEXT,
  text_excerpt TEXT,
  media_type TEXT,
  media_id TEXT,
  is_story BOOLEAN DEFAULT FALSE,
  expires_at TIMESTAMPTZ,
  raw JSONB
);

-- basic helpful indexes
CREATE INDEX IF NOT EXISTS idx_mention_detected_at ON mention (detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_mention_platform ON mention (platform);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_platform_media ON mention (platform, media_id);
