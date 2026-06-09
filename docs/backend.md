# SimpleFeed++ Backend Architecture Documentation

**Document Owner:** Core Engineering  
**System:** SimpleFeed++ API Gateway & Worker Fleet  
**Framework Paradigm:** ShuAndy Engineering  

---

## 1. Executive Summary

The SimpleFeed++ backend abandons the traditional, monolithic web-framework approach in favor of a strictly decoupled, high-throughput ingestion pipeline. Operating under a strict **Closed-World Assumption**, the backend acts as a highly defensive gatekeeper. It leverages hardware-accelerated FFI boundaries, in-memory AI singletons, and database-level security policies to guarantee that only mathematically relevant, cleanly parsed data enters the system.

This document details the abstractions driving the API gateway, the Celery orchestration fleet, and the multi-tenant vector database.

---

## 2. Stateless API Gateway (Django & DRF)

The Django layer (`config/`, `feed/`) is deliberately stripped of all heavy computation. It operates exclusively as a stateless, high-concurrency API gateway responsible for routing, authentication, and database querying.

### OpenAPI & Contract Verification
The gateway dynamically generates a strict OpenAPI V3 specification via `drf-spectacular`. This completely dictates the frontend client generation, ensuring zero contract drift between the API and the React SPA. 

### Traffic Governance & Throttling
To protect the database from Denial of Service (DoS) attacks and poorly written client loops, the gateway enforces mathematically strict throttling limits:
* **Anonymous hits:** Capped at `100/day` to prevent brute-forcing of the JWT authentication endpoints.
* **Authenticated users:** Capped at `1000/minute` to allow the frontend to rapidly virtualize and paginate large vector datasets without saturating the ASGI worker threads.

---

## 3. Distributed Worker Fleet & AI Singleton

To prevent HTTP request timeouts during feed polling, all ingestion logic is pushed to a distributed Redis-backed Celery worker fleet. The workers act as the mathematical filter for the entire platform.

### The AI Singleton Pattern (`ai/engine.py`)
Loading a multi-gigabyte Transformer model (`sentence-transformers/all-mpnet-base-v2`) into memory on every task execution would instantly crash the worker fleet. 
* **Worker-Bound Lifecycle:** The model is instantiated at the module level. When a Celery worker process spins up, it loads the $768$-dimensional embedding model into RAM exactly once.
* **The Write-Barrier Triage:** As raw text is ingested, it is embedded and compared against the dynamic vector centroids of the workspace. If the Cosine Similarity falls below the closed-world threshold ($\tau < 0.72$), the article is dropped from memory *before* it ever touches the PostgreSQL database, preserving disk I/O and index integrity.

### Exponential Polling Math (`workers/tasks.py`)
Polling feeds linearly is a waste of network resources. The Celery Beat orchestrator pulses the database every 60 seconds, queuing feeds based on an exponential decay algorithm. If a feed does not publish frequently, its polling interval is exponentially widened, keeping system loads perfectly optimized.

---

## 4. The FFI Boundary (gRPC to Native Kernel)

Python's Global Interpreter Lock (GIL) and standard library string operations are fundamentally incapable of parsing massive, malformed XML syndication feeds at scale without severe CPU blocking.

* **The Bridge (`kernel/client.py`):** When a Celery worker pulls down an RSS/Atom payload, it immediately pushes the raw bytes across a localized gRPC channel.
* **Bypassing the GIL:** The execution is handed off to the C++20 Native Kernel. The kernel utilizes AVX-512 hardware intrinsics to shred the payload across CPU vector registers, completely bypassing Python's operational constraints. 
* **Memory Ownership:** The parsed entries are returned via Protobuf, safely mapping the deterministic C++ structures back into native Python dictionaries for the AI triage phase.

---

## 5. Persistence & Multi-Tenant Security (PostgreSQL)

The database schema (`db/`) abandons Django's standard Object-Relational Mapping (ORM) migrations in favor of raw Data Definition Language (DDL) to enforce constraints at the lowest possible level.

### Vector Search Optimization (`pgvector`)
We strictly utilize the `pgvector` extension for semantic search operations. Rather than doing flat similarity scans (which degrades to $O(N)$ time complexity), the database builds Hierarchical Navigable Small World (HNSW) indexes over the $768$-dimensional embeddings. This ensures sub-millisecond retrieval of contextually relevant articles, even at multi-million row scale.

### Table Partitioning
To prevent index bloat and ensure lightning-fast vacuuming, the `feed_items` table is horizontally partitioned. Partitioning logic dictates physical separation of data on disk, allowing PostgreSQL to immediately prune irrelevant partitions during query planning.

### Row-Level Security (RLS)
Security is not left to application-level `QuerySet` filters, which are prone to human error. We enforce multi-tenancy directly at the kernel of PostgreSQL via Row-Level Security:
* A user querying the database must pass their specific `workspace_id` into the transaction context.
* If a query attempts to read or mutate a `FeedItem` belonging to a different workspace, PostgreSQL intercepts the request at the disk level and returns an empty set.
* This mathematically guarantees total tenant isolation, even if a backend developer forgets to append a `.filter(workspace=...)` clause in the Python codebase.
