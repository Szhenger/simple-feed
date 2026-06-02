# SimpleFeed++ Backend Architecture Documentation

**Location:** `backend/`  
**Stack:** Python 3.11+, Django REST Framework, Celery, PostgreSQL 16, Redis

This document outlines the architectural constraints for the SimpleFeed++ backend. In this system, the backend is not a monolithic controller, but a **stateless API gateway** and a **distributed orchestration layer** for high-throughput feed synthesis.

---

## 🏗️ Architectural Axioms

The backend is engineered for horizontal scale and fault isolation. The core philosophy is **I/O-Bound Decoupling**: no HTTP request ever triggers a feed fetch or heavy parsing.

1. **Strict Statelessness:** The Django REST API stores no user state in memory. All state resides in the PostgreSQL cluster.
2. **Deterministic Task Execution:** The Celery fleet ensures that feed ingestion is idempotent, fault-tolerant, and atomic.
3. **Database-as-the-Source-of-Truth:** All security (RLS), partitioning, and vector similarity logic are defined in PostgreSQL DDLs, not Python application code.

---

## ⚙️ Core Subsystems

### 1. Stateless API Gateway (Django REST Framework)
The gateway is solely responsible for authentication (JWT), request routing, and mapping JSON payloads to SQL queries.
* **OpenAPI/Swagger:** All endpoints are strictly typed, serving as the source of truth for the frontend's TypeScript interface generation.
* **RLS Injection:** The API middleware automatically injects the current `workspace_id` into the connection session, ensuring the application cannot "see" data outside the requested tenant.

### 2. Distributed Ingestion Engine (Celery + Redis)
Feed fetching is decoupled from the user-facing request cycle via a message-passing architecture.
* **Decaying Polling Loops:** Rather than `cron` jobs, SimpleFeed++ utilizes an exponential backoff algorithm to tune the polling frequency per-feed based on the density of "axiomatic" updates.
* **Distributed Lock Manager:** We use Redis `Redlock` to ensure that even with thousands of worker containers, a single feed URI is processed by at most one worker at any given time.

### 3. Native Processing Kernel (C++20 + FFI)
Python's `feedparser` is unsuitable for massive syndication streams. We offload tokenization to a native kernel.
* **SIMD Optimization:** The kernel uses AVX-512 intrinsic functions to scan XML character buffers.
* **Zero-Copy Serialization:** Data is returned from the C++ kernel to the Python worker via low-latency memory-mapped buffers (gRPC/FFI).

### 4. Vectorized Triage Pipeline (pgvector)
Once ingested, content is subjected to AI-driven filtering.
* **Embedding Layer:** Articles are pushed to an embedding model (e.g., Sentence-Transformers).
* **Cosine Distance Thresholding:** The result is queried via `pgvector` against the user's workspace centroid. Only content with a similarity score $	au \ge 0.72$ is committed to the main `feed_item` table.

---

## 📂 Directory Structure

```text
backend/
├── ai/                  # Vector models and similarity logic
├── config/              # Django settings, ASGI/WSGI, API routing
├── db/                  # Raw SQL for partitioning and Row-Level Security
├── feed/                # Core Business Logic (Models, Views)
├── workers/             # Celery tasks and polling decay logic
├── requirements.txt     # Python dependencies
└── manage.py            # Entry point for migrations and management
```

---

## 🔒 Security & Governance

1. **Row-Level Security (RLS):** Policies are enforced at the database layer. Even a compromised API key cannot query records from another `workspace_id`.
2. **Strict Code Freeze:** The `/db/` and `/kernel/` directories are subject to a strict code freeze. Changes require an architectural review.
3. **Integration Testing:** All new API endpoints must be accompanied by defensive integration tests in `feed/tests/` that verify the RLS policies in an isolated database sandbox.

---

## 🚀 Deployment & Operations

### Database Migrations
```bash
python manage.py migrate
# Apply partitioning DDL
psql -d simplefeed -f db/ddl/0001_partitioning.sql
```

### Distributed Worker Lifecycle
```bash
# Start the Celery worker fleet
celery -A backend worker --loglevel=info --concurrency=8
```
