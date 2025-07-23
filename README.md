# 🗳️ Polling System – Django + Docker + Redis

A real-time poll application built with Django, PostgreSQL, Redis, and Docker Compose. Built for resilience, clarity, and extendability — this stack supports vote caching, live results in the admin, and environment-safe orchestration.

---

## 🚀 Features

- RESTful API to fetch poll results and submit votes
- Redis-powered vote tracking with rate limits
- Docker Compose stack with healthchecks and startup logic
- Automated migrations, data loading, and superuser setup
- Customized Django Admin view for live poll results
- JavaScript-powered admin refresh UI
- ASGI deployment via Uvicorn

---

## 🧱 Tech Stack

| Component     | Usage                                   |
|---------------|------------------------------------------|
| Django        | Backend app, ORM, admin                 |
| PostgreSQL    | Persistent poll data storage            |
| Redis         | Vote tracking, rate limiting            |
| Docker        | Containerized development & deployment |
| Docker Compose| Multi-service orchestration             |
| JavaScript    | Live results rendering in admin         |

---

## 🐳 Setup Instructions

1. **Build and start the stack**:
   ```bash
   docker-compose up --build -d
