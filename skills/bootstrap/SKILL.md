---
name: bootstrap
description: >
  One-time ingestion of an external data folder into this repo's source of
  truth. Reads any folder the owner points to — structured or unstructured —
  and populates data/profile/, data/facts/, data/context/, and data/projects/ from its contents.
triggers:
  - "bootstrap my source of truth"
  - "my data is at"
  - "import from"
  - "set up my source of truth"
  - "populate from"
user-invocable: true
argument-hint: "<path-to-your-data-folder>"
---

# Bootstrap Skill

## Purpose

The owner has a folder somewhere on their machine containing their personal
materials — an old resume, project notes, source code, research papers, or
an already-structured `data/facts/` / `data/profile/` directory tree. This skill reads
that folder end-to-end and writes the contents into this repo's
`data/profile/profile.yaml`, `data/facts/*.yaml`, `data/context/*.md`, and `data/projects/`.

Run this skill **once** on first setup, or when rebuilding from a new data
source. For incremental updates after setup, use `sync`.

## Hard rules

- **Never fabricate.** Write only what you can read in the source files or
  confirm through clarifying questions.
- **Ask before guessing.** If key identity information (name, email, education)
  is absent from the source files, ask the owner — do not invent it.
- **Leave outputs uncommitted.** Do not `git commit` or `git push`.
- **Do not overwrite if populated.** If `data/profile/profile.yaml` or any
  `data/facts/*.yaml` already has content, warn the owner before overwriting and
  ask them to confirm.

---

## Step 0 — Identify and validate the source folder

The owner should have provided a path, e.g.:
> *"My data is at ~/my-resume-data — bootstrap my source of truth."*

Resolve the path to an absolute path (expand `~`). Verify it exists and is a
directory. If not, stop and report the error.

---

## Step 1 — Detect source structure

Check whether the source folder uses this repo's schema already:

- **Structured source**: the folder contains any of `data/profile/profile.yaml`,
  `data/facts/experience.yaml`, `data/facts/projects.yaml`, `data/facts/skills.yaml`.
- **Unstructured source**: none of the above exist — it's a flat or ad-hoc
  collection of files.

Both modes end at the same outputs; the path differs.

---

## Step 2 — Enumerate all readable files

Recursively list all files under the source folder. For each, extract as much
readable text as possible:

| File type | How to extract |
|-----------|---------------|
| `.pdf` | `pdftotext <file> -` (requires Poppler) |
| `.tex`, `.bib` | Read directly |
| `.md`, `.txt`, `.rst` | Read directly |
| `.yaml`, `.json` | Read directly |
| `.c`, `.cpp`, `.h`, `.py`, `.m`, `.v`, `.sv`, `.vhd`, `.s`, `.asm` | Read directly |
| `.png`, `.jpg`, `.svg`, binary | Record filename only; no text extraction |

If `pdftotext` is unavailable, note which PDFs were skipped and continue.

---

## Step 3 — Structured source path

If the source is **structured** (Step 1 detected schema files):

1. Read each schema file from the source folder.
2. Validate that it matches the expected schema (see schemas below).
3. For files that are valid, copy them verbatim to the corresponding local path
   (e.g., `source/profile/profile.yaml` → `data/profile/profile.yaml`).
4. For files that have schema mismatches or missing required fields, note the
   gaps and continue — you will fill them in Step 6.
5. Copy any `data/context/*.md` files to local `data/context/`.
6. Copy any `data/projects/` subdirectories to local `data/projects/`.
7. Skip to Step 6.

---

## Step 4 — Unstructured source path: classify files

For each file in the source, assign one of these categories:

### A — Resume document
**Signals:** A `.pdf` or `.tex` whose extracted text contains a name at the
top, contact info (email, phone, LinkedIn), work experience with dates, and
an education section. Often has section headers like "Experience", "Education",
"Projects", "Skills".

- Use this as the primary source for `data/profile/`, `data/facts/experience.yaml`,
  `data/facts/projects.yaml`, and `data/facts/skills.yaml`.

### B — Research paper
**Signals:** Abstract, introduction/conclusion structure, bibliography,
author affiliations, or academic venue (conference, journal, arXiv).

- Destination: `data/projects/{slug}/papers/` where `{slug}` is inferred from
  the filename or paper title.
- Also extract publication metadata for `data/facts/research.yaml` (if applicable).

### C — Source code
**Signals:** Source code extension (`.c`, `.cpp`, `.h`, `.py`, `.m`, `.v`,
`.sv`, `.vhd`, `.s`, `.asm`) or build files (`Makefile`, `CMakeLists.txt`).

- Group by the immediate parent folder name as the project slug.
- Destination: `data/projects/{slug}/`.

### D — Project notes / write-up
**Signals:** `.md`, `.txt`, or `.rst` with prose describing a project,
internship, research role, or experience. Usually contains a title or
heading indicating what it's about.

- Destination: `data/context/{slug}.md` where `{slug}` is inferred from the
  filename or heading.

### E — Supporting resource
Everything else: datasheets, images, datasets, configuration files.

