# SimpleFeed++: A Distributed, AI-Orchestrated Multi-Tenant Workspace Engine

**SimpleFeed++** is an enterprise-grade, high-concurrency RSS/Atom ingestion and data-synthesis platform designed to transform raw web syndication streams into a highly focused, collaborative professional workspace. 

Engineered under the **ShuAndy Engineering** framework—a personal initiative focused on systems-level compilers and high-performance infrastructure—this architecture represents a complete evolution from a monolithic application into a decoupled, deterministic system built for multi-tenant isolation, automated semantic triage, and bare-metal processing efficiency.

---

## 🎯 The Four Professional Axioms

To prevent data fatigue and maintain a hyper-focused professional workspace, SimpleFeed++ enforces a strict **Closed-World Assumption**. The platform algorithmically rejects general web noise, admitting data only if it maps directly to one of the four foundational pillars of professional development:

1. **Education:** Continuous technical learning, academic publications, compiler design updates, research papers, and structural skills acquisition.
2. **Career Advancement:** Engineering leadership methodologies, system architecture patterns, industry movements, and organizational scaling paradigms.
3. **Finances:** Quantitative macroeconomics, market optimization, personal capital allocation, tax planning, and investment strategies.
4. **Life Planning:** Long-term deterministic tracking, healthcare management, risk mitigation, and collaborative execution frameworks.

---

## 🏗️ Distributed Architecture & Deployment

The infrastructure separates concerns across a strictly typed frontend client, specialized compute endpoints, message processing, and data state layers to achieve linear horizontal scaling and eliminate runtime race conditions.

```text
                           +---------------------------------------+
                           |  Client SPA (React + TypeScript)      |
                           |  - TanStack Query Async State         |
                           +---------------------------------------+
                                               |
                                               v [HTTPS / Strict JSON Contract]
                           +---------------------------------------+
                           |      Stateless Web App (Django)       |
                           +---------------------------------------+
                                               |
                     +-------------------------+-------------------------+
                     | [Enqueue Async Task]                              | [Transactional State]
                     v                                                   v
         +-----------------------+                           +-----------------------+
         |  Redis Message Broker |                           | PostgreSQL Cluster    |
         +-----------------------+                           |  - Primary Node       |
                     |                                       |  - Read Replicas      |
                     v [Worker Pull]                         +-----------------------+
         +-----------------------+                                       ^
         | Celery Worker Fleet   |                                       |
         | (Python State Engine) |                                       |
         +-----------------------+                                       |
                     |                                                   |
                     +---> [FFI/gRPC Stream]                             |
                     |     v                                             |
                     |  +---------------------------------------+        |
                     |  |  Native Parser Kernel (C++20)          |        |
                     |  |  - SIMD / AVX-512 Stream Tokenizer    |        |
                     |  +---------------------------------------+        |
                     |     |                                             |
                     |     v [Structured Binary Vector]                  |
                     +-----+---------------------------------------------+
                           | [Batch Write / RLS Guarded]
                           v
         +-------------------------------------------------------------------+
         | PostgreSQL Storage Array (Declarative Partitioning + pgvector)   |
         +-------------------------------------------------------------------+
```

### 1. Strongly Typed Client SPA (React + TypeScript)
* **Compiler-Verified UI:** The entire interface is built with React and strict TypeScript. API responses map to auto-generated TypeScript interfaces, ensuring the database schemas are mathematically preserved through the DOM.
* **Asynchronous State Management:** Utilizes TanStack Query (React Query) to manage server state, cache validation, and UI loading states. This gracefully handles the backend's exponential polling delays without blocking the user interface.
* **DOM Virtualization:** Heavy rendering pipelines for historical archives use windowing/virtualization, guaranteeing $O(1)$ memory consumption regardless of how many thousands of entries exist in a workspace.

### 2. Stateless Compute Layer (Django REST Framework)
* **Decoupled Lifecycle:** The Django web application operates exclusively as a stateless API gateway. It authenticates requests, terminates TLS, and enforces the OpenAPI specification contracts consumed by the TypeScript frontend.
* **Asynchronous Offloading:** All I/O-bound feed fetching, DNS resolution, and string-parsing workflows are completely stripped out of the HTTP cycle and managed via distributed background tasks.

### 3. Distributed Task Broker & Worker Fleet (Redis + Celery)
* **At-Least-Once Delivery:** Uses Redis as an in-memory message broker to distribute ingestion payloads uniformly across an auto-scaling cluster of Celery workers.
* **Idempotent Execution:** Tasks are locked using a Redis-backed distributed lock manager (`Redlock`), ensuring exactly one worker processes a specific URI feed stream at any given timestamp.

