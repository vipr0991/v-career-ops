-- 0001_init.sql — Career-Ops state machine schema
CREATE TYPE eval_stage AS ENUM (
  'tier1_parse', 'tier2_eval', 'research', 'awaiting_approval',
  'pdf_render', 'networking', 'completed', 'archived'
);

CREATE TABLE evaluations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT NOT NULL,
  job_title TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  description_hash TEXT NOT NULL,
  stage eval_stage DEFAULT 'tier1_parse',
  tier2_score SMALLINT,
  company_research_json JSONB,    -- Tier 3 gap analysis output
  outreach_targets JSONB,         -- Discovered HR/Founders (Happenstance)
  outreach_draft TEXT,            -- Drafted warm-introduction message
  pcloud_file_id TEXT,
  pcloud_hash TEXT,               -- metadata.hash from the upload response (integrity check)
  needs_reauth BOOLEAN DEFAULT FALSE, -- set on pCloud 401 / error 1000/2000
  locked_by TEXT,                 -- worker ID holding the row
  locked_until TIMESTAMPTZ,       -- crash-recovery lock expiry
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX evaluations_stage_idx ON evaluations (stage);
CREATE INDEX evaluations_lock_idx ON evaluations (locked_until)
  WHERE locked_until IS NOT NULL;

CREATE TABLE scan_history (       -- replaces data/scan-history.tsv
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  portal TEXT NOT NULL,
  external_id TEXT NOT NULL,
  first_seen TIMESTAMPTZ DEFAULT now(),
  UNIQUE (portal, external_id)
);

CREATE TABLE unique_roles (       -- 30-day cross-board dedup
  role_hash TEXT PRIMARY KEY,     -- hash(company_name + job_title)
  evaluation_id UUID REFERENCES evaluations(id),
  evaluated_at TIMESTAMPTZ DEFAULT now()
);
