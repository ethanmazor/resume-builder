# AGENTS.md — Resume Builder

This repository is a **tailored-resume factory**. A coding agent (you) reads a
single source of truth about the owner's real experience and generates one-page,
ATS-friendly LaTeX resumes tailored to specific job descriptions.

**Read this file first, then follow the relevant skill below.**

## Skills

Seven agent skills live in `skills/`. Each is marked `user-invocable: true`, so
it's also available as a slash command (e.g. `/bootstrap`, `/build-resume`) in
agent CLIs that support skill-based slash commands, in addition to matching on
its natural-language triggers.

| Skill | Slash command | Trigger | What it does |
|-------|---------------|---------|-------------|
| `first-time-setup` | `/first-time-setup` | *"get me set up"*, *"how do I get started"* | Guided walkthrough for a brand-new clone: checks the toolchain, runs `bootstrap` if empty, explains the day-to-day workflow. |
| `bootstrap` | `/bootstrap` | *"My data is at /path — bootstrap my source of truth"* | First-time setup: ingests an external data folder and populates `data/profile/`, `data/facts/`, `data/context/`, and `data/projects/`. Writes `.sync-config.yaml`. |
| `sync` | `/sync` | *"sync my data"* | Incrementally merges new content from the data folder into the source of truth. Skips anything already present. |
| `fetch-job` | `/fetch-job` | *"fetch this job: https://..."* | Fetches one or more job-posting URLs, parses JD metadata/keywords, and writes `data/jobs/{company-role}.md`. |
| `start-tracker` | `/start-tracker` | *"start tracker"* | Launches the local job-tracker web app on `http://127.0.0.1:5050`. |
| `tracker-cli` | `/tracker-cli` | *"add Acme SWE to tracker"*, *"mark Acme as Rejected"*, *"list my applications"* | Agent writes Python sqlite3 code directly to update the tracker DB. Kanban board auto-picks up changes via polling. |
| `build-resume` | `/build-resume` | Drop a JD in `data/jobs/`, ask agent to build | Generates a tailored one-page PDF resume |

**If `data/profile/profile.yaml` does not exist yet, run `first-time-setup` (or `bootstrap` directly) before anything else.**

## Repository map

| Path | Purpose |
|------|---------|
| `data/profile/` | Static identity: name, contact, links, education. Never tailored. |
| `data/facts/` | **Structured factual guardrail.** Experiences, projects, research, skills, courses. The boundary of what is true. |
| `data/context/` | Free-form "brag docs" / write-ups. Richer material to draw wording from. |
| `data/projects/` | Raw code, schematics, and resources. The agent reads `data/context/` summaries, not these directly. |
| `template/` | Jake's Resume base + `STYLE_GUIDE.md`. You author `resume.tex` per this. |
| `data/jobs/` | Input job descriptions: `data/jobs/{company-role}.md` (raw JD text + optional `## Hints`). |
| `resumes/` | Output. One folder per job: `resume.pdf`, `resume.tex`, `tailoring-notes.md`. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |
| `scripts/start-tracker.sh` | Start the local job-tracker web app (creates venv and installs deps if needed). |

## The grounding contract (non-negotiable)

Resumes are built by **selecting** bullets from the pre-approved pool in
`data/facts/` — not by synthesizing new wording. Every bullet on a resume
must have a corresponding `id` in `data/facts/experience.yaml` or
`data/facts/projects.yaml`.

- ✅ Allowed: selecting pool bullets; reordering them; lightly condensing a
  bullet's length for line-fit; combining two pool bullets into one line if
  both IDs are cited in `tailoring-notes.md`.
- ✅ Allowed: proposing a new pool bullet to the owner (they approve, you add
  it to `data/facts/`, then it can be used).
- ❌ Forbidden: writing new bullet text not in the pool; inventing employers,
  job titles, dates, degrees, certifications, metrics/numbers, or technologies
  not present in `data/facts/` or `data/context/`. Do not exaggerate scope or
  seniority.

Every placed bullet must cite its pool ID in `tailoring-notes.md`. If you cannot
cover a JD need from the pool, note the gap — do not fabricate coverage.

## Hard rules

1. **One page, always.** The final PDF must be exactly one page.
2. **Never edit `data/facts/`, `data/profile/`, or `data/context/`** while generating a resume —
   those are inputs. (Only edit them when the owner explicitly asks you to update
   the source of truth, or during `bootstrap` / `sync`.)
3. **Leave outputs uncommitted.** Do not `git commit` or `git push`. The owner
   reviews the PDF and commits.
4. **No fabrication.** See the grounding contract above.

## Toolchain

- [Tectonic](https://tectonic-typesetting.github.io/) — LaTeX compilation.
- [Poppler](https://poppler.freedesktop.org/) `pdfinfo` — page-count verification.

Install: `brew install tectonic poppler`. See `README.md`.
