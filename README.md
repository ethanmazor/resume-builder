# Resume Builder

Maintain one one-page **base resume** and generate lightly tailored, grounded
copies for job descriptions. The base resume is the owner's home base: it comes
from an existing resume when one is provided, or is built from the owner's
approved facts when one is not.

For each job description, the builder starts from that base and makes only
minor truth-preserving changes, such as surfacing supported skills, tools,
coursework, or certifications; reordering existing content; and using faithful
keyword terminology. It never invents bullets, experience, or qualifications.

## Workflow

```text
owner's personal documents
  existing resume(s), project files, notes, credentials
        |
        v
resume-builder-workspace/
  data/base-resume/                 selected home-base source and history
  resumes/base/resume.pdf           compiled base resume
  data/jobs/acme-role.md            job description
  resumes/acme-role/resume.pdf      lightly tailored derived resume
```

During setup, the agent inventories existing resumes and asks the owner to
choose one base when multiple candidates are present. The owner can then refine
that base at any time, or ask the agent to create it when no resume was supplied.

Example prompts:

- `My data is at ~/my-resume-data - bootstrap my source of truth.`
- `Refine my base resume to emphasize systems work.`
- `Fetch this job: https://example.com/jobs/123.`
- `Build a resume for acme-software-engineer.`

## Data layout

| Path | Purpose |
|------|---------|
| `data/base-resume/` | Owner-selected base resume source and change notes. |
| `data/profile/` | Static identity, contact details, and education. |
| `data/facts/` | Factual guardrail and approved bullet pool. |
| `data/context/` | Supporting project and experience write-ups. |
| `data/jobs/` | Job-description inputs. |
| `resumes/base/` | Compiled home-base resume. |
| `resumes/{job-slug}/` | Derived one-page resume and tailoring notes. |

The agent compiles every base or derived resume with `scripts/build.sh` and
checks it is exactly one page. Outputs are left uncommitted for owner review.
