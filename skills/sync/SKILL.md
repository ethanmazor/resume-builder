---
name: sync
description: >
  Incrementally sync new content from the owner's data folder into this repo's
  source of truth. Reads the source path from .sync-config.yaml (written by
  bootstrap), then merges only entries and files not already present —
  leaving existing content untouched.
triggers:
  - "sync my data"
  - "sync from my data folder"
  - "sync"
  - "update my source of truth"
user-invocable: true
---

# Sync Skill

## Purpose

After bootstrap has populated the source of truth, the owner may add new
experiences, projects, or write-ups to their external data folder. This skill
reads that folder again and merges only the **new** content — anything whose
`id` (for YAML entries) or filename (for context and project files) is not
already present in this repo.

Existing entries in `data/facts/`, `data/context/`, and `data/projects/` are **never
overwritten**. If the owner has edited a bullet or write-up directly in this
repo, those edits are preserved.

Run this skill whenever the data folder gains new material.

**Path convention:** in this skill, every `data/...` and `resumes/...` path is
relative to `WORKSPACE_ROOT` (set in `.sync-config.yaml` as `workspace_path`),
not the repository root.

## Hard rules

- **Never fabricate.** Write only what you can read in the source files.
- **Never overwrite.** Skip any entry or file already present. Do not modify
  existing `data/facts/`, `data/context/`, or `data/projects/` content.
- **Leave outputs uncommitted.** Do not `git commit` or `git push`.

---

## Step 0 — Read .sync-config.yaml

Read `.sync-config.yaml` from the repo root. It must contain:

```yaml
source_path: /absolute/path/to/data-folder
```

If the file does not exist, stop and tell the owner:

> `.sync-config.yaml` not found. Run bootstrap first:
> *"My data is at /path — bootstrap my source of truth"*

Resolve `source_path` to an absolute path and verify it is a readable
directory. If not, stop and report the error.

---

## Step 1 — Detect source structure

Verify the source folder uses this repo's schema:

- `data/profile/profile.yaml`
- `data/facts/experience.yaml`
- `data/facts/projects.yaml`
- `data/facts/skills.yaml`

If none of these exist, stop and tell the owner the source folder does not
appear to be a structured data folder.

---

## Step 2 — Load existing state

Read the current contents of:

- `data/facts/experience.yaml` → collect all existing `id` values
- `data/facts/projects.yaml` → collect all existing `id` values
- `data/facts/skills.yaml`
- `data/facts/courses.yaml` (if present) → collect existing `id` values
- `data/facts/activities.yaml` (if present) → collect existing `id` values
- `data/context/` → list all existing filenames (e.g. `flock-safety.md`)
- `data/projects/` → list all existing subdirectory names

---

## Step 3 — Merge data/facts/experience.yaml

Read `{source_path}/facts/experience.yaml`. For each entry:

- If its `id` is already in the existing set → **skip** (log: "skipped: {id}")
- If its `id` is new → append it to `data/facts/experience.yaml` (log: "added: {id}")

Preserve all existing entries and comments. Only append; never modify or
reorder existing entries.

---

## Step 4 — Merge data/facts/projects.yaml

Same logic as Step 3, applied to `data/facts/projects.yaml`.

---

## Step 5 — Merge data/facts/skills.yaml

Read `{source_path}/facts/skills.yaml`. For each skill group and each skill
within it:

- If the group already exists in the local file: append any skills not already
  listed within it.
- If the group does not exist: append the entire group.

Never remove or reorder existing skill groups or entries.

---

## Step 6 — Merge data/facts/courses.yaml and data/facts/activities.yaml

If these files exist in the source folder, apply the same ID-based merge logic
used in Steps 3–4.

---

## Step 7 — Merge data/context/*.md

List all `.md` files under `{source_path}/context/`. For each:

- If a file with the same name already exists in local `data/context/` → **skip**
- If it is new → copy verbatim to `data/context/{filename}` (log: "added: {filename}")

---

## Step 8 — Merge data/projects/

List all subdirectories under `{source_path}/projects/`. For each:

- If a subdirectory with the same name already exists in local `data/projects/` → **skip**
- If it is new → copy the entire subdirectory verbatim to `data/projects/{name}/`
  (log: "added project: {name}")

---

## Step 9 — Report

Print a brief summary:

```
Sync complete.

Added:
  data/facts/experience.yaml   +N entries: {id1}, {id2}, ...
  data/facts/projects.yaml     +N entries: {id1}, ...
  data/facts/skills.yaml       +N skills across N groups
  data/context/                +N files: {name1.md}, ...
  data/projects/               +N directories: {name1}, ...

Skipped (already present):
  data/facts/experience.yaml   N entries
  data/facts/projects.yaml     N entries
  data/context/                N files
  data/projects/               N directories

Nothing to commit — review the additions above, then commit when ready.
```

If nothing was added, say so clearly and stop.
