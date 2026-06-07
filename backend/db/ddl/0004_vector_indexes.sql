BEGIN;

-- Create an HNSW index on the embedding column using Cosine Distance (vector_cosine_ops)
-- We specify m=16 (max connections per layer) and ef_construction=64 
-- which is an optimal baseline for 768-dimensional transformer embeddings.
CREATE INDEX feed_feeditem_embedding_hnsw_idx 
    ON feed_feeditem 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Standard B-Tree indexes for state machine filtering and chronological sorting
CREATE INDEX feed_feeditem_state_idx ON feed_feeditem (workspace_id, state);
CREATE INDEX feed_feeditem_category_idx ON feed_feeditem (workspace_id, category);

COMMIT;
