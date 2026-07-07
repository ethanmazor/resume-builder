# AGENTS.md — Resume Builder

This repository is a **tailored-resume factory**. A coding agent (you) reads a
single source of truth about the owner's real experience and generates one-page,
ATS-friendly LaTeX resumes tailored to specific job descriptions.

**Read this file first, then follow the relevant skill below.**

## Skills

Six agent skills live in `skills/`:

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `bootstrap` | *"My data is at /path — bootstrap my source of truth"* | First-time setup: ingests an external data folder and populates `data/profile/`, `data/facts/`, `data/context/`, and `data/projects/`. Writes `.sync-config.yaml`. |
| `sync` | *"sync my data"* | Incrementally merges new content from the data folder into the source of truth. Skips anything already present. |
| `fetch-job` | *"fetch this job: https://..."* | Fetches one or more job-posting URLs, parses JD metadata/keywords, and writes `data/jobs/{company-role}.md`. |
| `start-tracker` | *"start tracker"* | Launches the local job-tracker web app on `http://127.0.0.1:5050`. |
| `tracker-cli` | *"add Acme SWE to tracker"*, *"mark Acme as Rejected"*, *"list my applications"* | Agent writes Python sqlite3 code directly to update the tracker DB. Kanban board auto-picks up changes via polling. |
| `build-resume` | Drop a JD in `data/jobs/`, ask agent to build | Generates a tailored one-page PDF resume |

**If `data/profile/profile.yaml` does not exist yet, run `bootstrap` before anything else.**

## Repository map

| Path | Purpose |
|------|---------|
| `data/profile/` | Static identity: name, contact, links, education. Never tailored. |
| `data/facts/` | **Structured factual guardrail.** Experiences, projects, research, skills, courses. The boundary of what is true. |
| `data/context/` | Free-form "brag docs" / write-ups. Richer material to draw wording from. |
| `data/projects/` | Raw code, schematics, and resources. The agent reads `data/context/` summaries, not these directly. |
| `template/` | Jake's Resume base + `STYLE_GUIDE.md`. You author `resume.tex` per this. |
| `data/jobs/` | Input job descriptions: `data/jobs/{company-role}.md` (raw JD text + optional `## Hints`). |
| `data/resumes/` | Output. One folder per job: `resume.pdf`, `resume.tex`, `tailoring-notes.md`. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |
| `scripts/start-tracker.sh` | Start the local job-tracker web app (creates venv and installs deps if needed). |

## The grounding contract (non-negotiable)

You may **reword, reorder, select, and synthesize new bullets** — but every
concrete claim must trace back to something the owner actually wrote in `data/facts/`
or `data/context/`.

- ✅ Allowed: rephrasing a canonical bullet; combining two real accomplishments;
  writing a new bullet whose facts come from a `data/context/` write-up; emphasizing
  the skills/keywords the JD asks for.
- ❌ Forbidden: inventing employers, job titles, dates, degrees, certifications,
  metrics/numbers, or technologies that are **not present** in `data/facts/` or
  `data/context/`. Do not exaggerate scope or seniority.

Every tailored bullet must cite its source in `tailoring-notes.md`. If you cannot
ground a claim, do not make it.

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
