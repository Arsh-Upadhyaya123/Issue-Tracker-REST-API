# Issue Tracker API

### A lightweight backend for tracking work—from new bugs to completed fixes.

A clean, SQLite-backed REST API that turns an issue list into a usable service. Create tickets, assign priorities, move work through a simple status workflow, and query issues using filters and pagination—all through documented HTTP endpoints.

**Why this project?** Issue tracking is a familiar problem with real backend challenges: designing resource-oriented endpoints, validating requests, persisting state, and returning predictable errors. This implementation focuses on those fundamentals rather than a flashy UI.

**Tech:** Python · FastAPI · Pydantic · SQLite · unittest

## What it does

- **Issue lifecycle:** Create, list, view, update, and delete issues.
- **Workflow:** Track `todo`, `in_progress`, and `done` states and `low`, `medium`, `high` priorities.
- **Targeted queries:** Filter by status/priority and paginate results with `limit` and `offset`.
- **Input contracts:** Pydantic validation, useful HTTP status codes, and generated OpenAPI documentation.
- **Local persistence:** SQLite storage with parameterized SQL queries and UTC timestamps.
- **Automated checks:** API tests using Python's `unittest`.

## Run it in 60 seconds

Requires **Python 3.10+**.

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Open **http://127.0.0.1:8000/docs** to create and manage issues from the interactive API interface—no frontend required.

### Try a request

**POST** `/issues`

```json
{
  "title": "Fix login bug",
  "description": "Mobile sign-in fails intermittently",
  "priority": "high"
}
```

Other useful routes:

| Method | Route | Action |
| --- | --- | --- |
| `GET` | `/issues?status=todo&limit=10` | Filter and paginate |
| `GET` | `/issues/{issue_id}` | View one issue |
| `PATCH` | `/issues/{issue_id}` | Update fields or status |
| `DELETE` | `/issues/{issue_id}` | Delete an issue |

## Engineering choices

- **FastAPI + Pydantic** keep request schemas close to the endpoints and expose them in `/docs`.
- **SQLite** makes the service runnable locally without setting up a database server; `ISSUES_DB` overrides the default database path.
- **Parameterized SQL** keeps untrusted input out of query strings.
- **Bounded pagination** prevents unlimited responses (`limit` is capped at 100).

## Test

```bash
python -m unittest -v
```

## Project scope and next steps

This is a **local backend demonstration**, not a deployed multi-user product. Potential extensions include authentication and authorization, database migrations, optimistic concurrency, containerization, and CI.

**GitHub description:** FastAPI issue-tracking REST API with SQLite persistence, validated CRUD endpoints, workflow filters, pagination and automated tests.
