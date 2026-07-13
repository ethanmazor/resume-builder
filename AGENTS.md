# AGENTS.md — Resume Builder

This repository is a **tailored-resume factory**. A coding agent (you) reads a
single source of truth about the owner's real experience and generates one-page,
ATS-friendly LaTeX resumes tailored to specific job descriptions.

**Read this file first, then follow the relevant skill below.**

## Personal-data boundary

All personal data lives outside this repository in a machine-local
`WORKSPACE_ROOT` directory (configured in `.sync-config.yaml` via
`workspace_path`). The repo stores only skills, scripts, templates, and app
logic.

When these instructions reference `data/...` or `resumes/...`, interpret them
as:

- `${WORKSPACE_ROOT}/data/...`
- `${WORKSPACE_ROOT}/resumes/...`

## Skills

Seven agent skills live in `skills/`. Each is marked `user-invocable: true`, so
it's also available as a slash command (e.g. `/bootstrap`, `/build-resume`) in
agent CLIs that support skill-based slash commands, in addition to matching on
its natural-language triggers.

| Skill | Slash command | Trigger | What it does |
|-------|---------------|---------|-------------|
| `first-time-setup` | `/first-time-setup` | *"get me set up"*, *"how do I get started"* | Guided walkthrough for a brand-new clone: checks the toolchain, runs `bootstrap` if empty, explains the day-to-day workflow. |
| `bootstrap` | `/bootstrap` | *"My data is at /path — bootstrap my source of truth"* | First-time setup: ingests an external data folder and populates `${WORKSPACE_ROOT}/data/profile/`, `${WORKSPACE_ROOT}/data/facts/`, `${WORKSPACE_ROOT}/data/context/`, and `${WORKSPACE_ROOT}/data/projects/`. Writes `.sync-config.yaml`. |
| `sync` | `/sync` | *"sync my data"* | Incrementally merges new content from the data folder into the source of truth. Skips anything already present. |
| `fetch-job` | `/fetch-job` | *"fetch this job: https://..."* | Fetches one or more job-posting URLs, parses JD metadata/keywords, and writes `${WORKSPACE_ROOT}/data/jobs/{company-role}.md`. |
| `start-tracker` | `/start-tracker` | *"start tracker"* | Launches the local job-tracker web app on `http://127.0.0.1:5050`. |
| `tracker-cli` | `/tracker-cli` | *"add Acme SWE to tracker"*, *"mark Acme as Rejected"*, *"list my applications"* | Agent writes Python sqlite3 code directly to update the tracker DB. Kanban board auto-picks up changes via polling. |
| `build-resume` | `/build-resume` | Drop a JD in `${WORKSPACE_ROOT}/data/jobs/`, ask agent to build | Generates a tailored one-page PDF resume |

**If `${WORKSPACE_ROOT}/data/profile/profile.yaml` does not exist yet, run `first-time-setup` (or `bootstrap` directly) before anything else.**

## Repository map

| Path | Purpose |
|------|---------|
| `${WORKSPACE_ROOT}/data/profile/` | Static identity: name, contact, links, education. Never tailored. |
| `${WORKSPACE_ROOT}/data/facts/` | **Structured factual guardrail.** Experiences, projects, research, skills, courses. The boundary of what is true. |
| `${WORKSPACE_ROOT}/data/context/` | Free-form "brag docs" / write-ups. Richer material to draw wording from. |
| `${WORKSPACE_ROOT}/data/projects/` | Raw code, schematics, and resources. The agent reads `${WORKSPACE_ROOT}/data/context/` summaries, not these directly. |
| `template/` | Jake's Resume base + `STYLE_GUIDE.md`. You author `resume.tex` per this. |
| `${WORKSPACE_ROOT}/data/jobs/` | Input job descriptions: `${WORKSPACE_ROOT}/data/jobs/{company-role}.md` (raw JD text + optional `## Hints`). |
| `${WORKSPACE_ROOT}/resumes/` | Output. One folder per job: `resume.pdf`, `resume.tex`. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |
| `scripts/start-tracker.sh` | Start the local job-tracker web app (creates venv and installs deps if needed). |

## The grounding contract (non-negotiable)

Resumes are built by **selecting** bullets from the pre-approved pool in
`${WORKSPACE_ROOT}/data/facts/` — not by synthesizing new wording. Every bullet
on a resume must have a corresponding `id` in
`${WORKSPACE_ROOT}/data/facts/experience.yaml` or
`${WORKSPACE_ROOT}/data/facts/projects.yaml`.

- ✅ Allowed: selecting pool bullets; reordering them; lightly condensing a
  bullet's length for line-fit; combining two pool bullets into one line if
  both IDs are cited in `tailoring-notes.md`.
- ✅ Allowed: proposing a new pool bullet to the owner (they approve, you add
  it to `${WORKSPACE_ROOT}/data/facts/`, then it can be used).
- ❌ Forbidden: writing new bullet text not in the pool; inventing employers,
  job titles, dates, degrees, certifications, metrics/numbers, or technologies
  not present in `${WORKSPACE_ROOT}/data/facts/` or
  `${WORKSPACE_ROOT}/data/context/`. Do not exaggerate scope or seniority.

Every placed bullet must map to a real pool ID in `${WORKSPACE_ROOT}/data/facts/`.
If you cannot cover a JD need from the pool, note the gap — do not fabricate coverage.

## Bullet writing standard (STAR)

Every resume bullet must follow the STAR structure:
- **Situation/Task**: concise context or problem
- **Action**: what the owner did
- **Result**: measurable impact or concrete outcome

Bullets must remain grounded in approved pool content, but when selecting or lightly
condensing bullets, prefer versions that preserve clear STAR flow.

If STAR-complete wording is unclear or key context/result details are missing, stop and
ask the owner for clarification before finalizing the resume. Do not guess or invent
missing details.

## Hard rules

1. **One page, always.** The final PDF must be exactly one page.
2. **Never edit `${WORKSPACE_ROOT}/data/facts/`, `${WORKSPACE_ROOT}/data/profile/`, or `${WORKSPACE_ROOT}/data/context/`** while generating a resume —
   those are inputs. (Only edit them when the owner explicitly asks you to update
   the source of truth, or during `bootstrap` / `sync`.)
3. **Leave outputs uncommitted.** Do not `git commit` or `git push`. The owner
   reviews the PDF and commits.
4. **No fabrication.** See the grounding contract above.

## Toolchain

- [Tectonic](https://tectonic-typesetting.github.io/) — LaTeX compilation.
- [Poppler](https://poppler.freedesktop.org/) `pdfinfo` — page-count verification.

Install: `brew install tectonic poppler`. See `README.md`.
