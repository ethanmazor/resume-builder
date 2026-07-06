---
name: ingest-inbox
description: >
  Scan inbox/ subfolders (one per project or experience), classify every new
  file within each subfolder, move contents to projects/, and update
  facts/experience.yaml and context/.
triggers:
  - "process my inbox"
  - "ingest inbox"
  - "organize inbox"
  - "process inbox"
---

# Ingest Inbox Skill

## Purpose

The user drops one subfolder per project or experience into `inbox/`. Each
subfolder name is the slug for that project. This skill reads, classifies, and
organises their contents — updating the source-of-truth files so the
`build-resume` skill can use the new material.

## Hard rules

- **Never fabricate.** Only create facts entries from content you can read in
  the actual files or from `NEEDS_INFO.md` answers the user has provided.
- **Never delete originals without first confirming the copy succeeded.** Files
  go to their permanent home before the inbox copy is removed.
- **Never edit `facts/`, `profile/`, or `context/` beyond what the new material
  warrants.** Do not touch existing entries unless the user explicitly asked.
- **Leave outputs uncommitted.** Do not `git commit` or `git push`.

---

## Step 0 — Preflight

Verify that `pdftotext` is available by running `pdftotext --version` (or
equivalent). It ships with the Poppler toolkit, installable via any system
package manager (`brew install poppler`, `apt install poppler-utils`, etc.).

If `pdftotext` is missing, stop and ask the user to install Poppler, then
re-run the skill.

---

## Step 1 — Identify new subfolders to process

List all **subdirectories** directly inside `inbox/` (non-recursive). Exclude:
`NEEDS_INFO.md`, `README.md`, `.gitkeep`, `processing-report.md`.

### Warn on loose files

If any **loose files** exist directly in `inbox/` (not inside a subfolder),
do not process them. Tell the user:

> The following files are loose in inbox/ and won't be processed. Please move
> each into a named subfolder before re-running:
> - {filename}

Continue processing any valid subfolders.

### Skip already-processed subfolders (idempotency)

If `inbox/processing-report.md` exists, read it and collect all subfolder
names listed in the **"Folders processed"** table (first column). Remove any
subfolder from the working list whose name appears there.

If the working list is empty after this filter, report "no new subfolders
since last run" and stop.

---

## Step 2 — Check for NEEDS_INFO.md

If `inbox/NEEDS_INFO.md` exists, read it in full. The user has answered
questions from a previous partial run — treat those answers as authoritative
throughout this run.

---

## Step 3 — For each subfolder: list and extract file contents

For each subfolder in the working list, enumerate all files within it
(recursively). For each file, extract as much readable text as possible:

| File type | How to extract |
|-----------|---------------|
| `.pdf` | Run `pdftotext <file> -` to emit plain text to stdout |
| `.tex`, `.bib` | Read directly |
| `.c`, `.cpp`, `.h`, `.py`, `.m`, `.v`, `.sv`, `.vhd`, `.vhdl`, `.s`, `.asm` | Read directly |
| `.md`, `.txt`, `.rst`, `.yaml`, `.json` | Read directly |
| `.png`, `.jpg`, `.svg`, `.dxf`, binary formats | Record filename only; no text extraction |

The subfolder name is the **slug** — no need to infer project association from
file content.

---

## Step 4 — Classify each file by type

Since the slug is the subfolder name, classification only needs to assign a
**file type** (which determines the destination subdirectory within
`projects/{slug}/`):

### A — Research paper (primary source)
**Signals:** Contains an abstract, introduction/conclusion structure,
bibliography/references, author affiliations, or academic venue name
(conference, journal, arXiv). Usually `.pdf` or `.tex`.

- Destination: `projects/{slug}/papers/`

### B — Source code
**Signals:** Source code extension (`.c`, `.cpp`, `.h`, `.py`, `.m`, `.v`,
`.sv`, `.vhd`, `.vhdl`, `.s`, `.asm`) or build files (Makefile,
`CMakeLists.txt`).

- Destination: `projects/{slug}/`

### C — Supporting resource
Everything else: datasheets, schematics, images, datasets, configuration
files, notes, READMEs.

- Destination: `projects/{slug}/resources/`

There is no "Unknown" category — project association is always clear from the
subfolder.

---

## Step 5 — Extract metadata from research papers (Category A)

For each Category A file, extract the following. Leave as `# TODO` if not
determinable from the file:

| Field | Where to look |
|-------|--------------|
| `paper_title` | Paper title / `\title{}` in `.tex` |
| `venue` | Journal or conference name and year |
| `my_role` | Author position, acknowledgements, e.g. "Undergraduate Researcher" |
| `advisor` | PI/supervisor from affiliations or acknowledgements |
| `institution` | Affiliation line |
| `start_date` | Submission date, acknowledgement date, or inferable semester |
| `end_date` | Same, or "Present" |
| `key_contributions` | Concrete actions from methods/results sections |
| `technologies` | Languages, frameworks, hardware, datasets named in the paper |

