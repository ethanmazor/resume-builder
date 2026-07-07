from __future__ import annotations

import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "tracker.db"

STATUS_OPTIONS = [
    "Saved",
    "Applied",
    "Interview",
    "Offer",
    "Accepted",
    "Rejected",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    conn = connect_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                posting_url TEXT,
                location TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL,
                applied_at TEXT,
                next_action_at TEXT,
                outcome TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (application_id) REFERENCES applications (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_setting(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default
    return row["value"]


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        (key, value),
    )


def fetch_dashboard_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            j.id AS job_id,
            j.company,
            j.role,
            j.posting_url,
            j.location,
            j.created_at,
            a.id AS application_id,
            a.status,
            a.applied_at,
            a.next_action_at,
            a.outcome,
            a.updated_at,
            (
                SELECT COUNT(*)
                FROM notes n
                WHERE n.application_id = a.id
            ) AS note_count
        FROM jobs j
        LEFT JOIN applications a ON a.job_id = j.id
        ORDER BY j.created_at DESC
        """
    ).fetchall()


def export_snapshot(conn: sqlite3.Connection) -> tuple[Path, dict[str, Any]]:
    exported_at = utc_now_iso()

    jobs = [dict(row) for row in conn.execute("SELECT * FROM jobs ORDER BY id").fetchall()]
    applications = [
        dict(row)
        for row in conn.execute("SELECT * FROM applications ORDER BY id").fetchall()
    ]
    notes = [dict(row) for row in conn.execute("SELECT * FROM notes ORDER BY id").fetchall()]
    settings = {
        row["key"]: row["value"]
        for row in conn.execute("SELECT key, value FROM settings").fetchall()
    }

    payload = {
        "exported_at": exported_at,
        "version": 1,
        "jobs": jobs,
        "applications": applications,
        "notes": notes,
        "settings": settings,
    }

    safe_stamp = exported_at.replace(":", "-")
    latest_path = EXPORTS_DIR / "latest.json"
    stamped_path = EXPORTS_DIR / f"export-{safe_stamp}.json"

    latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    stamped_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return stamped_path, payload


def run_git_export(repo_path: str, branch: str) -> tuple[bool, str]:
    repo = Path(repo_path).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        return False, f"Export repo path does not exist: {repo}"

    if not (repo / ".git").exists():
        return False, f"Not a git repository: {repo}"

    commit_message = f"tracker export {utc_now_iso()}"

    commands = [
        ["git", "-C", str(repo), "add", "."],
        ["git", "-C", str(repo), "commit", "-m", commit_message],
        ["git", "-C", str(repo), "push", "origin", branch],
    ]

    outputs: list[str] = []
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if out:
            outputs.append(out)
        if err:
            outputs.append(err)

        # Allow commit to fail when there is nothing to commit.
        if result.returncode != 0:
            joined = "\n".join(outputs)
            if "nothing to commit" in joined.lower() and "commit" in cmd:
                continue
            return False, joined or f"Command failed: {' '.join(cmd)}"

    return True, "\n".join(outputs)


app = Flask(__name__)
app.secret_key = "local-dev-secret-change-if-needed"


@app.route("/")
def index() -> str:
    conn = connect_db()
    try:
        rows = fetch_dashboard_rows(conn)
        export_repo_path = get_setting(conn, "export_repo_path")
        export_branch = get_setting(conn, "export_branch", "main")
    finally:
        conn.close()

    return render_template(
        "index.html",
        rows=rows,
        statuses=STATUS_OPTIONS,
        export_repo_path=export_repo_path,
        export_branch=export_branch,
    )


@app.route("/jobs", methods=["POST"])
def create_job() -> Any:
    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()
    posting_url = request.form.get("posting_url", "").strip()
    location = request.form.get("location", "").strip()

    if not company or not role:
        flash("Company and role are required.", "error")
        return redirect(url_for("index"))

    conn = connect_db()
    try:
        cur = conn.execute(
            """
            INSERT INTO jobs (company, role, posting_url, location, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company, role, posting_url, location, utc_now_iso()),
        )
        job_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO applications (job_id, status, applied_at, next_action_at, outcome, updated_at)
            VALUES (?, ?, NULL, NULL, '', ?)
            """,
            (job_id, "Saved", utc_now_iso()),
        )
        conn.commit()
    finally:
        conn.close()

    flash("Job added.", "success")
    return redirect(url_for("index"))


@app.route("/applications/<int:application_id>/status", methods=["POST"])
def update_status(application_id: int) -> Any:
    status = request.form.get("status", "").strip()
    applied_at = request.form.get("applied_at", "").strip() or None
    next_action_at = request.form.get("next_action_at", "").strip() or None
    outcome = request.form.get("outcome", "").strip()

    if status not in STATUS_OPTIONS:
        flash("Invalid status.", "error")
        return redirect(url_for("index"))

    conn = connect_db()
    try:
        conn.execute(
            """
            UPDATE applications
            SET status = ?, applied_at = ?, next_action_at = ?, outcome = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, applied_at, next_action_at, outcome, utc_now_iso(), application_id),
        )
        conn.commit()
    finally:
        conn.close()

    flash("Application updated.", "success")
    return redirect(url_for("index"))


