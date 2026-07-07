---
name: start-tracker
description: >
  Start the local job tracker web server. Ensures virtualenv + dependencies
  exist, then launches the app on localhost.
triggers:
  - "start tracker"
  - "start the web tracker"
  - "run tracker"
  - "launch tracker web app"
user-invocable: true
---

# Start Tracker Skill

## Purpose

Start the local job application tracker web app from this repo with a single
agent prompt.

Use this when the owner asks to launch the tracker UI.

## Steps

1. `cd` into the repo root first, then run:

```bash
cd /path/to/resume-builder   # must be the repo root, not the parent folder
./scripts/start-tracker.sh
```

2. Wait for the Flask startup output. Confirm the server is listening on:

```text
http://127.0.0.1:5050
```

3. Tell the owner the tracker is running and where to open it.

## Hard rules

- Do not run in the background unless explicitly asked.
- Do not modify source-of-truth data files just to start the server.
- Leave all changes uncommitted.