### 4. Native Parsing Engine (SIMD Optimization Core)
* **GIL Liberation:** Python's Global Interpreter Lock (GIL) overhead is bypassed by offloading heavy XML/Atom string operations.
* **C++20 Ingestion Core:** Critical string tokenization and date formatting are executed by a zero-dependency, bare-metal C++ library compiled with AVX-512/NEON SIMD optimization flags, accessed via FFI/gRPC.

### 5. Advanced State & Vector Storage Layer (PostgreSQL)
* **Declarative Range Partitioning:** The `feed_item` repository uses native PostgreSQL table partitioning structured chronologically by month.
* **Data Sharding:** Workspaces are horizontally partitioned via a deterministic hashing scheme mapped to isolated physical database nodes as user scale surpasses monolithic thresholds.

---

## 🔒 Multi-Tenancy & Cryptographic Security

SimpleFeed++ treats workspace isolation as a database-level primitive rather than a fragile application-layer check.

* **Database Row-Level Security (RLS):** Every single query executed against workspace records carries an implicitly injected tenant context (`workspace_id`). RLS policies defined directly within PostgreSQL prevent cross-tenant data leaks.
* **Granular ACL Permissions:** A bitmask-based Access Control List system enables precise per-user permissions (`READ_FEED`, `WRITE_ITEM`, `MANAGE_WORKSPACE`, `EXECUTE_AI_TRIAGE`).

---

## 🤖 Key Features & AI Triage Pipeline

Every incoming feed entry passes through an automated machine learning pipeline to ensure absolute alignment with the platform's core axioms.

* **Semantic Ingestion Filtering:** Content text is vectorized into high-dimensional embeddings using a 768-d Transformer model. The system evaluates the cosine similarity against dynamically maintained vector centroids for *Education*, *Career*, *Finance*, and *Life Planning* using `pgvector`. If the similarity drops below the threshold (τ = 0.72), the entry is discarded.
* **Smart Polling Decay (Exponential Backoff):** Polling schedules dynamically adapt:
  `ΔT_next = min(T_max, T_base × γ^n)`
  Where `n` represents consecutive checks without new axiomatic entries, and `γ = 1.5` represents the backoff multiplier.
* **State Engine Transition:** Ingested articles move through a strict, deterministic state machine:
  `Discovered ⟶ Vector Triaged ⟶ Actionable (User Workspace) ⟶ Archived / Completed`

---

## 📂 Upgraded Project Structure

```text
simple-feed/
├── .github/                     # CI/CD pipelines & GitHub workflow freezes
├── frontend/                    # Strongly typed React SPA
│   ├── source/
│   │   ├── components/          # Isolated, axiomatic UI components
│   │   ├── hooks/               # TanStack Query API interactions
│   │   ├── types/               # Auto-generated TypeScript interfaces
│   │   └── App.tsx              # Application entry point
│   ├── package.json
│   └── tsconfig.json            # Strict TypeScript compiler configurations
├── backend/
│   ├── ai/                      # Vector space & classification mechanics (pgvector)
│   ├── config/                  # Django REST framework & multi-database configurations
│   ├── db/                      # DDLs, partitioning logic, and RLS definitions
│   ├── feed/                    # Unified Workspace Logic Application (Models, Views)
│   └── workers/                 # Celery task execution, exponential polling loops
├── kernel/                      # Native bare-metal execution optimization
│   ├── CMakeLists.txt
│   ├── include/parser.hpp       # High-efficiency C++ tokenization definitions
│   └── source/parser.cpp           # SIMD AVX-512 optimized XML extraction
└── docker-compose.yml           # Local orchestration for Frontend, Backend, Redis, Postgres
```

---

## 🛠️ Enterprise Tech Stack

* **Frontend:** React 18+, TypeScript, TanStack Query (React Query), Vite.
* **Backend:** Python 3.14+ (Django REST Framework API), Celery (Distributed Workers).
* **Native Kernel:** C++20 (Bare-metal string parsing).
* **Data Layer:** PostgreSQL 16+ (With `pgvector`, Range Partitioning, Native RLS), Redis (Message Broker).
* **Infrastructure:** Linux, Docker, Kubernetes, GitHub Actions.

---

## 🚀 Governance & Review Policy

Upstream modifications to production logic require absolute validation. All continuous iterative contributions must be explicitly bounded to the testing directories to continually build out defensive fuzzing, TypeScript type-checking bounds, and concurrency race evaluations.
