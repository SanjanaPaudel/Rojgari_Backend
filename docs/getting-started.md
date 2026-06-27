# Getting Started Guide 🚀

Welcome to Rojgari! This document will help you get your local development environment up and running quickly.

---

## 📋 Prerequisites

Make sure you have the following installed on your machine:
* **Python**: Version `3.12` or higher.
* **uv**: Astral's package installer (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
* **Docker & Docker Compose**: To orchestrate database and caching services.
* **Make**: (Optional, but highly recommended) for executing shortcuts in the `Makefile`.

---

## ⚙️ Configuration Setup

Settings are managed via environment variables. By default, the application reads from the `.env` file in the project root.

1. **Create your `.env`**:
   ```bash
   cp .env.example .env
   ```
2. **Review Default Variables**:
   * `DEBUG`: Set to `True` for detailed tracebacks; `False` in production.
   * `DATABASE_URL`: Connection string pointing to Postgres or SQLite.
   * `CACHE_URL`: Connection string pointing to Valkey/Redis.

---

## 🏃 Running the Application

You can run the project in two environments: **Docker** or **Locally**.

### Option A: Running with Docker Compose (Recommended)
This boots the Django application, PostgreSQL, and Valkey automatically without requiring anything installed locally besides Docker.

```bash
# Build the containers (first-time boot or dependency changes)
make build

# Start the services (Django on http://localhost:8000)
make dev

# Run migrations and seed data in another terminal (defaults to 10 users)
make migrate
make seed

# Seed a custom number of users
make seed USERS=50
```

### Option B: Running Locally (SQLite Fallback)
If you don't want to run Docker, you can run the project locally. It will fall back to SQLite for the database and you'll need to point caching to a local instance.

```bash
# Setup virtual environment and install dependencies
make local-setup

# Apply migrations and run the dev server
make local-run

# Seed the database locally (defaults to 10 users, customize with USERS=N)
make local-seed
```

---

## 🔍 Logs & Diagnostics

* **Check Django and Database logs**:
  ```bash
  make logs
  ```
* **Verify Health Check Endpoint**:
  Once the server is running, visit:
  [http://localhost:8000/status/](http://localhost:8000/status/)
  
  You should see:
  ```json
  {
    "database": "healthy",
    "cache": "healthy"
  }
  ```
