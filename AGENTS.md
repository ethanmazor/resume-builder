# AGENTS.md — Resume Builder

This repository maintains one **base resume** as the owner's home base and
creates one-page, job-specific derived resumes when the owner supplies job
descriptions. The base resume is the primary wording and factual reference;
derived resumes may make only minor, grounded keyword-alignment changes.

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
| `bootstrap` | `/bootstrap` | *"My data is at /path — bootstrap my source of truth"* | Ingests the owner data, inventories existing resumes, and establishes or prepares a base resume. |
| `sync` | `/sync` | *"sync my data"* | Incrementally merges new content from the data folder into the source of truth. Skips anything already present. |
| `fetch-job` | `/fetch-job` | *"fetch this job: https://..."* | Fetches one or more job-posting URLs, parses JD metadata/keywords, and writes `${WORKSPACE_ROOT}/data/jobs/{company-role}.md`. |
| `start-tracker` | `/start-tracker` | *"start tracker"* | Launches the local job-tracker web app on `http://127.0.0.1:5050`. |
| `tracker-cli` | `/tracker-cli` | *"add Acme SWE to tracker"*, *"mark Acme as Rejected"*, *"list my applications"* | Agent writes Python sqlite3 code directly to update the tracker DB. Kanban board auto-picks up changes via polling. |
| `build-resume` | `/build-resume` | *"refine my base resume"*, *"build for Acme"* | Refines the base resume or derives a lightly tailored JD-specific PDF |

**If `${WORKSPACE_ROOT}/data/profile/profile.yaml` does not exist yet, run `first-time-setup` (or `bootstrap` directly) before anything else.**

## Repository map

| Path | Purpose |
|------|---------|
| `${WORKSPACE_ROOT}/data/profile/` | Static identity: name, contact, links, education. Never tailored. |
| `${WORKSPACE_ROOT}/data/facts/` | **Structured factual guardrail and bullet pool.** The boundary of what is true. |
| `${WORKSPACE_ROOT}/data/context/` | Free-form "brag docs" / write-ups. Richer material to draw wording from. |
| `${WORKSPACE_ROOT}/data/projects/` | Raw code, schematics, and resources. The agent reads `${WORKSPACE_ROOT}/data/context/` summaries, not these directly. |
| `template/` | Jake's Resume base + `STYLE_GUIDE.md`. You author `resume.tex` per this. |
| `${WORKSPACE_ROOT}/data/base-resume/` | The owner's selected or newly created home-base resume source and notes. |
| `${WORKSPACE_ROOT}/data/jobs/` | Input job descriptions, one file per role. |
| `${WORKSPACE_ROOT}/resumes/base/` | Compiled base resume. |
| `${WORKSPACE_ROOT}/resumes/{job-slug}/` | Derived PDF, TeX, and tailoring notes for one job description. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |
| `scripts/start-tracker.sh` | Start the local job-tracker web app (creates venv and installs deps if needed). |

## The grounding contract (non-negotiable)

The base and derived resumes are built from the pre-approved pool in
`${WORKSPACE_ROOT}/data/facts/` — not by synthesizing new wording. Every bullet
on a resume must have a corresponding `id` in
`${WORKSPACE_ROOT}/data/facts/experience.yaml` or
`${WORKSPACE_ROOT}/data/facts/projects.yaml`.

- ✅ Allowed: selecting pool bullets; reordering them; lightly condensing a
  bullet for line fit.
- ✅ Allowed: proposing a new pool bullet to the owner (they approve, you add
  it to `${WORKSPACE_ROOT}/data/facts/`, then it can be used).
- ❌ Forbidden: writing new bullet text not in the pool; inventing employers,
  job titles, dates, degrees, certifications, metrics/numbers, or technologies
  not present in `${WORKSPACE_ROOT}/data/facts/` or
  `${WORKSPACE_ROOT}/data/context/`. Do not exaggerate scope or seniority.

Every placed bullet must map to a real pool ID in `${WORKSPACE_ROOT}/data/facts/`.
Derived resumes must preserve the base resume's structure and claims. A JD may
prompt minor changes such as reordering existing content, surfacing a supported
skill/tool, or making faithful keyword substitutions. The JD alone never proves
experience and never authorizes a new bullet or claim.

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
