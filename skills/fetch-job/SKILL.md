---
name: fetch-job
description: >
  Fetch one or more job-posting URLs, extract the job description and core
  metadata, parse must-have and nice-to-have keywords, and write normalized
  files to data/jobs/ for downstream resume generation.
triggers:
  - "fetch this job:"
  - "fetch these jobs:"
  - "add job from"
  - "fetch job posting"
user-invocable: true
argument-hint: "<job-posting-url> [job-posting-url...]"
---

# Fetch Job Skill

## Purpose

The owner provides one or more job-posting URLs. This skill fetches each page,
extracts and cleans the JD content, derives a stable slug, and writes a
structured markdown file to `data/jobs/{slug}.md`.

This gives the owner a reviewable job file with:
- source URL and fetch date
- role metadata (company, role, seniority, location)
- parsed keyword sets (must-have and nice-to-have)
- full cleaned job description text

Use this skill before `build-resume` when the owner starts from links instead
of pasted JDs.

## Hard rules

- **Never fabricate.** Only write fields found in the fetched content. If a
  field cannot be determined, write `Unknown`.
- **Use built-in web fetch tooling.** Use the agent's built-in webpage fetch
  capability (for example `fetch_webpage` or equivalent in the current agent).
- **One output per URL.** Create one file per successfully fetched posting.
- **Leave outputs uncommitted.** Do not `git commit` or `git push`.

---

## Step 0 — Parse input URLs

Extract one or more absolute URLs from the owner request.

- Accept comma/newline/space-separated URLs.
- Deduplicate exact matches.
- If no valid URL is found, stop and ask the owner to provide at least one
  absolute URL.

---

## Step 1 — Fetch each posting

For each URL:

1. Fetch page content using built-in web fetch tooling.
2. If fetch fails, returns empty content, or is obviously blocked by anti-bot
   gating, mark the URL as failed and continue processing remaining URLs.

At the end, report failed URLs and ask the owner to paste JD text manually for
those entries.

---

## Step 2 — Extract posting metadata + text

From each successfully fetched page, extract:

- `company`
- `role`
- `seniority` (Intern, New Grad, Mid, Senior, Staff, etc.)
- `location` (or Remote/Hybrid if clearly stated)
- cleaned JD body text (responsibilities, requirements, qualifications)

Prefer content that appears under headings like:
- Responsibilities
- Requirements / Qualifications
- Preferred / Nice to have
- About the role

Remove obvious noise where possible:
- navigation/footer/legal boilerplate
- cookie banners
- unrelated recommended jobs blocks

If `company` or `role` is not clearly extractable, set to `Unknown`.

---

## Step 3 — Parse keyword sets

Produce two keyword lists:

- `Must-have`: hard requirements and core skills repeatedly emphasized
- `Nice-to-have`: preferred/bonus qualifications and secondary skills

Guidelines:
- Normalize case and deduplicate.
- Keep keywords concise (e.g. `C++`, `embedded Linux`, `RTOS`, `PCB bring-up`).
- Use only what appears in the posting.

---

## Step 4 — Derive slug and handle collisions

Create base slug: `{company}-{role}` in lowercase kebab-case.

Rules:
- Strip punctuation and collapse whitespace to `-`.
- If company or role is `Unknown`, use `unknown` for that component.
- Output path: `data/jobs/{slug}.md`.

Collision handling:
- If the target file exists, append `-2`, then `-3`, etc. until an unused
  filename is found.

---

## Step 5 — Write output file

Write each posting to `data/jobs/{slug}.md` using this format:

```markdown
# {Company} — {Role}

**Source:** {url}
**Fetched:** {YYYY-MM-DD}
**Seniority:** {seniority}
**Location:** {location}

## Parsed keywords
**Must-have:** kw1, kw2, kw3
**Nice-to-have:** kw1, kw2, kw3

## Job description
{cleaned JD text}
```

Do not include fabricated values. Use `Unknown` when needed.

---

## Step 6 — Report

Print a concise summary:

```
Fetched jobs complete.

Created:
  data/jobs/{slug1}.md
  data/jobs/{slug2}.md

Failed URLs:
  - https://...

Next step:
  Ask: "Build resumes for any new jobs."
```

If all URLs fail, do not create files; ask the owner to paste JD text manually.
