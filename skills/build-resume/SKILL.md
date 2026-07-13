---
name: build-resume
description: >
  Generate a one-page, ATS-friendly, tailored LaTeX resume from this repo's
  source of truth for a job description in data/jobs/. Compiles with Tectonic
  and enforces exactly one page.
triggers:
  - "build a resume for"
  - "build the resume for"
  - "generate a resume for"
  - "tailor a resume for"
user-invocable: true
argument-hint: "[job-slug or company/role — omit to auto-build all pending jobs]"
---

# SKILL: build-resume

Generate one-page, tailored LaTeX resumes from this repo's source of truth.
Read [`../../AGENTS.md`](../../AGENTS.md) first for repo context and the
**grounding contract**. This file is the exact procedure to follow.

**Path convention:** in this skill, every `data/...` and `resumes/...` path is
relative to `WORKSPACE_ROOT` (set in `.sync-config.yaml` as `workspace_path`),
not the repository root.

---

## 0. Preflight

Verify the toolchain is installed:

```bash
command -v tectonic >/dev/null || echo "MISSING: brew install tectonic"
command -v pdfinfo  >/dev/null || echo "MISSING: brew install poppler"
```

If either is missing, stop and tell the owner to run `brew install tectonic poppler`.

---

## 1. Decide what to build

Determine the target job(s) in this priority order:

