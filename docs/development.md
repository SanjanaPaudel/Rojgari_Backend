# Django Development Guide 💻

This guide provides instructions and best practices for developing and expanding the Rojgari Django project.

---

## 📦 Package Management with `uv`

We use `uv` for lightning-fast package resolution. Avoid using bare `pip` commands.

* **Add a dependency**:
  ```bash
  uv add <package-name>
  ```
* **Add a development-only dependency**:
  ```bash
  uv add --dev <package-name>
  ```
* **Sync environment** (runs lock and installs dependencies):
  ```bash
  uv sync
  ```

---

## 🗄️ Database Migrations

Whenever you modify any model class in `models.py`:

1. **Generate Migration Files**:
   ```bash
   # Local run
   uv run python manage.py makemigrations
   
   # Docker-compose run
   docker compose exec web python manage.py makemigrations
   ```
2. **Apply Migrations**:
   ```bash
   # Local run (requires local database setup or SQLite fallback)
   uv run python manage.py migrate
   
   # Docker-compose run
   make migrate
   # (or: docker compose exec web python manage.py migrate)
   ```

---

## ⚡ Valkey Caching Layer

Valkey serves as the caching backend. Standard Django caching functions can be imported and used directly:

```python
from django.core.cache import cache

# Set cache (key, value, timeout_seconds)
cache.set("my_key", "my_value", timeout=60)

# Get cache
value = cache.get("my_key")
```

### Query Caching & Eviction Pattern
We implement query-level caching for read-heavy and static databases (e.g. [list_categories](file:///Users/pablo/Development/Projects/Rojgari/accounts/api/categories.py#L9)):
1. **Lookup**: Check Valkey first. If present, return data immediately.
2. **Fetch & Store**: If a cache miss occurs, query from database and save to cache.
3. **Invalidation**: Evict the cache key inside the model's `save()` and `delete()` overrides (see [ServiceCategory](file:///Users/pablo/Development/Projects/Rojgari/services/models.py#L6)) to prevent serving stale data.

To monitor caching operations in real-time, open the Valkey CLI inside the container:
```bash
docker compose exec valkey valkey-cli
# Then type 'MONITOR' to inspect all incoming command keys
```

---

## 🛠️ Adding a New Django App

If you need to isolate new business domains (e.g., `jobs`, `companies`):

1. **Scaffold the App**:
   ```bash
   uv run python manage.py startapp <app_name>
   ```
2. **Register it**: Add the app name to `INSTALLED_APPS` in [settings.py](file:///Users/pablo/Development/Projects/Rojgari/rojgari/settings.py).
3. **Build API Routes**: Add Ninja routing paths and link them to the main API router in [rojgari/urls.py](file:///Users/pablo/Development/Projects/Rojgari/rojgari/urls.py).

---

## 🧪 Testing

To ensure new endpoints or operations do not break core APIs, write tests in `<app_name>/tests.py` and run them:

```bash
# Docker-based test run
make test

# Local host machine test run
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py test
```
*Tip: Test cases automatically spin up an isolated test database and destroy it upon completion.*