- Destination: `data/projects/{slug}/` under the nearest identifiable project
  grouping (parent folder name or filename prefix).

---

## Step 5 — Extract content from unstructured sources

### 5a — From the resume document (Category A)

Parse the resume text to extract:

**Identity** (for `data/profile/profile.yaml`):
- Full name
- Email, phone
- LinkedIn URL, portfolio URL, GitHub URL
- Citizenship / work authorization (if mentioned)

**Education** (for `data/profile/profile.yaml`):
- Institution, degree, location, start/end dates, GPA (if present)

**Work experience** (for `data/facts/experience.yaml`):
- Company, title, location, start/end dates
- Bullet points → canonical bullet inventory

**Projects** (for `data/facts/projects.yaml`):
- Project name, tech stack, description bullets

**Skills** (for `data/facts/skills.yaml`):
- Group by category if the resume groups them; otherwise leave flat

**Research** (for `data/facts/research.yaml`, if present):
- Institution, advisor, dates, publication titles

### 5b — From project notes (Category D)

Each write-up becomes a `data/context/{slug}.md` file. Preserve the prose as-is;
do not summarise or condense — richer context produces better resume bullets.

If the write-up clearly corresponds to an existing `data/facts/` entry (same
employer or project name), note the connection in a YAML comment in that
entry.

---

## Step 6 — Write outputs

Write the following files. Never truncate existing content; merge if a file
already has data.

### `data/profile/profile.yaml`

```yaml
# data/profile/profile.yaml
# Static identity. Used verbatim in every resume header + education section.
# This is NEVER tailored to a job.

name: ""

contact:
  email: ""
  phone: ""

links:
  linkedin: ""
  github: ""        # optional
  portfolio: ""     # optional

citizenship: ""     # e.g. "US Citizen" — omit if not applicable

education:
  - school: ""
    degree: ""
    location: ""
    start: ""       # YYYY-MM
    end: ""         # YYYY-MM or "Expected Month YYYY"
    gpa: ""         # omit if not including
```

### `data/facts/experience.yaml`

```yaml
# data/facts/experience.yaml
# All work experience: full-time, internship, and research roles.
experiences:
  - id: ""                    # kebab-case stable identifier
    company: ""
    title: ""
    location: ""
    start: ""                 # YYYY-MM
    end: ""                   # YYYY-MM or "Present"
    tech: []                  # technologies used
    bullets:
      - id: ""                # {experience-id}-b{n}
        text: ""
        skills: []
```

### `data/facts/projects.yaml`

```yaml
# data/facts/projects.yaml
projects:
  - id: ""
    name: ""
    tech: []
    start: ""
    end: ""
    bullets:
      - id: ""
        text: ""
        skills: []
```

### `data/facts/skills.yaml`

```yaml
# data/facts/skills.yaml
skills:
  languages: []
  frameworks: []
  tools_platforms: []
  # add/rename groups to match the owner's background
```

### `data/facts/research.yaml` (only if research content found)

```yaml
# data/facts/research.yaml
research:
  - id: ""
    institution: ""
    lab: ""
    advisor: ""
    start: ""
    end: ""
    bullets:
      - id: ""
        text: ""
    publications:
      - title: ""
        venue: ""
        path: ""          # relative path inside data/projects/
```

### `data/context/{slug}.md`

Write each project/experience write-up as a standalone markdown file. Use the
project or experience name as the slug (`kebab-case`).

---

## Step 7 — Copy project files

For each source code file (Category C) and resource file (Category E), copy
to `data/projects/{slug}/` using the same relative path within the project grouping.
For research papers (Category B), copy to `data/projects/{slug}/papers/`.

Do not modify or summarise the files — copy verbatim.

---

## Step 8 — Identify gaps and ask clarifying questions

After writing all outputs, review what could not be determined from the source
files. Ask the owner to fill in any gaps in a single message, listing each
unknown field clearly:

```
Bootstrap found the following gaps — please provide these details:

Identity:
  - Full name: ___
  - Email: ___
  ...

Experience: {company}
  - Exact start date: ___
  ...
```

---

## Step 9 — Write .sync-config.yaml

Write the following file to the repo root (it is gitignored — it stores only
the local machine path and is never committed):

```yaml
# .sync-config.yaml — machine-local, gitignored
# Written by bootstrap. Read by the sync skill to locate the source data folder.
source_path: "/absolute/resolved/path/to/source-folder"
```

Replace the value with the absolute path resolved in Step 0.

---

## Step 10 — Report

Write a brief summary to the terminal:

```
Bootstrap complete.

Populated:
  data/profile/profile.yaml          ✓
  data/facts/experience.yaml         ✓  (N entries)
  data/facts/projects.yaml           ✓  (N entries)
  data/facts/skills.yaml             ✓
  data/context/                      ✓  (N files)
  data/projects/                     ✓  (N directories)

Gaps (see data/facts/ or data/context/ for TODOs):
  - Missing phone number
  - ...

Next steps:
  1. Review the populated files and fill in any gaps.
  2. Drop a job description in data/jobs/ and ask: "Build a resume for [role]."
  3. When you add new material to your data folder, ask: "sync my data."
```