1. **Explicit target** — the owner named a JD (e.g. "build the resume for
   `data/jobs/acme-swe.md`"). Build only that one.
2. **Refine mode** — the owner gave feedback on an existing resume
   (e.g. "for acme-swe, lead with the AWS project"). Regenerate that one resume,
   applying the feedback.
3. **Auto-detect (default)** — for every `data/jobs/{slug}.md` that has **no**
   `resumes/{slug}/resume.pdf`, build it. The `{slug}` is the JD filename without
   `.md`. If everything is already built, say so and stop.

`{slug}` = the JD filename stem. `resumes/{slug}/` is its output folder.

---

## 2. Parse the job description

Read `data/jobs/{slug}.md`. It is raw JD text and MAY contain an optional
`## Hints` section (owner steering — respect it strongly). Extract:

- Role title and seniority level.
- Must-have and nice-to-have skills / technologies / keywords.
- Domain and any signals about what the employer values.
- Any explicit hints from the owner.

Keep a short list of the **top keywords/skills** the resume should surface. These
drive selection and phrasing (and help with ATS keyword matching) — but only use
keywords the owner can truthfully claim per the source of truth.

### Skills gap resolution

After extracting required skills/tools/languages from the JD, cross-reference
against `data/facts/skills.yaml`. For any required item **not** present:

1. **Stop and ask the owner** — list the missing items and ask: "The JD requires
   [X, Y]. Do you have experience with these? Should I add any to your source of
   truth, or include them on this resume only?"
2. **Owner confirms one-time use** — include the skill in this resume's Technical
   Skills section only. Do **not** add it to `data/facts/skills.yaml` or
   `data/profile/`.
3. **Owner confirms it should persist** — add it to `data/facts/skills.yaml`, then include it in the resume.
4. **Owner says they don't have it** — omit entirely and call out the gap in your final response.

Never silently add skills to the source of truth, and never claim a skill the
owner has not confirmed.

---

## 3. Load the source of truth

Read:
- `data/profile/profile.yaml` — identity, contact, links, education (verbatim, never tailored).
- `data/facts/experience.yaml`, `data/facts/projects.yaml`, `data/facts/skills.yaml`,
  `data/facts/courses.yaml`, `data/facts/activities.yaml` — the factual guardrail + pre-approved
  bullet pool. Research and internship entries both live in `experience.yaml`.
- `data/context/*.md` — free-form write-ups providing background; read for understanding,
  not as a source of new bullets.

**These are read-only inputs.** Do not modify them while generating a resume.

---

## 4. Select bullets from the pool (do NOT synthesize)

Goal: the strongest possible one-page resume for *this* JD, built entirely from
pre-approved bullets in `data/facts/`.

### Selection rules

- **Select, don't write.** Every bullet on the resume must come from the `bullets:`
  pool in `data/facts/experience.yaml` or `data/facts/projects.yaml`. Do not
  compose new bullet text. If no pool bullet covers a JD need, note the gap in your final response and continue; do not fabricate coverage.
- **Score by relevance.** For each experience/project, rank its pool bullets by
  how well they match the JD's keywords, domain, and role type. Use the `angle`
  and `skills` fields on each bullet as signals. Pick the top 2–4 per entry.
- **Reorder entries** so the most relevant experience leads (reverse-chronological
  within each relevance tier). See STYLE_GUIDE.md for the reverse-chron rule.
- **Minor length adjustments are allowed.** A single pool bullet may be shortened
  (condensed to one line, a clause removed) if it would otherwise overflow the
  page — but the core claim and wording must remain faithful to the pool text.
- **Skills section**: surface the JD-relevant subset of `data/facts/skills.yaml`.
- **STAR format is required.** Every selected bullet must read with clear
  Situation/Task, Action, and Result. When lightly condensing pool bullets, preserve
  STAR structure and concrete outcomes.
- **Ask when STAR details are missing.** If a selected bullet lacks enough context,
  action detail, or result clarity, pause and ask the owner for the missing details
  before finalizing. Never infer or fabricate missing outcomes.
- **Abstract implementation detail.** Prefer bullets that emphasize capability and impact over
  low-level implementation specifics (e.g., register addresses, bus wiring internals, or
  signal routing minutiae) unless the owner explicitly asks for those details.

### Adding new bullets to the pool

If you identify a true, grounded accomplishment that belongs in the pool but
doesn't exist yet, **stop and propose it to the owner** rather than using it
directly. The owner approves it, you add it to the appropriate `bullets:` array
in `data/facts/`, and then it can be selected for this and future resumes.

### Fill the page

A one-page resume should use the whole page. If content runs short:
1. Add back pool bullets you cut for relevance (a 4th bullet on a role, etc.).
2. Surface an off-topic-but-real entry from `data/facts/` (e.g. the FPAA research
   on an embedded resume, or the SCOMP peripheral on a software resume).
3. Expand the Technical Skills section with more real skills.
4. Add coursework/activities/certifications if previously cut.

Only use bullets and entries that are already in `data/facts/` — never invent.

---

## 5. Author `resume.tex`

Author the LaTeX following [`../../template/STYLE_GUIDE.md`](../../template/STYLE_GUIDE.md)
(Jake's Resume style). Do **not** blindly fill a rigid template — author the
document so it can be trimmed structurally to fit one page. Write it to
`resumes/{slug}/resume.tex`.

Use `data/profile/profile.yaml` for the header (name, contact, links) and education.
- Always include `citizenship: "US Citizen"` in the header.
- Include `portfolio` link in the header for hardware/EE/embedded roles where
  a portfolio is relevant. Omit for pure software or non-hardware roles.

---

## 6. Compile and enforce ONE PAGE

Use the helper (compiles + reports page count):

```bash
scripts/build.sh resumes/{slug}/resume.tex
```

Or manually:

```bash
tectonic -o resumes/{slug} resumes/{slug}/resume.tex
pdfinfo resumes/{slug}/resume.pdf | grep -i '^Pages:'
```

If the PDF is **more than one page**, trim and recompile. Apply this
**trim priority** (least destructive first):

1. Tighten spacing/margins/font size **within the bounds allowed by the style guide**.
2. Cut the weakest, least-JD-relevant bullets first.
3. Drop the least-relevant projects/courses entirely.
4. Condense wording (shorter bullets, fewer filler words).

Never drop core identity or education. Repeat until `Pages: 1`. If it truly
cannot fit, tell the owner what you had to cut and ask how to proceed.

If the PDF is **one page with noticeable leftover white space** (e.g. the last
section ends well above the bottom margin, or there's an obvious gap), that is
also a failure state — go back to step 4/5 and **add more grounded content**
(see "Fill the page" above and the style guide's "Filling the page" priority
order), then recompile and recheck. Repeat until the page is fully used without
overflowing to a second page.

If a fixed compile error occurs, read the Tectonic log, fix the LaTeX, recompile.

---

## 7. Finish

- Confirm `resumes/{slug}/` contains `resume.pdf` (1 page) and `resume.tex`.
- **Do NOT commit.** Leave everything uncommitted.
- Report to the owner: which resume(s) you built, the emphasis taken, any trims,
  and any JD keywords you could not truthfully cover.

---

## Updating the source of truth (separate task)
When the owner explicitly asks to add/update experience, edit `data/facts/`,
`data/profile/`, or `data/context/` following the schemas in those files. That is the ONLY
time you modify inputs. Never edit inputs during resume generation.
