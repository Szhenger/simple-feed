-- test_partitions.sql
BEGIN;

-- 1. Create a workspace context
INSERT INTO workspaces (id, name) VALUES ('ws_edge', 'Edge Case Sandbox');

-- 2. Attempt to insert a vector with a timestamp 10 years in the future, 
-- where no physical disk partition exists yet.
-- This MUST fail to prevent unbounded table growth.
DO $$ 
BEGIN
    INSERT INTO feed_items (workspace_id, guid, published_at, embedding)
    VALUES ('ws_edge', '0x999', NOW() + INTERVAL '10 years', '[0.1, 0.2, ...]');
    
    -- If the insert succeeds, fail the test script
    RAISE EXCEPTION 'Test Failed: Postgres allowed out-of-bounds partition insertion.';
EXCEPTION WHEN check_violation THEN
    -- Expected outcome: The check constraint correctly rejected the orphan row
    RAISE NOTICE 'Success: Out-of-bounds timestamp safely rejected by partition constraints.';
END $$;

ROLLBACK;
