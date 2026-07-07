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
   applying the feedback. Read the existing `data/resumes/{slug}/tailoring-notes.md`
   for continuity.
3. **Auto-detect (default)** — for every `data/jobs/{slug}.md` that has **no**
   `data/resumes/{slug}/resume.pdf`, build it. The `{slug}` is the JD filename without
   `.md`. If everything is already built, say so and stop.

`{slug}` = the JD filename stem. `data/resumes/{slug}/` is its output folder.

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

---

## 3. Load the source of truth

Read:
- `data/profile/profile.yaml` — identity, contact, links, education (verbatim, never tailored).
- `data/facts/experience.yaml`, `data/facts/projects.yaml`, `data/facts/skills.yaml`,
  `data/facts/courses.yaml`, `data/facts/activities.yaml` — the factual guardrail + canonical
  bullet inventory. Research and internship entries both live in `experience.yaml`.
- `data/context/*.md` — free-form write-ups for richer wording.

**These are read-only inputs.** Do not modify them while generating a resume.

---

## 4. Select and synthesize content (apply the grounding contract)

Goal: the strongest possible one-page resume for *this* JD.

- **Select** the most relevant experiences, projects, skills, and bullets by
  scoring each against the JD keywords/needs.
- **Reorder** so the most relevant content leads (within each section and, where
  the style guide allows, across sections).
- **Reword / synthesize** bullets to mirror the JD's language and emphasize
  matching impact — using strong action verbs and quantified outcomes **only
  where a real number exists** in the source of truth.
- **Skills section**: surface the JD-relevant skills the owner actually has.

**Grounding contract (from AGENTS.md):** every concrete claim — employer, title,
date, degree, metric, technology — must trace to `data/facts/` or `data/context/`.
Synthesizing new wording is fine; inventing facts is forbidden. When in doubt,
leave it out.

Track, for each bullet you place, **where it came from** (a `data/facts/` id or a
`data/context/` file). You will record this in `tailoring-notes.md`.

**Fill the page.** A one-page resume with visible empty space at the bottom is a
worse outcome than one that uses the full page, even if that means including
material that's a weaker match for the JD. After you've placed the strongly
relevant content, if the page still has room:
- Add back bullets you'd otherwise have cut for relevance (e.g. a 4th bullet on
  a role, or a secondary project).
- Add other real experiences/projects/research entries from `data/facts/` that are
  less on-topic for this specific JD but still true and generally impressive
  (e.g. surface the research entry on an embedded/hardware resume even though
  the JD didn't ask for research — it's real signal and better than blank space).
- Expand the Technical Skills section with more of the owner's real skills.
- Only pad with **grounded, true** content — never invent filler to take up space.
See the style guide's "Filling the page" section for the priority order.

---

## 5. Author `resume.tex`

Author the LaTeX following [`../../template/STYLE_GUIDE.md`](../../template/STYLE_GUIDE.md)
(Jake's Resume style). Do **not** blindly fill a rigid template — author the
document so it can be trimmed structurally to fit one page. Write it to
`data/resumes/{slug}/resume.tex`.

Use `data/profile/profile.yaml` for the header (name, contact, links) and education.
- Always include `citizenship: "US Citizen"` in the header.
- Include `portfolio` link in the header for hardware/EE/embedded roles where
  a portfolio is relevant. Omit for pure software or non-hardware roles.

---

## 6. Compile and enforce ONE PAGE

Use the helper (compiles + reports page count):

```bash
scripts/build.sh data/resumes/{slug}/resume.tex
```

Or manually:

```bash
tectonic -o data/resumes/{slug} data/resumes/{slug}/resume.tex
pdfinfo data/resumes/{slug}/resume.pdf | grep -i '^Pages:'
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

## 7. Write the tailoring notes

Write `data/resumes/{slug}/tailoring-notes.md`:

```markdown
# Tailoring notes — {Company} / {Role}

**JD:** data/jobs/{slug}.md
**Generated:** {date}
**Emphasis:** short summary of the angle taken (what was surfaced, what was cut, why).

## Keyword coverage
- {jd keyword} → {how the resume addresses it, or "not claimed — owner lacks this"}

## Bullet provenance
| Section | Bullet (short) | Source |
|---------|----------------|--------|
| Experience — Acme | "Led migration to AWS…" | data/facts/experience.yaml#acme-b2 |
| Projects — Foo | "Built X handling Y…" | data/context/foo.md |

## Trims applied to fit one page
- {what was cut and why}
```

Every placed bullet must appear in the provenance table with a real source. If a
JD keyword could not be truthfully claimed, note it — do not fabricate coverage.

---

## 8. Finish

- Confirm `data/resumes/{slug}/` contains `resume.pdf` (1 page), `resume.tex`,
  `tailoring-notes.md`.
- **Do NOT commit.** Leave everything uncommitted.
- Report to the owner: which resume(s) you built, the emphasis taken, any trims,
  and any JD keywords you could not truthfully cover.

---

## Updating the source of truth (separate task)
When the owner explicitly asks to add/update experience, edit `data/facts/`,
`data/profile/`, or `data/context/` following the schemas in those files. That is the ONLY
time you modify inputs. Never edit inputs during resume generation.
