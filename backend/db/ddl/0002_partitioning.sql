BEGIN;

-- Drop the standard table created by Django's ORM
DROP TABLE IF EXISTS feed_feeditem CASCADE;

-- Recreate the table as a native Range Partitioned table
CREATE TABLE feed_feeditem (
    id UUID NOT NULL,
    workspace_id UUID NOT NULL REFERENCES feed_workspace(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES feed_feedsource(id) ON DELETE CASCADE,
    guid VARCHAR(512) NOT NULL,
    title VARCHAR(1000) NOT NULL,
    url VARCHAR(2000) NOT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- AI Triage Mechanics
    embedding vector(768),
    state VARCHAR(20) NOT NULL,
    category VARCHAR(20) NOT NULL,
    similarity_score DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- The PK must include the partition key
    PRIMARY KEY (id, published_at),
    UNIQUE (source_id, guid, published_at)
) PARTITION BY RANGE (published_at);

-- Create initial partitions for the current and upcoming quarters
CREATE TABLE feed_feeditem_y2026q2 PARTITION OF feed_feeditem 
    FOR VALUES FROM ('2026-04-01 00:00:00+00') TO ('2026-07-01 00:00:00+00');

CREATE TABLE feed_feeditem_y2026q3 PARTITION OF feed_feeditem 
    FOR VALUES FROM ('2026-07-01 00:00:00+00') TO ('2026-10-01 00:00:00+00');

CREATE TABLE feed_feeditem_y2026q4 PARTITION OF feed_feeditem 
    FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2027-01-01 00:00:00+00');

-- Create an automated default partition to catch anomalies
CREATE TABLE feed_feeditem_default PARTITION OF feed_feeditem DEFAULT;

COMMIT;
