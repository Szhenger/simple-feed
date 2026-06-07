#!/usr/bin/env bash
# apply.sh - SimpleFeed++ Database Infrastructure Bootstrap

set -e

DB_NAME="${DB_NAME:-simplefeed}"
DB_USER="${DB_USER:-simplefeed_app}"
DB_HOST="${DB_HOST:-localhost}"

echo "🚀 Bootstrapping SimpleFeed++ PostgreSQL 16 Infrastructure..."

echo "-> 1/4 Applying pgvector extensions..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/ddl/0001_pgvector_setup.sql

echo "-> 2/4 Applying Range Partitioning DDLs..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/ddl/0002_partitioning.sql

echo "-> 3/4 Injecting Row-Level Security Policies..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/ddl/0003_rls_policies.sql

echo "-> 4/4 Building HNSW Vector Indexes..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/ddl/0004_vector_indexes.sql

echo "✅ Database infrastructure successfully enforced."
