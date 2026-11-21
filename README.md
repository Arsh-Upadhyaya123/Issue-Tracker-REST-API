# Issue Tracker REST API

**GitHub description:** Production-style issue tracking REST API built with FastAPI, Pydantic and SQLite, featuring CRUD, filtering, pagination and automated tests.

## Skills demonstrated
Python · REST APIs · validation · SQL/SQLite · CRUD · HTTP status codes · automated testing

## Quick start
```bash
python -m pip install -r requirements.txt
uvicorn app:app --reload
```
Visit `http://127.0.0.1:8000/docs` to try the interactive OpenAPI UI.

```bash
curl -X POST http://127.0.0.1:8000/issues -H 'Content-Type: application/json' \
  -d '{"title":"Fix login bug","description":"Reproduce on mobile","priority":"high"}'
curl 'http://127.0.0.1:8000/issues?priority=high&limit=10'
python -m unittest -v
```

## Architecture
FastAPI handles routing and schema validation; SQLite provides durable local storage; SQL statements use parameterized queries. Status values: `todo`, `in_progress`, `done`. Set `ISSUES_DB` to choose a database file.

## Improvements to build next
Add authentication, optimistic locking, Alembic migrations, Docker and CI. **Not** deployed or authenticated in this starter version.
