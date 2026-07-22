BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'openclaw_memory_reader') THEN
    CREATE ROLE openclaw_memory_reader NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'openclaw_memory_writer') THEN
    CREATE ROLE openclaw_memory_writer NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'openclaw_memory_promoter') THEN
    CREATE ROLE openclaw_memory_promoter NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'openclaw_memory_backup') THEN
    CREATE ROLE openclaw_memory_backup NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'openclaw_memory_admin') THEN
    CREATE ROLE openclaw_memory_admin NOLOGIN;
  END IF;
  EXECUTE format('GRANT openclaw_memory_admin TO %I', current_user);
END;
$$;

ALTER TABLE memory_records
  ADD COLUMN IF NOT EXISTS content_hash text;

UPDATE memory_records
SET content_hash = encode(
  digest(
    record_type::text || E'\n' ||
    scope || E'\n' ||
    privacy_class::text || E'\n' ||
    title || E'\n' ||
    body || E'\n' ||
    source || E'\n' ||
    coalesce(source_ref, ''),
    'sha256'
  ),
  'hex'
)
WHERE content_hash IS NULL;

ALTER TABLE memory_records
  ALTER COLUMN content_hash SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'chk_memory_records_content_hash_sha256'
      AND conrelid = 'memory_records'::regclass
  ) THEN
    ALTER TABLE memory_records
      ADD CONSTRAINT chk_memory_records_content_hash_sha256
        CHECK (content_hash ~ '^[0-9a-f]{64}$');
  END IF;
END;
$$;

CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_records_content_hash_active
  ON memory_records(content_hash)
  WHERE status IN ('candidate', 'shared');

CREATE OR REPLACE VIEW current_shared_canon
WITH (security_invoker = true) AS
SELECT *
FROM memory_records
WHERE status = 'shared'
  AND superseded_by_id IS NULL;

CREATE OR REPLACE FUNCTION prevent_memory_audit_mutation()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'memory_audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_memory_audit_no_update ON memory_audit_log;
CREATE TRIGGER trg_memory_audit_no_update
BEFORE UPDATE ON memory_audit_log
FOR EACH ROW
EXECUTE FUNCTION prevent_memory_audit_mutation();

DROP TRIGGER IF EXISTS trg_memory_audit_no_delete ON memory_audit_log;
CREATE TRIGGER trg_memory_audit_no_delete
BEFORE DELETE ON memory_audit_log
FOR EACH ROW
EXECUTE FUNCTION prevent_memory_audit_mutation();

DROP TRIGGER IF EXISTS trg_memory_audit_no_truncate ON memory_audit_log;
CREATE TRIGGER trg_memory_audit_no_truncate
BEFORE TRUNCATE ON memory_audit_log
FOR EACH STATEMENT
EXECUTE FUNCTION prevent_memory_audit_mutation();

ALTER TABLE memory_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_records FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_embeddings FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_audit_log FORCE ROW LEVEL SECURITY;
-- The actual backup LOGIN role must be provisioned with BYPASSRLS.
-- Role attributes such as BYPASSRLS are not inherited from this NOLOGIN group.

DROP POLICY IF EXISTS memory_records_select_policy ON memory_records;
CREATE POLICY memory_records_select_policy ON memory_records
FOR SELECT
USING (
  pg_has_role(current_user, 'openclaw_memory_admin', 'member')
  OR pg_has_role(current_user, 'openclaw_memory_backup', 'member')
  OR privacy_class IN ('project', 'shared_safe')
);

DROP POLICY IF EXISTS memory_records_insert_policy ON memory_records;
CREATE POLICY memory_records_insert_policy ON memory_records
FOR INSERT
WITH CHECK (
  pg_has_role(current_user, 'openclaw_memory_admin', 'member')
  OR (
    pg_has_role(current_user, 'openclaw_memory_writer', 'member')
    AND status = 'candidate'
    AND privacy_class IN ('project', 'shared_safe')
  )
  OR (
    pg_has_role(current_user, 'openclaw_memory_promoter', 'member')
    AND status IN ('candidate', 'shared')
    AND privacy_class IN ('project', 'shared_safe')
  )
);

DROP POLICY IF EXISTS memory_records_update_policy ON memory_records;
CREATE POLICY memory_records_update_policy ON memory_records
FOR UPDATE
USING (
  pg_has_role(current_user, 'openclaw_memory_admin', 'member')
  OR (
    pg_has_role(current_user, 'openclaw_memory_promoter', 'member')
    AND privacy_class IN ('project', 'shared_safe')
  )
)
WITH CHECK (
  pg_has_role(current_user, 'openclaw_memory_admin', 'member')
  OR (
    pg_has_role(current_user, 'openclaw_memory_promoter', 'member')
    AND privacy_class IN ('project', 'shared_safe')
  )
);

DROP POLICY IF EXISTS memory_embeddings_select_policy ON memory_embeddings;
CREATE POLICY memory_embeddings_select_policy ON memory_embeddings
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM memory_records r
    WHERE r.id = memory_embeddings.record_id
  )
);

DROP POLICY IF EXISTS memory_embeddings_insert_policy ON memory_embeddings;
CREATE POLICY memory_embeddings_insert_policy ON memory_embeddings
FOR INSERT
WITH CHECK (
  pg_has_role(current_user, 'openclaw_memory_admin', 'member')
  OR pg_has_role(current_user, 'openclaw_memory_writer', 'member')
  OR pg_has_role(current_user, 'openclaw_memory_promoter', 'member')
);

DROP POLICY IF EXISTS memory_audit_select_policy ON memory_audit_log;
CREATE POLICY memory_audit_select_policy ON memory_audit_log
FOR SELECT
USING (
  EXISTS (
    SELECT 1
    FROM memory_records r
    WHERE r.id = memory_audit_log.record_id
  )
);

DROP POLICY IF EXISTS memory_audit_insert_policy ON memory_audit_log;
CREATE POLICY memory_audit_insert_policy ON memory_audit_log
FOR INSERT
WITH CHECK (
  pg_has_role(current_user, 'openclaw_memory_admin', 'member')
  OR pg_has_role(current_user, 'openclaw_memory_writer', 'member')
  OR pg_has_role(current_user, 'openclaw_memory_promoter', 'member')
);

REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO
  openclaw_memory_reader,
  openclaw_memory_writer,
  openclaw_memory_promoter,
  openclaw_memory_backup,
  openclaw_memory_admin;
GRANT USAGE ON TYPE
  memory_record_type,
  memory_record_status,
  memory_privacy_class,
  memory_audit_event_type
  TO
  openclaw_memory_reader,
  openclaw_memory_writer,
  openclaw_memory_promoter,
  openclaw_memory_backup,
  openclaw_memory_admin;

GRANT SELECT ON memory_records, memory_embeddings, memory_audit_log, current_shared_canon
  TO openclaw_memory_reader;

GRANT SELECT, INSERT ON memory_records, memory_embeddings, memory_audit_log
  TO openclaw_memory_writer;
GRANT USAGE, SELECT ON SEQUENCE memory_audit_log_id_seq
  TO openclaw_memory_writer;

GRANT SELECT, INSERT, UPDATE ON memory_records, memory_embeddings, memory_audit_log
  TO openclaw_memory_promoter;
GRANT USAGE, SELECT ON SEQUENCE memory_audit_log_id_seq
  TO openclaw_memory_promoter;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO openclaw_memory_backup;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO openclaw_memory_backup;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public
  TO openclaw_memory_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public
  TO openclaw_memory_admin;

COMMIT;
