# Neon PostgreSQL Setup

## Prerequisites

- Python 3.12+
- `uv` package manager (or pip)
- A [Neon](https://neon.tech) account

## Step 1: Sign Up & Create a Project

1. Go to https://neon.tech and sign up (GitHub/Google/email)
2. Click **Create a project**
3. Choose region (e.g., `ap-southeast-1`)
4. Copy the connection string from the dashboard

**Example connection string:**
```
postgresql://neondb_owner:password@ep-xxxx.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

## Step 2: Update Environment Variables

In `.env`, set `DATABASE_URL` to your Neon connection string:

```env
DATABASE_URL=postgresql://neondb_owner:password@ep-xxxx.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

> ⚠️ **Note:** The connection string must include `?sslmode=require` for Neon.

## Step 3: Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### Required Package for Neon

`psycopg` (or `psycopg[binary]`) is the PostgreSQL adapter. It is already included in:

- `pyproject.toml`: `psycopg[binary]>=3.3.4`
- `requirements.txt`: `psycopg==3.3.4` and `psycopg-binary==3.3.4`

No additional Neon-specific package is needed — Neon is standard PostgreSQL.

## Step 4: Run Migrations

```bash
# Create new migrations (if models changed)
python manage.py makemigrations

# Apply all migrations to Neon
python manage.py migrate

# View SQL for a specific migration
python manage.py sqlmigrate accounts 0001

# List all migrations and their status
python manage.py showmigrations

# Fake-mark a migration as applied (without running it)
python manage.py migrate accounts 0001 --fake
```

## Step 5: Verify Connection

```bash
# Open Django shell and test
python manage.py shell
```

```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT current_database();")
    print(cursor.fetchone())
# Should print: ('neondb',)
```

## Common Migration Commands

| Command | Purpose |
|---------|---------|
| `python manage.py makemigrations` | Generate migration files from model changes |
| `python manage.py migrate` | Apply all pending migrations |
| `python manage.py migrate <app> <migration_name>` | Migrate to a specific migration |
| `python manage.py showmigrations` | Show all migrations with apply status |
| `python manage.py sqlmigrate <app> <migration_id>` | View the SQL for a migration |
| `python manage.py migrate <app> zero` | Rollback all migrations for an app |
| `python manage.py makemigrations --empty <app>` | Create an empty migration for manual edits |

## Troubleshooting

- **SSL errors**: Ensure `?sslmode=require` is appended to the connection URL
- **Connection refused**: Check if the Neon IP allowlist includes your IP
- **Authentication failed**: Verify username/password in the connection string
- **Database not found**: The database name in the URL must match your Neon project

## Useful Links

- [Neon Docs: Connect from any application](https://neon.tech/docs/connect/connect-from-any-app)
- [Neon Dashboard](https://console.neon.tech)
