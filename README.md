# SimpleFeed++: A Distributed Web Feed Infrastructure

**SimpleFeed++** is a high-availability RSS/Atom discovery and management engine built with Python and Django. Beyond simple subscription management, the project serves as a sandbox for exploring **distributed data ingestion**, **manual sharding**, and **fault-tolerant deployment**.

Created and maintained under the **SZ Open Laboratory** — a personal initiative focused on systems-level compilers and infrastructure.

---

## 🏗 Distributed Architecture & Deployment

Unlike standard monolithic feed readers, **SimpleFeed++** is architected to handle high-concurrency ingestion and reliable content delivery:
*   **Distributed Task Execution:** Utilizes a multi-threaded task runner and scheduler to perform automated, daily ingestion of global feeds without blocking the primary application server.
*   **Manual Replication & Sharding:** Engineered with a custom replication and sharding scheme designed to handle high-concurrency data ingestion and ensure system fault tolerance.
*   **Containerized Orchestration:** Orchestrated for deployment on **Render**, leveraging its containerized environment to manage automated service replication and load balancing.
*   **Scalable Schema:** Features a robust Django ORM schema designed to manage complex relationships between users, granular feed permissions, and high-volume entry archival.

---

## 🚀 Key Features

*   **Automated Ingestion:** Daily updates powered by `schedule` + background threading (7:30 AM).
*   **Privacy Controls:** Toggle feeds between public/private and active/inactive.
*   **Discovery Engine:** "Random Feed" explorer to discover public content across the user base.
*   **User Management:** Full authentication suite (register, login, logout) including personalized profiles.
*   **Admin Suite:** Integrated dashboard for managing users, feeds, and entry archival.

---

## 📂 Project Structure

*   **`feed/models.py`** — Custom `User`, `Profile`, `Feed`, and `Item` models designed for high-concurrency.
*   **`feed/util.py`** — Core ingestion logic using `feedparser` with database-level persistence.
*   **`feed/views.py`** — Implementation of core interaction logic and permission gateways.
*   **`feeds/urls.py`** — Route mapping for the main infrastructure interface.
*   **`django/settings.py`** — Production-ready configuration utilizing **PostgreSQL** and custom user models.

---

## 🛠 Tech Stack

*   **Languages:** Python, SQL, HTML/CSS.
*   **Frameworks:** Django (REST), PostgreSQL.
*   **Tools:** Linux, Git, Docker/Containerized Environments (Render), CI/CD Automation.


