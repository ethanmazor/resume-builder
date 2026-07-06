# projects/

Raw code, resources, schematics, design docs, and other artifacts for each
project live here — one subfolder per project, e.g. `projects/embedded-cave-game/`.

## How this connects to the resume pipeline

The agent does NOT read raw project code when generating resumes. Instead:

1. **`projects/{name}/`** — your raw materials (code, schematics, images, notes).
2. **`context/{name}.md`** — a human-written summary you maintain that the agent
   *does* read. It should capture the problem, what you built, key decisions,
   real metrics, and the tech used. Keep it grounded — anything concrete the agent
   turns into a resume bullet must be something you actually wrote here.

When you add or update a project's code, update its `context/` write-up too so
the agent has current, accurate material to draw from.

## If your project already lives in a separate repo

Reference it via the `link` field in `facts/projects.yaml` instead of duplicating
code here. You can still keep a `context/` write-up for the agent without storing
all the source code in this repo.

## .gitignore note

Large build artifacts (binaries, object files, etc.) inside `projects/` should be
gitignored. Add patterns to the root `.gitignore` as needed.
