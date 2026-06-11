# Database Migrations

Use Alembic for production schema changes.

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The app also runs a small compatibility migration at startup for older local
databases that predate the order lifecycle columns. That is only a development
safety net; production deploys should run Alembic before starting the app.
