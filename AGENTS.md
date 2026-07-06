# AGENTS.md — Resume Builder

This repository is a **tailored-resume factory**. A coding agent (you) reads a
single source of truth about the owner's real experience and generates one-page,
ATS-friendly LaTeX resumes tailored to specific job descriptions.

**Read this file first, then follow the relevant skill below.**

## Skills

Three agent skills live in `skills/`:

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `bootstrap` | *"My data is at /path — bootstrap my source of truth"* | First-time setup: ingests an external data folder and populates `profile/`, `facts/`, `context/`, and `projects/` |
| `build-resume` | Drop a JD in `jobs/`, ask agent to build | Generates a tailored one-page PDF resume |
| `ingest-inbox` | *"Process my inbox"* | Adds new material from `inbox/` to an already-populated source of truth |

**If `profile/profile.yaml` does not exist yet, run `bootstrap` before anything else.**

## Repository map

| Path | Purpose |
|------|---------|
| `profile/` | Static identity: name, contact, links, education. Never tailored. |
| `facts/` | **Structured factual guardrail.** Experiences, projects, research, skills, courses. The boundary of what is true. |
| `context/` | Free-form "brag docs" / write-ups. Richer material to draw wording from. |
| `projects/` | Raw code, schematics, and resources. The agent reads `context/` summaries, not these directly. |
| `inbox/` | Drop zone for new material after initial bootstrap. One subfolder per project/experience. |
| `template/` | Jake's Resume base + `STYLE_GUIDE.md`. You author `resume.tex` per this. |
| `jobs/` | Input job descriptions: `jobs/{company-role}.md` (raw JD text + optional `## Hints`). |
| `resumes/` | Output. One folder per job: `resume.pdf`, `resume.tex`, `tailoring-notes.md`. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |

## The grounding contract (non-negotiable)

You may **reword, reorder, select, and synthesize new bullets** — but every
concrete claim must trace back to something the owner actually wrote in `facts/`
or `context/`.

- ✅ Allowed: rephrasing a canonical bullet; combining two real accomplishments;
  writing a new bullet whose facts come from a `context/` write-up; emphasizing
  the skills/keywords the JD asks for.
- ❌ Forbidden: inventing employers, job titles, dates, degrees, certifications,
  metrics/numbers, or technologies that are **not present** in `facts/` or
  `context/`. Do not exaggerate scope or seniority.

Every tailored bullet must cite its source in `tailoring-notes.md`. If you cannot
ground a claim, do not make it.

## Hard rules

1. **One page, always.** The final PDF must be exactly one page.
2. **Never edit `facts/`, `profile/`, or `context/`** while generating a resume —
   those are inputs. (Only edit them when the owner explicitly asks you to update
   the source of truth, or during `bootstrap` / `ingest-inbox`.)
3. **Leave outputs uncommitted.** Do not `git commit` or `git push`. The owner
   reviews the PDF and commits.
4. **No fabrication.** See the grounding contract above.

## Toolchain

- [Tectonic](https://tectonic-typesetting.github.io/) — LaTeX compilation.
- [Poppler](https://poppler.freedesktop.org/) `pdfinfo` — page-count verification.

Install: `brew install tectonic poppler`. See `README.md`.
