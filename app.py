"""SQLite-backed issue tracker REST API. Run: uvicorn app:app --reload"""
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv('ISSUES_DB', 'issues.sqlite3'))
Status = Literal['todo', 'in_progress', 'done']
Priority = Literal['low', 'medium', 'high']


@contextmanager
def connection():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    with connection() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS issues (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL, description TEXT NOT NULL,
          status TEXT NOT NULL, priority TEXT NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title='Issue Tracker API', version='1.0.0', lifespan=lifespan)


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default='', max_length=2000)
    priority: Priority = 'medium'


class IssuePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: Status | None = None
    priority: Priority | None = None


class Issue(IssueCreate):
    id: int
    status: Status
    created_at: str
    updated_at: str


def fetch_one(issue_id: int):
    with connection() as db:
        row = db.execute('SELECT * FROM issues WHERE id=?', (issue_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail='Issue not found')
    return dict(row)


@app.post('/issues', response_model=Issue, status_code=201)
def create_issue(payload: IssueCreate):
    now = datetime.now(timezone.utc).isoformat()
    with connection() as db:
        cur = db.execute('''INSERT INTO issues (title, description, status, priority, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (payload.title, payload.description, 'todo', payload.priority, now, now))
        issue_id = cur.lastrowid
    return fetch_one(issue_id)


@app.get('/issues', response_model=list[Issue])
def list_issues(status: Status | None = None, priority: Priority | None = None,
                limit: int = Query(default=50, ge=1, le=100),
                offset: int = Query(default=0, ge=0)):
    clauses, args = [], []
    if status:
        clauses.append('status=?')
        args.append(status)
    if priority:
        clauses.append('priority=?')
        args.append(priority)
    where = (' WHERE ' + ' AND '.join(clauses)) if clauses else ''
    with connection() as db:
        rows = db.execute('SELECT * FROM issues' + where +
                          ' ORDER BY id DESC LIMIT ? OFFSET ?', (*args, limit, offset)).fetchall()
    return [dict(row) for row in rows]


@app.get('/issues/{issue_id}', response_model=Issue)
def get_issue(issue_id: int):
    return fetch_one(issue_id)


@app.patch('/issues/{issue_id}', response_model=Issue)
def update_issue(issue_id: int, payload: IssuePatch):
    fetch_one(issue_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        return fetch_one(issue_id)
    if any(value is None for value in changes.values()):
        raise HTTPException(422, 'Fields cannot be null')
    changes['updated_at'] = datetime.now(timezone.utc).isoformat()
    columns = ', '.join(f'{key}=?' for key in changes)
    with connection() as db:
        db.execute('UPDATE issues SET ' + columns + ' WHERE id=?', (*changes.values(), issue_id))
    return fetch_one(issue_id)


@app.delete('/issues/{issue_id}', status_code=204)
def delete_issue(issue_id: int):
    fetch_one(issue_id)
    with connection() as db:
        db.execute('DELETE FROM issues WHERE id=?', (issue_id,))
