# Alembic migrations

Generate a fresh migration after model changes:

```powershell
alembic revision --autogenerate -m "describe the change"
```

Apply pending migrations:

```powershell
alembic upgrade head
```

Roll back one revision:

```powershell
alembic downgrade -1
```

The Alembic env loads `app.core.config.settings.DATABASE_URL`, so the same
connection used at runtime is used for migrations — no need to set
`sqlalchemy.url` in `alembic.ini` for normal operation.
