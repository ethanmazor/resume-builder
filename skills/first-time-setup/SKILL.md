---
name: first-time-setup
description: >
  Guided first-run walkthrough for a brand-new clone of this repo. Checks the
  toolchain, runs bootstrap if the source of truth is empty, and points the
  owner at their next step (fetch a job, build a resume, start the tracker).
  Use this when the owner is new to the repo or asks how to get started.
triggers:
  - "first time setup"
  - "get me set up"
  - "how do I get started"
  - "set up this repo"
  - "onboard me"
user-invocable: true
argument-hint: "[optional: path to your existing data folder]"
---

# First-Time Setup Skill

## Purpose

A single entry point for someone who just cloned this repo. It walks the owner
through everything needed before they can build a tailored resume, delegating
to the other skills rather than duplicating their logic.

Run this top-to-bottom, stopping to ask the owner questions where noted. Don't
skip steps just because they look done — verify each one.

---

## Step 1 — Check the toolchain

```bash
command -v tectonic >/dev/null && echo "tectonic: OK" || echo "tectonic: MISSING"
command -v pdfinfo  >/dev/null && echo "pdfinfo:  OK" || echo "pdfinfo:  MISSING"
python3 --version   >/dev/null 2>&1 && echo "python3:  OK" || echo "python3:  MISSING"
```

If `tectonic` or `pdfinfo` is missing, tell the owner to run:

```bash
brew install tectonic poppler
```

Don't proceed to a resume build until both are present, but you can still do
Steps 2–3 without them.

---

## Step 2 — Check whether the source of truth is already populated

Check for real content (not just placeholder files):

```bash
test -s data/profile/profile.yaml && grep -q 'name: *"..*"' data/profile/profile.yaml && echo "profile: POPULATED" || echo "profile: EMPTY"
```

Also glance at `data/facts/experience.yaml` and `data/facts/projects.yaml` for
non-empty entries.

### Case A — Already populated

Report what's already there (name, # of experience entries, # of projects) and
skip to Step 4.

### Case B — Empty

Ask the owner (unless they already gave a path as this skill's argument):

> "Where's your existing resume / notes / project data? Give me a folder path
> and I'll run bootstrap against it."

Once you have a path, run the **`bootstrap`** skill against it
(`skills/bootstrap/SKILL.md`) — do not reimplement its logic here, invoke it.
Bootstrap will ingest the data AND build a comprehensive bullet pool for each
experience and project. After bootstrap finishes, review its gap report and
bullet pool proposals with the owner before moving on.

---

## Step 3 — Confirm `.sync-config.yaml`

Bootstrap should have written `.sync-config.yaml` at the repo root (gitignored).
Confirm it exists and points at a real path:

```bash
cat .sync-config.yaml 2>/dev/null || echo "No .sync-config.yaml yet — sync will not work until bootstrap runs."
```

This is what lets the owner later say "sync my data" to pull in new material.

---

## Step 4 — Explain the day-to-day workflow

Tell the owner, briefly, what happens next:

1. **Add a job description** — drop a JD in `data/jobs/{company-role}.md`, or
   ask to fetch one directly: *"fetch this job: https://..."* (`fetch-job` skill).
2. **Build a tailored resume** — *"build a resume for {company-role}"*
   (`build-resume` skill). Output lands in `resumes/{slug}/`.
3. **Track applications** (optional) — *"add {company} {role} to tracker"*
   (`tracker-cli` skill), or *"start tracker"* to open the kanban board
   (`start-tracker` skill) at `http://127.0.0.1:5050`.
4. **Add new material later** — *"sync my data"* (`sync` skill) incrementally
   merges anything new from the original data folder without touching existing
   content.

---

## Step 5 — Offer to do the next step now

Ask the owner:

> "Want me to fetch a job posting now, or do you already have one in
> `data/jobs/`?"

If they have one ready, offer to run `build-resume` immediately. If not, stop
here — setup is complete and they can come back anytime.

---

## Hard rules

- Never fabricate profile/experience data — this skill only orchestrates
  `bootstrap`; it doesn't invent content itself.
- Don't re-run `bootstrap` over already-populated data without warning the
  owner first (bootstrap itself guards against silent overwrites).
- Leave everything uncommitted — the owner reviews and commits.
