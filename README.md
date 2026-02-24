# Nexus-A-Full-Stack_AI-Driven-E-Commerce-Architecture
An end-to-end, containerized e-commerce architecture. Integrates a modern frontend, scalable microservices, cloud deployment, and a machine learning engine for real-time customer churn prediction.

---------------------
## About The Project:

Nexus is a comprehensive, scalable e-commerce platform designed to demonstrate end-to-end system engineering. Going beyond basic CRUD operations, this project integrates a robust polyglot persistence backend, a responsive user interface, and cloud-native infrastructure.

At its core lies an intelligent data science engine, leveraging predictive models (such as Random Forest and GBM) to analyze customer behavior and proactively prevent churn. Developed with a strong focus on pragmatic, clean code principles, the entire architecture is containerized using Docker and orchestrated for seamless cloud deployment. It serves as a blueprint for bridging the gap between software development, data science, and cloud operations.

----------------------
##  Tech Stack & Architecture (Work in Progress)

This project is actively being developed as a microservices-oriented monorepo. The current and planned technology stack includes:

###  Infrastructure & DevOps
* **Docker & Docker Compose:** Containerization and local orchestration of the microservices environment.
* **Git & GitHub:** Version control and monorepo management.

###  Databases (Polyglot Persistence Layer)
* **PostgreSQL:** ACID-compliant relational database for Users, Orders, and financial transactions.
* **MongoDB:** Document-based NoSQL database for the flexible Product catalog schema.
* **Redis:** In-memory data store for caching and shopping cart management.

### Data Science & Machine Learning (Upcoming)
* **R (Random Forest / GBM):** Customer churn prediction model, integrated as a standalone microservice.
* **Python (FastAPI / Flask):** API layer to serve the machine learning models to the core backend.

### Backend API & Business Logic (Upcoming)
* *(e.g., Node.js with Express / Java with Spring Boot)*

### Frontend (Upcoming)
* *(e.g., React.js / Vue.js)*
----------------------

## System Architecture & Repository Structure

To adhere to pragmatic engineering principles, this project is structured as a **modular monorepo**. Each domain—from user interfaces to machine learning models—is heavily isolated to ensure a strict separation of concerns. This prevents tangled codebases and allows independent scaling. 

Despite being developed in different environments, the entire ecosystem is orchestrated seamlessly using Docker.

```text
nexus-retail-architecture/
│
├── /frontend/           # UI Layer: Responsive web application for customers and admins (React/Vue).
│
├── /backend/            # Core API: Business logic, secure authentication, and polyglot database management (PostgreSQL, MongoDB, Redis).
│
├── /data-science/       # AI Engine: Customer churn prediction models (built with R, Random Forest, GBM) and a Python API wrapper for backend integration.
│
├── /infrastructure/     # Cloud & Network: Nginx configurations for API Gateway, load balancing, and cloud deployment scripts.
│
└── docker-compose.yml   # Orchestration: The central configuration that boots up the entire microservice ecosystem with a single command.
```

Module Breakdown
frontend/: Handles the visual presentation and client-side state management. It communicates strictly with the backend via RESTful APIs, keeping the UI completely decoupled from the data layer.

backend/: The backbone of the application. It processes orders, manages the product catalog, and acts as the central hub that routes data between the frontend, the databases, and the data science engine.

data-science/: This directory houses the analytical intelligence of the platform. By analyzing historical user data, it serves predictive insights (like churn probability) back to the core system to trigger automated retention strategies.

infrastructure/: Contains the necessary configurations to take the application from a local development environment to a production-ready cloud deployment, ensuring security and network stability.

---------------------

## Database Architecture: The Polyglot Persistence Approach

In modern, high-traffic e-commerce ecosystems, a single database paradigm is often a bottleneck. To ensure scalability, data integrity, and system flexibility, this project implements a **Polyglot Persistence** architecture. This means strategically matching the right database technology to the specific characteristics of each domain.

###  Why PostgreSQL? (Users & Orders)
* **ACID Compliance & Strict Schema:** Financial transactions (Orders) and sensitive credentials (Users) require absolute data integrity, strict rules, and consistency. 
* **Relational Power:** Tracking which user bought which item at what time requires robust, relationship-driven SQL structures.

###  Why MongoDB? (Products)
* **Schema Flexibility (NoSQL):** A product catalog is inherently dynamic. A high-end laptop requires completely different data fields (RAM, CPU, GPU) than a t-shirt (Size, Fabric, Color). MongoDB's document-based nature allows for an inherently flexible `attributes_json` field. This eliminates the need for complex, inefficient SQL anti-patterns (like EAV tables) or tables filled with `NULL` values.

-------

## System Blueprint (ER Diagram)
<img width="1104" height="609" alt="er-diagram" src="https://github.com/user-attachments/assets/92723209-d233-4461-9e15-34b0a65e2cf5" />

-------

## Key Architectural Decisions & Engineering Trade-offs

Beyond simply connecting tables, the database layer was designed with enterprise-level security and financial accuracy in mind:

1. **UUIDs Over Auto-Incrementing IDs (Security First):** Instead of using predictable sequential integers (e.g., ID: 1, 2, 3), all primary keys (`user_id`, `order_id`) utilize universally unique identifiers (`gen_random_uuid()`). This effectively neutralizes **ID Enumeration Attacks** (preventing malicious users from scraping order data by simply guessing the next ID) and makes the system ready for distributed database scaling.

2. **Historical Financial Immutability (The `unit_price` Snapshot):**
   In the `order_items` table, the `unit_price` is distinctly recorded at the exact moment of checkout. This is a critical e-commerce rule: if a product's price in the MongoDB catalog is updated tomorrow, the historical invoices and total amounts of yesterday's orders remain strictly untouched and accurate.

3. **Cross-Database Referencing (Decoupling):**
   Notice that the `product_id` inside the PostgreSQL `order_items` table acts as a "soft" foreign key. It stores the `_id` string from MongoDB. The actual relationship constraint is handled elegantly at the backend application (API) layer, keeping the microservices completely decoupled.

---

## Tech Stack & Tools
| Category | Technologies |
| :--- | :--- |
| **Database & Caching** | ![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white) ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white) ![ElasticSearch](https://img.shields.io/badge/-ElasticSearch-005571?style=for-the-badge&logo=elasticsearch)|
| **DevOps, Cloud & Architecture**|![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)|
| **Backend & API (Microservices)**|![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-e92063?style=for-the-badge&logo=pydantic&logoColor=white) ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)|
| **Frontend & Mobile Clients**|![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) ![Swift](https://img.shields.io/badge/swift-F54A2A?style=for-the-badge&logo=swift&logoColor=white) ![iOS](https://img.shields.io/badge/iOS-000000?style=for-the-badge&logo=ios&logoColor=white)|

---
