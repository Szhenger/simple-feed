# SimpleFeed++ Frontend Architecture & API Integration

**Document Owner:** Core Engineering  
**System:** SimpleFeed++ Single Page Application (SPA)  
**Target Environment:** React 18 / TypeScript / Vite

---

## 1. Executive Summary

Under the **ShuAndy Engineering** framework, the SimpleFeed++ frontend is not merely a display layer; it is a strict, compiler-verified client bound to the stateless Django API gateway. It operates under the constraints of a **Closed-World Assumption**, meaning the UI must mathematically align with the backend's Row-Level Security (RLS) policies, JWT lifecycle, and high-throughput vector payloads.

This document outlines the architectural abstractions and data-flow constraints required to safely render AI-triaged feeds without breaking the browser's main thread or violating multi-tenant boundaries.

---

## 2. Compiler-Verified API Contracts

We strictly prohibit manual type definitions for API responses. Because the backend acts as a single source of truth via its OpenAPI V3 schema (`drf-spectacular`), the frontend must derive its entire data layer via automated code generation.

### The Code-Gen Pipeline
Instead of manually writing `interface FeedItem { ... }`, the CI/CD pipeline executes a schema synchronization step (e.g., using `openapi-typescript` or `rtk-query-codegen`).

* **Zero `any` Types:** All network payloads, including the complex paginated responses containing $768$-dimensional vector similarity scores, are strictly typed at compile time.
* **Deterministic Refactoring:** If a backend engineer changes the `similarity_score` threshold or renames a category enum, the frontend build will instantly fail in CI, preventing runtime crashes in production.

---

## 3. Multi-Tenant State & Security Protocols

The database explicitly rejects queries that lack a valid workspace context. The frontend is responsible for injecting this context and managing the volatile lifecycle of the user's session.

### Workspace Context Injection
Every outbound request to the `/api/v1/feed/*` namespace must include the active workspace identifier. This is managed via an Axios/Fetch interceptor:
1. The global state manager (e.g., Zustand or React Context) holds the `activeWorkspaceId`.
2. The network interceptor reads this state and appends the `X-Workspace-ID` HTTP header to the request.
3. If the user switches workspaces, the UI must immediately invalidate the local query cache to prevent cross-contamination (rendering Tenant A's data in Tenant B's view).

### Stateless JWT Rotation & Blacklisting
The backend issues aggressive, short-lived Access Tokens (60 minutes) and strictly blacklists rotated Refresh Tokens. The UI must handle 401 Unauthorized responses invisibly:

1. **Trap the 401:** The HTTP interceptor catches the expired token response.
2. **Queue Requests:** Any concurrent outgoing requests are paused and placed in a promise queue.
3. **Rotate:** A single background request is dispatched to `/api/v1/auth/token/refresh/`.
4. **Replay & Flush:** Upon receiving the new token pair, local storage is updated, and the queued requests are replayed with the new Authorization header. 
*Note: If the refresh request fails (e.g., the refresh token is blacklisted or expired), the user is immediately purged from the application state and routed to `/login`.*

---

## 4. High-Performance DOM Rendering

The backend limits limit/offset pagination to dense batches of up to 50 items. Rendering hundreds of deep DOM nodes containing rich AI summaries and parsed XML will cause frame drops and battery drain if handled natively.

### Viewport Virtualization
To maintain a 60 FPS scrolling experience, lists rendering `FeedItems` must be virtualized. 
* **Implementation:** Utilizing libraries like `@tanstack/react-virtual` or `react-window`.
* **Mechanics:** The React tree only renders the physical DOM nodes currently visible within the user's screen viewport (plus a small overscan buffer). As the user scrolls, nodes that exit the top of the screen are unmounted and recycled at the bottom.

### Resiliency Under Rate Limiting (HTTP 429)
The API gateway enforces strict throttling (`1000/minute` for authenticated users). If the user rapidly switches workspaces or scrubs through pages, the UI may trigger a 429 Too Many Requests response.
* **Exponential Backoff:** Background data fetching (like polling for AI triage updates) must catch the 429 and apply a mathematical backoff (e.g., wait 2s, 4s, 8s) before retrying.
* **Graceful Degradation:** The UI must catch user-initiated 429s and display a non-blocking toast notification indicating network saturation, rather than throwing an unhandled promise rejection to the console.

---

## 5. Axiomatic UI Mapping

The frontend must map the backend's core database enums directly to the user experience. The four Professional Axioms defined in `ai/centroids.py` dictate the primary navigation and filtering sidebars.

| Backend Enum (`AxiomChoices`) | UI Representation / Filtering Tab |
| :--- | :--- |
| `EDUCATION` | Technical Skills & Academic Research |
| `CAREER` | Engineering Leadership & Systems |
| `FINANCE` | Capital Allocation & Macro |
| `LIFE` | Deterministic Tracking & Longevity |

By maintaining strict parity between the AI's mathematical vector centroids and the React router's navigation paths, the system presents a unified, deterministic interface to the end user.
