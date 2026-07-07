---
name: tracker-cli
description: >
  Interact with the local job tracker database directly from the agent terminal.
  No separate CLI script or running web server needed — the agent writes Python
  sqlite3 code inline to read and update the DB. The kanban board polls every
  5 seconds and automatically reflects the changes.
triggers:
  - "add * to tracker"
  - "add * job to the tracker"
  - "mark * as *"
  - "update * status"
  - "add note to *"
  - "list my applications"
  - "show tracker"
  - "search tracker"
---

# Tracker CLI Skill

## Purpose

The owner asks you to add, update, or look up job applications. You write
Python code directly using the `sqlite3` standard library to read/write
`tracker-web/data/tracker.db` — no separate CLI, no running server needed.

If the web app is running at `http://127.0.0.1:5050`, the kanban board will
pick up your DB changes automatically on its 5-second poll.

---

## Database location

```
{repo_root}/tracker-web/data/tracker.db
```

Resolve `{repo_root}` as the directory containing `AGENTS.md`.

---

## Schema

```sql
jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    posting_url TEXT,
    location TEXT,
    created_at TEXT NOT NULL          -- ISO-8601 UTC
)

applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL UNIQUE,   -- FK → jobs.id
    status TEXT NOT NULL,
    applied_at TEXT,                  -- ISO-8601 date or NULL
    next_action_at TEXT,
    outcome TEXT,
    updated_at TEXT NOT NULL
)

notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,  -- FK → applications.id
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
)
```

## Valid statuses

`Saved` · `Applied` · `Interview` · `Offer` · `Accepted` · `Rejected`

---

## Python template (use inline in run_in_terminal)

```python
import sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

DB = Path("/absolute/path/to/tracker-web/data/tracker.db")
now = datetime.now(timezone.utc).isoformat(timespec="seconds")

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")

# --- your operation here ---

conn.commit()
conn.close()
```

---

## Common operations

### Add a job
```python
cur = conn.execute(
    "INSERT INTO jobs (company, role, posting_url, location, created_at) VALUES (?,?,?,?,?)",
    ("Acme Corp", "Software Engineer", "https://acme.com/jobs/1", "Remote", now),
)
job_id = cur.lastrowid
conn.execute(
    "INSERT INTO applications (job_id, status, applied_at, next_action_at, outcome, updated_at) VALUES (?,?,NULL,NULL,'',?)",
    (job_id, "Saved", now),
)
```

### Update status
```python
conn.execute(
    "UPDATE applications SET status=?, updated_at=? WHERE job_id=(SELECT id FROM jobs WHERE lower(company) LIKE lower(?))",
    ("Applied", now, "%acme%"),
)
```

### Add a note
```python
app_id = conn.execute(
    "SELECT a.id FROM applications a JOIN jobs j ON j.id=a.job_id WHERE lower(j.company) LIKE lower(?)",
    ("%acme%",),
).fetchone()["id"]
conn.execute(
    "INSERT INTO notes (application_id, body, created_at) VALUES (?,?,?)",
    (app_id, "Phone screen scheduled for Thursday.", now),
)
conn.execute("UPDATE applications SET updated_at=? WHERE id=?", (now, app_id))
```

### List all applications
```python
rows = conn.execute(
    "SELECT j.company, j.role, a.status, a.applied_at FROM jobs j JOIN applications a ON a.job_id=j.id ORDER BY j.created_at DESC"
).fetchall()
for r in rows:
    print(f"{r['company']} — {r['role']}  [{r['status']}]")
```

---

## Hard rules

- Resolve DB path as absolute before connecting.
- Never commit or push after DB operations.
- Use only valid status values listed above.
- Do not fabricate company names, roles, or dates not provided by the owner.
