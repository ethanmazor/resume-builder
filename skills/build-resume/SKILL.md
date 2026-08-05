---
name: build-resume
description: Refine the owner's single base resume, optionally using a job description for lightweight keyword alignment.
triggers:
  - "refine my resume"
  - "build my resume"
  - "build a resume for"
  - "tailor my resume for"
user-invocable: true
argument-hint: "[base | job-slug]"
---

# SKILL: build-resume

Maintain one home-base resume. Job descriptions may guide light, truthful
keyword alignment, but output always remains the base resume.
Read [`../../AGENTS.md`](../../AGENTS.md) first.

## Resume model

- `data/base-resume/`: the owner-selected source resume and a short record of
  its origin. It is the wording and factual home base.
- `resumes/base/resume.tex` and `resume.pdf`: the compiled base resume.
- `data/jobs/{job-slug}.md`: a job description input.

During setup, use an existing owner resume as the base when supplied. If no
resume is supplied, create the base resume from the approved factual sources.

## Base-resume mode

Use this mode when the owner asks to create, revise, or refine their resume
without naming a JD.

1. Read `data/base-resume/`, `data/profile/`, `data/facts/`, and relevant
   `data/context/` files.
2. Apply the owner's requested changes to `resumes/base/resume.tex`. Do not
   invent bullets or claims. When a requested skill/tool is already supported
   by the factual sources, it may be added to the skills section.
3. Keep `data/base-resume/` synchronized with the approved base source and
   record meaningful changes in `data/base-resume/README.md`.
4. Compile with `scripts/build.sh resumes/base/resume.tex`; the PDF must be one page.

## Job-description mode

Use this mode when the owner names `data/jobs/{job-slug}.md` or asks to build
for a job.

1. Read the base source, `resumes/base/resume.tex`, the JD, and factual sources.
2. Edit `resumes/base/resume.tex` directly; do not create job-specific output directories.
3. Make only minor, truth-preserving alignment changes:
   - reorder existing entries or bullets;
   - surface skills, tools, coursework, or certifications already supported by
     `data/facts/` or `data/context/`;
   - use a JD term as a faithful synonym where it does not change the claim;
   - make minimal line-fit adjustments.
4. Do not add a new bullet, metric, employer, technology, or accomplishment
   solely because it appears in the JD. If a required item is unsupported,
   omit it.
5. Compile with `scripts/build.sh resumes/base/resume.tex` and verify one page.

Do not commit. Report that the base resume was updated and list the minor
changes made.
