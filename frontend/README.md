# SimpleFeed++ Frontend Architecture Documentation

**Location:** `frontend/`  
**Stack:** React 18, TypeScript (Strict Mode), Vite, TanStack Query, React Virtual  

This document outlines the architectural boundaries, state management philosophy, and component design patterns for the SimpleFeed++ client application. 

In alignment with the **SZ Open Laboratory** systems engineering philosophy, this frontend is not treated as a dynamic, loosely-typed web page. It is engineered as a strictly governed, deterministic state machine compiled to run within the browser's JavaScript engine.

---

## 🎯 Engineering Philosophy: The Closed-World UI

The SimpleFeed++ client strictly enforces the **Closed-World Assumption** established by the backend. The UI is designed to minimize cognitive load, completely rejecting "infinite scroll" dopamine loops in favor of a utilitarian, high-signal workspace.

1. **Deterministic Rendering:** A specific application state (Redux/React Query cache + URL routing) must always yield the exact same DOM structure. No hidden side-effects.
2. **Type Contracts as ABI:** The boundary between the Django API and the client is treated like an Application Binary Interface. TypeScript interfaces are auto-generated from backend schemas; any mutation in the backend payload structure will intentionally break the frontend build at compile-time.
3. **$O(1)$ Memory Scaling:** The DOM is a severe bottleneck. Regardless of whether a workspace contains 10 or 100,000 archived articles, DOM node count and memory consumption must remain perfectly flat via strict virtualization.

---

## 🏗️ Core Subsystems

### 1. Asynchronous State Synchronization (TanStack Query)
We do not use Redux for server state. The client acts as a synchronized cache of the PostgreSQL database, managed entirely by TanStack Query (`react-query`).

* **Polling Decoupling:** The frontend does not dictate the polling interval. It subscribes to the backend's Exponential Polling Backoff state.
* **Optimistic UI Updates:** Moving an item through the workspace pipeline (`Actionable -> Archived`) mutates the local cache instantly, reconciling with the Django API asynchronously in the background to ensure zero latency for the user.

### 2. Type-Safe API Gateway
All network I/O is routed through a generated Axios client. 

* **No `any` Types:** The `any` keyword is strictly prohibited in this directory. 
* **Vector Triage Interfaces:** Feed items passed down as props must mathematically conform to the axiomatic vector models. If an object does not possess a valid `threshold_score` $\ge 0.72$, the TypeScript compiler prevents the `<FeedItem />` component from mounting it.

### 3. DOM Virtualization Kernel
Rendering long lists of data destroys client performance. We utilize `react-virtual` to map mathematical scroll offsets to absolute DOM positioning. 

* **Windowing:** The browser only ever renders the 12 to 15 nodes currently visible in the viewport. 
* **Hardware Acceleration:** Scrolling utilizes `transform: translateY()` rather than mutating margin/padding, pushing the paint calculations directly to the user's GPU.

---

## 🛡️ Security Architecture & Zero-Trust UI

Because SimpleFeed++ operates across a multi-tenant, sharded database architecture, the frontend implements a strict Zero-Trust security model to prevent cross-tenant data leakage and physical session hijacking.

### 1. Cross-Tenant Cache Poisoning Defense
Standard React Query implementations are vulnerable to cache leakage when switching contexts. We mathematically isolate memory by injecting the `activeWorkspaceId` into every TanStack query key array (e.g., `['feedItems', activeWorkspaceId, axiom]`). If the active database shard changes, the local memory context is instantly rendered invalid and unreachable.

### 2. The Global Kill Switch & Session Daemon
The Zustand `authStore` operates a passive background daemon monitoring DOM interaction. If 15 minutes of idle inactivity pass, it triggers an `IDLE_TIMEOUT` state. This fires a global `sz_memory_purge` browser event, commanding all local stores to self-destruct their ephemeral state and permanently clearing the React Query network cache.

### 3. Step-Up Authentication (Sudo Mode)
For destructive or highly privileged actions (such as mutating the `pgvector` index threshold or altering infrastructure telemetry), the UI intentionally aborts standard API calls. It mounts a strict `SudoModal` overlay, requiring the user to physically re-sign the transaction intent with their cryptographic passphrase, neutralizing walk-away session hijacking vectors.

### 4. RLS API Gateway Boundary
The Axios client intercepts all outbound network requests to seamlessly inject the `X-Workspace-ID` header. This explicitly informs the Django backend's Row-Level Security (RLS) policies which PostgreSQL shard partition the user is requesting, rejecting out-of-bounds memory access before it evaluates the Python application logic.

---

## 📂 Directory Structure

```text
frontend/
├── source/
│   ├── api/                 # Auto-generated Axios clients & OpenAPI type contracts
│   ├── assets/              # Static binaries, icons, and SVG definitions
│   ├── components/          # Pure, side-effect-free UI rendering functions
│   │   ├── common/          # Buttons, Modals, Virtualized Lists
│   │   ├── axioms/          # Domain-specific renderers (Education, Career, Finance, Life)
│   │   └── workspace/       # Drag-and-drop state boards
│   ├── hooks/               # Custom React hooks wrapping TanStack Query mutations
│   ├── store/               # Zustand (Local ephemeral UI state ONLY - no server data)
│   ├── types/               # Global TypeScript interface declarations
│   ├── utils/               # Pure mathematical and formatting utility functions
│   ├── App.tsx              # Root mounting and React Context providers
│   └── main.tsx             # Vite entry point & strict mode wrapper
├── .eslintrc.cjs            # Strict linting governance
├── tsconfig.json            # Compiler options (strict: true, noImplicitAny: true)
├── vite.config.ts           # Build pipeline and Hot Module Replacement (HMR) config
└── package.json
```

---

## 🔒 Governance & Code Freeze Policy

To ensure parity with the backend's strict systems-level guarantees, the `/frontend` directory operates under the following development constraints:

1. **The Test Directory Exemption:** Following the project-wide mandate, the core architecture is under a strict feature freeze. The only acceptable routine pull requests are those expanding the `/src/__tests__` directory.
2. **Component Purity Testing:** All components in `src/components/` must be pure functions. They must be accompanied by Vitest unit tests verifying that $f(props) = 	ext{Expected DOM}$.
3. **No Inline Styling:** CSS-in-JS or inline styles are prohibited to prevent runtime stylesheet generation overhead. We utilize pre-compiled atomic CSS (e.g., Tailwind) to ensure the stylesheet payload remains statically sized regardless of application scale.

---

## 🚀 Build & Execution

### Development Runtime
```bash
cd frontend
npm install
npm run dev
```

### Production Compilation
```bash
npm run build
```
*Vite will compile the TypeScript, tree-shake dead code, and output a highly optimized static bundle ready to be served via Nginx or a CDN.*
