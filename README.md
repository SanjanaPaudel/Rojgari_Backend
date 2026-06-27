# Rojgari 💼

Rojgari (meaning "Employment") is a Django-based web application configured with a modern Python environment, containerized development support, a PostgreSQL database, and a Valkey caching layer.

---

## Technical Stack
* **Python Package Manager**: `uv` (Astral's high-performance resolver and installer)
* **Web Framework**: Django 6.0+
* **Database**: PostgreSQL 16
* **Cache**: Valkey 8.0 (wire-compatible with Redis protocol)
* **Containerization**: Docker & Docker Compose
* **Testing & Factories**: `factory-boy` & `faker`

---

## 🛠️ CLI Commands Log

Here is the log of CLI commands used to set up the project:

### 1. Project Initialization & Dependencies
```bash
# Initialize a new Python project via uv
uv init

# Lower Python requirements to >=3.12 (in pyproject.toml) to match slim container images
# Then regenerate the lockfile
uv lock

# Add core web and utility dependencies
uv add django psycopg "psycopg[binary]" redis django-environ

# Add development and seeding dependencies
uv add factory-boy faker
```

### 2. Django Scaffolding
```bash
# Start Django project configuration
uv run django-admin startproject rojgari .

# Create the accounts application (User, UserDetail, and Work models)
uv run python manage.py startapp accounts
```

### 3. Database & Seeding Operations
```bash
# Detect database changes and generate migrations files
uv run python manage.py makemigrations

# Apply migrations to the configured database (e.g., PostgreSQL or SQLite)
uv run python manage.py migrate

# Seed the database with mock profiles and work history (defaults to 10 users)
uv run python manage.py seed

# Seed a custom number of users (e.g., 50 users)
uv run python manage.py seed --users 50
```

---

## 🐋 Dockerized Dev Environment

The project is pre-configured with a dockerized stack defining three isolated services in `docker-compose.yml`:
1. **`web`**: Django dev server running on port `8000`.
2. **`db`**: PostgreSQL 16 database utilizing a healthcheck verify script.
3. **`valkey`**: Valkey 8.0 caching layer.

### How to Run it

To boot the whole environment:
```bash
# Build and run containers in the foreground
docker compose up --build

# Run containers in detached mode (background)
docker compose up -d
```

### Testing Connectivity
A built-in status verification page is exposed to confirm database and Valkey health:
* **URL**: `http://localhost:8000/status/`
* **Response**:
  ```json
  {
    "database": "healthy",
    "cache": "healthy"
  }
  ```

---

## 📦 Git Repository Status

A git repository has been initialized inside the workspace. To commit the current files, run:

```bash
# Check status of untracked files
git status

# Add files to stage
git add .

# Make the initial commit
git commit -m "Initial commit: Django scaffolding with uv, Docker, Postgres, Valkey, and accounts seeder"
```
