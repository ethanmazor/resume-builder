# Tailored Resume Automation

A repository that generates **one-page, ATS-friendly LaTeX resumes tailored to
specific job descriptions** — from a single source of truth about your real
experience. Generation is driven **locally by a coding agent** (Claude Code,
GitHub Copilot CLI, Cursor, etc.); there is no CI, no API keys, and no cloud.

## How it works

```
 jobs/acme-swe.md            source of truth                 resumes/acme-swe/
 (raw job description)  ──▶   profile/ facts/ context/  ──▶   resume.pdf
        │                          │                          resume.tex
        │                          │                          tailoring-notes.md
        └──────── coding agent (AGENTS.md + skills/build-resume/SKILL.md) ───────┘
```

1. Drop a job description in `jobs/{company-role}.md` (raw text; optional hints).
2. Spawn your coding agent in this repo. It auto-loads `AGENTS.md` and follows
   `skills/build-resume/SKILL.md`.
3. It auto-detects job descriptions with no matching resume, synthesizes tailored
   one-page content grounded in your source of truth, compiles a PDF, and writes
   the outputs to `resumes/{company-role}/`.
4. **You review the PDF and commit.** The agent never commits.

## Repository layout

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Canonical agent instructions (auto-loaded by most agent CLIs). |
| `CLAUDE.md` | Portability shim pointing to `AGENTS.md`. |
| `skills/build-resume/SKILL.md` | The step-by-step generation procedure. |
| `profile/profile.yaml` | Static identity: name, contact, links, education. |
| `facts/` | Structured factual guardrail: experience, projects, skills, courses. |
| `context/` | Free-form write-ups / brag docs for richer wording. |
| `projects/` | Raw code, schematics, resources per project. Agent reads `context/` summaries, not these directly. |
| `template/STYLE_GUIDE.md` | Jake's Resume LaTeX style guide the agent authors against. |
| `jobs/` | Input job descriptions. |
| `resumes/` | Output, one folder per job. |
| `scripts/build.sh` | Compile with Tectonic + verify one page with `pdfinfo`. |

## Setup

Install the LaTeX toolchain (one time):

```bash
brew install tectonic poppler
```

- **Tectonic** compiles LaTeX to PDF (self-contained; fetches packages on demand).
- **Poppler** provides `pdfinfo`, used to verify the resume is exactly one page.

Then fill in your source of truth:

1. Edit `profile/profile.yaml` with your identity and education.
2. Populate `facts/*.yaml` with your real experience, projects, skills, courses.
   These are the **factual boundary** — the agent won't claim anything not here.
3. Add free-form write-ups to `context/` for richer material (optional but
   recommended).

> Tip: you can ask your agent to populate `facts/` and `context/` from an existing
> resume or notes — just point it at the source and ask it to update the source of
> truth (it edits inputs only when you explicitly ask).

## Usage

**Generate resumes for all new job descriptions:**
Spawn your agent in the repo and ask, e.g. *"Build resumes for any new jobs."*

**Target one job:** *"Build the resume for `jobs/acme-swe.md`."*

**Refine an existing one:** *"For acme-swe, lead with the AWS project and cut the
coursework."* The agent regenerates that resume with your feedback.

**Manual compile** (to check LaTeX yourself):

```bash
scripts/build.sh resumes/acme-swe/resume.tex
```

## The grounding contract

Because the agent can synthesize new bullet wording, the guardrail is explicit:
it may reword, reorder, select, and combine — but every concrete claim (employer,
title, date, degree, metric, technology) must trace back to `facts/` or `context/`.
Each generated bullet's source is recorded in `tailoring-notes.md`, so review is a
quick scan. See `AGENTS.md` for the full contract.

## Design notes

- **One page, always.** The agent compiles, checks the page count, and trims per
  the style guide until it fits.
- **You are the reviewer.** Outputs are left uncommitted by design.
- **Nondeterministic.** The same job description may yield slightly different
  resumes across runs; review each PDF and use refine mode to steer.
