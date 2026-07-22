BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE memory_record_type AS ENUM (
  'decision',
  'state',
  'fact',
  'preference',
  'task',
  'incident',
  'procedure'
);

CREATE TYPE memory_record_status AS ENUM (
  'candidate',
  'shared',
  'superseded',
  'rejected',
  'archived'
);

CREATE TYPE memory_privacy_class AS ENUM (
  'private_agent',
  'personal_stanislav',
  'project',
  'shared_safe',
  'external_forbidden'
);

CREATE TYPE memory_audit_event_type AS ENUM (
  'proposed',
  'promoted',
  'superseded',
  'rejected',
  'archived',
  'mirror_exported',
  'restore_checked'
);

CREATE TABLE IF NOT EXISTS memory_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  record_type memory_record_type NOT NULL,
  status memory_record_status NOT NULL DEFAULT 'candidate',
  title text NOT NULL CHECK (length(trim(title)) > 0),
  body text NOT NULL CHECK (length(trim(body)) > 0),
  scope text NOT NULL DEFAULT 'openclaw' CHECK (length(trim(scope)) > 0),
  privacy_class memory_privacy_class NOT NULL,
  source text NOT NULL CHECK (length(trim(source)) > 0),
  source_ref text,
  owner text,
  created_by text NOT NULL CHECK (length(trim(created_by)) > 0),
  updated_by text NOT NULL CHECK (length(trim(updated_by)) > 0),
  confidence numeric(4,3) NOT NULL DEFAULT 0.700 CHECK (confidence >= 0 AND confidence <= 1),
  tags text[] NOT NULL DEFAULT '{}',
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  supersedes_id uuid REFERENCES memory_records(id),
  superseded_by_id uuid REFERENCES memory_records(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_embeddings (
  record_id uuid PRIMARY KEY REFERENCES memory_records(id) ON DELETE CASCADE,
  embedding vector(768) NOT NULL,
  model text NOT NULL,
  embedded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_audit_log (
  id bigserial PRIMARY KEY,
  record_id uuid NOT NULL REFERENCES memory_records(id),
  event_type memory_audit_event_type NOT NULL,
  actor text NOT NULL CHECK (length(trim(actor)) > 0),
  reason text NOT NULL CHECK (length(trim(reason)) > 0),
  before_status memory_record_status,
  after_status memory_record_status,
  event_data jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memory_records_status_scope
  ON memory_records(status, scope, record_type);

CREATE INDEX IF NOT EXISTS idx_memory_records_privacy
  ON memory_records(privacy_class);

CREATE INDEX IF NOT EXISTS idx_memory_records_tags
  ON memory_records USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_memory_records_metadata
  ON memory_records USING gin(metadata);

CREATE INDEX IF NOT EXISTS idx_memory_audit_record
  ON memory_audit_log(record_id, created_at);

CREATE INDEX IF NOT EXISTS idx_memory_embeddings_vector
  ON memory_embeddings USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE OR REPLACE FUNCTION set_memory_record_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_memory_records_updated_at ON memory_records;
CREATE TRIGGER trg_memory_records_updated_at
BEFORE UPDATE ON memory_records
FOR EACH ROW
EXECUTE FUNCTION set_memory_record_updated_at();

COMMIT;