@app.route("/applications/<int:application_id>/notes", methods=["POST"])
def add_note(application_id: int) -> Any:
    body = request.form.get("body", "").strip()
    if not body:
        flash("Note cannot be empty.", "error")
        return redirect(url_for("index"))

    conn = connect_db()
    try:
        conn.execute(
            """
            INSERT INTO notes (application_id, body, created_at)
            VALUES (?, ?, ?)
            """,
            (application_id, body, utc_now_iso()),
        )
        conn.commit()
    finally:
        conn.close()

    flash("Note added.", "success")
    return redirect(url_for("index"))


# ── JSON API (used by kanban drag-drop, auto-poll, and tracker-cli) ──────────

@app.route("/api/board")
def api_board() -> Any:
    conn = connect_db()
    try:
        rows = fetch_dashboard_rows(conn)
        last_updated = conn.execute(
            "SELECT MAX(updated_at) AS lu FROM applications"
        ).fetchone()["lu"] or ""
    finally:
        conn.close()

    columns: dict[str, list[dict[str, Any]]] = {s: [] for s in STATUS_OPTIONS}
    for row in rows:
        card = {
            "job_id": row["job_id"],
            "company": row["company"],
            "role": row["role"],
            "location": row["location"] or "",
            "posting_url": row["posting_url"] or "",
            "application_id": row["application_id"],
            "status": row["status"] or "Saved",
            "applied_at": row["applied_at"] or "",
            "next_action_at": row["next_action_at"] or "",
            "outcome": row["outcome"] or "",
            "note_count": row["note_count"] or 0,
            "updated_at": row["updated_at"] or "",
        }
        status = card["status"]
        if status in columns:
            columns[status].append(card)
        else:
            columns["Saved"].append(card)

    return jsonify({"columns": columns, "last_updated": last_updated})


@app.route("/api/applications/<int:application_id>/status", methods=["POST"])
def api_update_status(application_id: int) -> Any:
    data = request.get_json(force=True, silent=True) or {}
    status = (data.get("status") or "").strip()
    if status not in STATUS_OPTIONS:
        return jsonify({"error": f"Invalid status: {status}"}), 400

    conn = connect_db()
    try:
        conn.execute(
            "UPDATE applications SET status = ?, updated_at = ? WHERE id = ?",
            (status, utc_now_iso(), application_id),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"ok": True, "application_id": application_id, "status": status})


@app.route("/api/applications/<int:application_id>/notes")
def api_get_notes(application_id: int) -> Any:
    conn = connect_db()
    try:
        rows = conn.execute(
            "SELECT id, body, created_at FROM notes WHERE application_id = ? ORDER BY created_at DESC",
            (application_id,),
        ).fetchall()
    finally:
        conn.close()
    return jsonify({"notes": [dict(r) for r in rows]})


@app.route("/api/applications/<int:application_id>/notes", methods=["POST"])
def api_add_note(application_id: int) -> Any:
    data = request.get_json(force=True, silent=True) or {}
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"error": "body is required"}), 400

    conn = connect_db()
    try:
        cur = conn.execute(
            "INSERT INTO notes (application_id, body, created_at) VALUES (?, ?, ?)",
            (application_id, body, utc_now_iso()),
        )
        note_id = cur.lastrowid
        conn.execute(
            "UPDATE applications SET updated_at = ? WHERE id = ?",
            (utc_now_iso(), application_id),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"ok": True, "note_id": note_id})


# ── Form endpoints (legacy / export) ─────────────────────────────────────────

@app.route("/settings/export", methods=["POST"])
def save_export_settings() -> Any:
    repo_path = request.form.get("repo_path", "").strip()
    branch = request.form.get("branch", "main").strip() or "main"

    conn = connect_db()
    try:
        set_setting(conn, "export_repo_path", repo_path)
        set_setting(conn, "export_branch", branch)
        conn.commit()
    finally:
        conn.close()

    flash("Export settings saved.", "success")
    return redirect(url_for("index"))


@app.route("/export", methods=["POST"])
def export_now() -> Any:
    conn = connect_db()
    try:
        export_path, _payload = export_snapshot(conn)
        repo_path = get_setting(conn, "export_repo_path")
        branch = get_setting(conn, "export_branch", "main")
    finally:
        conn.close()

    if not repo_path:
        flash(f"Local export complete: {export_path}", "success")
        return redirect(url_for("index"))

    ok, output = run_git_export(repo_path, branch)
    if ok:
        flash(f"Export pushed to git repo. Snapshot: {export_path}", "success")
    else:
        flash(f"Export created but git push failed: {output}", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