Use only content from the files. Never infer fields not present.

---

## Step 6 — Check for required experience-entry fields

Required fields before writing to `facts/experience.yaml`:

| Field | Required |
|-------|---------|
| `company` (= institution name for research) | Yes |
| `title` (= your role, e.g. "Undergraduate Research Assistant") | Yes |
| `location` | Yes |
| `start` (ISO year-month) | Yes |
| `end` (ISO year-month or "Present") | Yes |
| `advisor` | Strongly preferred for research entries |

If any required field is still `# TODO` **and** `NEEDS_INFO.md` does not
already answer it, create or append to `inbox/NEEDS_INFO.md` with one specific
question per unknown field. Then **stop** and tell the user:

> I've extracted what I can from `{slug}/`. Please fill in `inbox/NEEDS_INFO.md`
> with the missing details and re-run "process my inbox".

Do not write a partial facts entry — wait for the user's answers.

---

## Step 7 — Create destination directories

For each slug, create the necessary subdirectories inside `projects/{slug}/`:
- `papers/` for research papers
- `resources/` for supporting files
- Code goes directly in `projects/{slug}/`

Use whatever file-system tools are available on the current platform.

---

## Step 8 — Move files to their permanent homes

For each Category A, B, and C file within the subfolder:

1. Copy the file from `inbox/{slug}/...` to its destination in `projects/{slug}/`.
2. Verify the destination file now exists.
3. Only after confirming the copy, delete the original.

After all files in a subfolder are moved, remove the now-empty
`inbox/{slug}/` directory.

---

## Step 9 — Create or update facts/experience.yaml

Research entries go directly into `facts/experience.yaml` alongside internship
and industry entries. Use the same schema. Two **optional** fields (`advisor`,
`publications`) may be added for research entries. Use `tags: [research]` to
distinguish research positions.

```yaml
  - id: "research-{slug}"
    company: "Georgia Institute of Technology"   # institution name
    title: "Undergraduate Research Assistant"    # actual role title
    location: "Atlanta, GA"
    start: "YYYY-MM"
    end: "YYYY-MM"                               # or "Present"
    advisor: "Prof. First Last"                  # optional; research only
    tech: [python, pytorch, numpy]
    bullets:
      - id: "research-{slug}-b1"
        text: >
          Concrete contribution grounded in the files.
        skills: [python, signal-processing]
    publications:                                # optional; research only
      - title: "Full Paper Title"
        venue: "Conference / Journal, Year"
        path: "projects/{slug}/papers/{filename}.pdf"
    tags: [research, ml, signal-processing]
```

Write at least one bullet per concrete contribution extractable from the files.
Apply the grounding contract: only claim what the files actually show.

---

## Step 10 — Create context write-up

Create `context/research-{slug}.md`:

```markdown
# Research: {paper_title}

**Role:** {title} — {company}
**Advisor:** {advisor}
**Period:** {start} – {end}
**Files:** projects/{slug}/

## What the research is about
2–4 sentence plain-English summary of the research problem and approach.

## What I did
Bulleted list of concrete contributions — code written, experiments run,
analyses performed, results achieved.

## Key technologies / methods
Languages, frameworks, hardware, algorithms, datasets.

## Potential resume angles
How this experience could be framed for different role types (embedded, ML,
systems, research-track, etc.).

## Publication(s)
Title, venue, year — one-sentence description of the contribution.
```

---

## Step 11 — Update processing-report.md

Append a new run section to `inbox/processing-report.md` (create if absent).
Do **not** overwrite prior entries — this file is the permanent manifest
consulted in Step 1.

```markdown
---

## Run: {ISO date}

### Folders processed

| Folder (slug) | Files moved | Destination |
|---------------|-------------|-------------|
| ml-anomaly    | 3           | projects/ml-anomaly/ |

### Loose files skipped (need a subfolder)
- {filename if any}

### Source-of-truth updates
- Updated: facts/experience.yaml (added: research-ml-anomaly)
- Created: context/research-ml-anomaly.md
- Created: projects/ml-anomaly/

### TODOs / items needing review
Any `# TODO` fields or bullets the user should verify.
```

---

## Step 12 — Report to user

Print a concise summary:
- Subfolders processed vs skipped (already processed)
- Any loose files that were warned about
- What was created or updated in `facts/` and `context/`
- Any remaining `# TODO` fields or unanswered `NEEDS_INFO.md` items
- Reminder that nothing is committed


