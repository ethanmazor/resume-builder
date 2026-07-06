# AGENTS.md — Tailored Resume Automation

This repository is a **tailored-resume factory**. It holds a single source of
truth about the owner's real experience and uses a coding agent (you) to generate
one-page, ATS-friendly LaTeX resumes tailored to specific job descriptions.

If you are an agent spawned in this repo, **read this file, then follow the
detailed procedure in [`skills/build-resume/SKILL.md`](skills/build-resume/SKILL.md).**

## What you do (in one sentence)
For each job description in `jobs/` that has no matching resume, read the source
of truth, synthesize tailored one-page content, compile it to PDF, and write the
outputs to `resumes/{company-role}/` — leaving everything uncommitted for the
owner to review.

## Skills
Two agent skills live in `skills/`:

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `build-resume` | Drop a JD in `jobs/`, ask agent to build | Generates a tailored one-page PDF resume |
| `ingest-inbox` | "process my inbox" | Scans `inbox/`, classifies files, updates `facts/` + `context/` + `projects/` |

## Repository map
| Path | Purpose |
|------|---------|
| `profile/` | Static identity: name, contact, links, education. Never tailored. |
| `facts/` | **Structured factual guardrail.** Experiences, projects, research, skills, courses, and a canonical bullet inventory. The boundary of what is true. |
| `context/` | Free-form "brag docs" / write-ups. Richer material to draw wording from. |
| `projects/` | Raw code, schematics, and resources. The agent reads `context/` summaries, not these directly. |
| `inbox/` | **Drop zone.** One subfolder per project/experience. Run `ingest-inbox` to classify, move to `projects/`, and update `facts/` + `context/`. Never drop loose files directly here. |
| `template/` | Jake's Resume base + `STYLE_GUIDE.md`. You author `resume.tex` per this. |
| `jobs/` | Input job descriptions: `jobs/{company-role}.md` (raw JD text + optional hints). |
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
   those are inputs. (You only edit them when the owner explicitly asks you to
   update the source of truth.)
3. **Leave outputs uncommitted.** Do not `git commit` or `git push`. The owner
   reviews the PDF and commits.
4. **No fabrication.** See the grounding contract above.

## Toolchain
- [Tectonic](https://tectonic-typesetting.github.io/) — LaTeX compilation.
- [Poppler](https://poppler.freedesktop.org/) `pdfinfo` — page-count verification.

Install: `brew install tectonic poppler`. See `README.md`.
