CREATE TABLE IF NOT EXISTS events (
    aggregate_id UUID NOT NULL,
    version INTEGER NOT NULL,
    event_data JSONB NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    emitted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (aggregate_id, version)
);

CREATE INDEX IF NOT EXISTS idx_events_emitted_at ON events (emitted_at);
CREATE INDEX IF NOT EXISTS idx_events_emitted_at ON events (aggregate_id);