# Resume Builder

Generate **one-page, ATS-friendly LaTeX resumes tailored to specific job descriptions** — from a single source of truth about your real experience. The agent does the work; you review the PDF.

No CI, no API keys, no cloud. Runs entirely on your machine via a coding agent (Claude Code, GitHub Copilot, Cursor, etc.).

## How it works

You keep a **data folder** — any directory with your materials: an old resume PDF, project notes, code, markdown write-ups, whatever you have. The agent reads it and builds the structured source of truth inside this repo. After that, add job descriptions in `data/jobs/` and ask it to build.

```
~/my-resume-data/        ← your folder: old resume, notes, project docs, code
        |
        v
  resume-builder/        ← this repo (cloned once)
    agent ingests  ──>  data/profile/  data/facts/  data/context/  data/projects/
    agent builds   ──>  data/resumes/acme-swe/resume.pdf
```

## Quickstart

```bash
brew install tectonic poppler   # LaTeX compiler + PDF tools (one-time)
git clone https://github.com/ethanmazor/resume-builder
cd resume-builder
```

Open the repo in your coding agent and say:

> *"My data is at ~/my-resume-data — bootstrap my source of truth."*

The agent scans your folder, extracts what it can from every readable file, populates `data/profile/profile.yaml`, `data/facts/`, and `data/context/`, then asks clarifying questions for anything it can't determine automatically. Once done:

1. Add a job description file in `data/jobs/acme-swe.md` (paste raw JD; add an optional `## Hints` section to steer the agent), or ask the agent to fetch from a URL
2. Ask: *"Build resumes for any new jobs."*

The agent tailors content from your source of truth, compiles a PDF, and writes outputs to `data/resumes/acme-swe/`. **You review and commit. The agent never commits.**

## What to say to your agent

| Goal | Prompt |
|------|--------|
| First-time setup from a data folder | *"My data is at ~/my-data — bootstrap my source of truth."* |
| Start local tracker web app | *"start tracker"* |
| Add a job via agent (no server needed) | *"add Acme SWE role to tracker"* |
| Update status via agent | *"mark Acme as Rejected"* |
| List all applications | *"list my applications"* |
| Sync new material from your external folder | *"sync my data"* |
| Fetch JD from URL(s) | *"fetch this job: https://..."* or *"fetch these jobs: https://..., https://..."* |
| Build all pending resumes | *"Build resumes for any new jobs."* |
| Target one JD | *"Build the resume for `data/jobs/acme-swe.md`."* |
| Refine an existing resume | *"For acme-swe, lead with the AWS project and cut coursework."* |
| Check build toolchain | *"Verify my build toolchain is set up."* |

## Your data folder

The agent handles any structure — it doesn't need to match this repo's layout. Useful things to have in it:

- An existing resume (`.pdf` or `.tex`)
- Markdown or text notes about jobs, projects, or research
- Source code for projects you want to reference
- Research papers (`.pdf`) you authored or contributed to
- A `profile.yaml` or `facts/*.yaml` if you already have them structured

If your folder already uses this repo's `facts/` / `profile/` / `context/` schema, the agent copies it directly. If it's unstructured, the agent extracts what it can and asks about the rest.

## Repository layout

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Canonical agent instructions (auto-loaded by most agent CLIs). |
| `skills/bootstrap/SKILL.md` | One-time ingestion of an external data folder into this repo's source of truth. |
| `skills/start-tracker/SKILL.md` | Starts the local job-tracker web server. |
| `skills/tracker-cli/SKILL.md` | Agent writes Python sqlite3 directly to the tracker DB — no CLI script, no server needed. |
| `skills/sync/SKILL.md` | Incremental sync from the external data folder after bootstrap. |
| `skills/fetch-job/SKILL.md` | Fetch one or more job posting URLs into normalized `data/jobs/*.md` files. |
| `skills/build-resume/SKILL.md` | Step-by-step resume generation procedure. |
| `data/profile/profile.yaml` | Your identity, contact info, and education. Never tailored. |
| `data/facts/` | **Factual guardrail.** Experience, projects, skills, courses. The agent won't claim anything not here. |
| `data/context/` | Free-form brag docs / write-ups. Richer material to draw wording from. |
| `data/projects/` | Raw code, schematics, resources per project. |
| `data/jobs/` | Input job descriptions, one file per role. |
| `data/resumes/` | Output — one folder per job. |
| `template/STYLE_GUIDE.md` | Jake's Resume LaTeX style guide the agent authors against. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |
| `scripts/start-tracker.sh` | Start the local job-tracker web app on `http://127.0.0.1:5050`. |

## The grounding contract

The agent may reword, reorder, select, and synthesize bullets — but every concrete claim (employer, title, date, degree, metric, technology) must trace back to `data/facts/` or `data/context/`. Each bullet's source is logged in `tailoring-notes.md`, so review is a quick scan. See `AGENTS.md` for the full contract.

## Design notes

- **One page, always.** The agent compiles, checks the page count, and trims until it fits.
- **You are the reviewer.** Outputs are left uncommitted by design.
- **Nondeterministic.** The same JD may yield slightly different results across runs; use refine mode to steer.
