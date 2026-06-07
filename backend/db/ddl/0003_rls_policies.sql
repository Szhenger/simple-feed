BEGIN;

-- Enable Row Level Security on all tenant-bound tables
ALTER TABLE feed_workspace ENABLE ROW LEVEL SECURITY;
ALTER TABLE feed_feedsource ENABLE ROW LEVEL SECURITY;
ALTER TABLE feed_feeditem ENABLE ROW LEVEL SECURITY;

-- 1. Workspace Policy: Users can only see Workspaces they own
CREATE POLICY workspace_isolation_policy ON feed_workspace
    FOR ALL
    USING (
        -- Assumes Django sets app.current_user_id in the DB session during authentication
        owner_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
    );

-- 2. FeedSource Policy: Bound directly to the active workspace context
CREATE POLICY source_isolation_policy ON feed_feedsource
    FOR ALL
    USING (
        workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid
    );

-- 3. FeedItem Policy: Bound directly to the active workspace context
CREATE POLICY item_isolation_policy ON feed_feeditem
    FOR ALL
    USING (
        workspace_id = NULLIF(current_setting('app.current_workspace_id', true), '')::uuid
    );

-- Force RLS on table owners (prevents the 'postgres' superuser from bypassing rules in application logic)
ALTER TABLE feed_workspace FORCE ROW LEVEL SECURITY;
ALTER TABLE feed_feedsource FORCE ROW LEVEL SECURITY;
ALTER TABLE feed_feeditem FORCE ROW LEVEL SECURITY;

COMMIT;
