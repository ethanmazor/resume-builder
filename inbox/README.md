# inbox/ — Drop Zone

Drop **one subfolder per project or experience** here, then run the
**ingest-inbox** skill to have the agent automatically classify and organise
everything.

## Structure

```
inbox/
  my-research-project/       ← folder name becomes the slug
    paper.pdf
    analysis.py
    notes.md
  another-project/
    schematic.png
    firmware.c
```

Each subfolder should contain all files related to one project, research
experience, or job. **Do not drop loose files directly into inbox/** — the
agent will warn you and refuse to process them.

## Folder naming

Use lower-kebab-case that describes the project, e.g.:
- `ml-anomaly-detection`
- `fpga-fir-filter`
- `gt-research-fall-2025`

The folder name becomes the slug used in `projects/`, `facts/experience.yaml`,
and `context/`. Choose something stable and descriptive.

## What to put inside a subfolder

| File type | Examples | Where it ends up |
|-----------|----------|-----------------|
| Research paper (PDF or LaTeX) | `paper.pdf`, `paper.tex` | `projects/{slug}/papers/` |
| Project code | `*.c`, `*.py`, `*.m`, `*.v` | `projects/{slug}/` |
| Schematics / images / datasheets | `*.png`, `*.pdf` (non-paper) | `projects/{slug}/resources/` |
| Notes / write-ups | `*.md`, `*.txt` | `projects/{slug}/resources/` |

## How to run

Open a Copilot/Claude/Codex chat in this repo and say:

> Process my inbox

The agent will, for each subfolder:
1. Read and classify every file inside it
2. Extract text from PDFs and source files
3. Create or update `facts/experience.yaml`, `context/`, and `projects/`
4. Move the subfolder contents to their permanent home in `projects/{slug}/`
5. If it can't determine required metadata (dates, role, advisor), write
   `inbox/NEEDS_INFO.md` with specific questions — fill it in and re-run

## Files/folders the agent ignores
- `README.md` (this file)
- `.gitkeep`
- `NEEDS_INFO.md`
- `processing-report.md`

## Already processed

Processed subfolder names are recorded in `processing-report.md`. Re-running
the skill will skip any folder already listed there, so it is safe to leave
processed subfolders in inbox until you are ready to clean up.
