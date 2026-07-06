# Resume Style Guide (Jake's Resume)

The agent authors `resume.tex` following this guide. It is based on the popular,
ATS-friendly **Jake's Resume** template (by Jake Gutierrez, MIT-licensed). The
goal is a clean, single-column, **one-page** resume that parses well in ATS.

> Author the document, don't just fill a rigid template. You may add/remove
> sections and adjust density (within the bounds below) so the result fits on
> exactly one page. Compile with Tectonic and verify with `pdfinfo` — see
> `SKILL.md` step 6.

> **Engine note:** this repo compiles with **Tectonic (XeTeX engine)**, not
> pdfLaTeX. pdfTeX-only primitives (`\input{glyphtounicode}`, `\pdfgentounicode`)
> must be wrapped in `\ifdefined\pdfgentounicode ... \fi` guards (already done in
> the preamble below). Prefer XeTeX-compatible packages/fonts.

---

## Reference preamble + commands

Start `resume.tex` from this. These custom commands are the building blocks;
use them consistently.

```latex
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}

% Engine guard: \input{glyphtounicode} and \pdfgentounicode are pdfTeX features.
% Tectonic uses the XeTeX engine (which maps glyphs to Unicode via its OpenType
% font handling), so these must be guarded or compilation fails under Tectonic.
\ifdefined\pdfgentounicode
  \input{glyphtounicode}
\fi

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Margins — tighten within [-0.5in .. -0.7in] range if you need to save space.
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Section formatting
\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure ATS-parsable PDF (pdfTeX only; guarded for XeTeX/Tectonic)
\ifdefined\pdfgentounicode
\pdfgentounicode=1
\fi

% ---------- Custom commands ----------
\newcommand{\resumeItem}[1]{\item\small{{#1 \vspace{-2pt}}}}

\newcommand{\resumeSubheading}[4]{%
  \vspace{-2pt}\item
    \begin{tabular*}{\linewidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}}

\newcommand{\resumeProjectHeading}[2]{%
    \item
    \begin{tabular*}{\linewidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0pt, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
% leftmargin=* puts the bullet symbol at the parent left margin (page edge)
% and indents bullet text by labelwidth+labelsep — maximizes usable width.
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
```

## Header

```latex
\begin{center}
    \textbf{\Huge \scshape Jane Doe} \\ \vspace{1pt}
    \small 555-555-5555 $|$ \href{mailto:jane@example.com}{\underline{jane@example.com}} $|$
    \href{https://linkedin.com/in/janedoe}{\underline{linkedin.com/in/janedoe}} $|$
    \href{https://github.com/janedoe}{\underline{github.com/janedoe}}
\end{center}
```
Pull these values from `profile/profile.yaml`. Omit any link the profile doesn't
provide. Keep the header to a single contact line if possible.

## Section patterns

**Education**
```latex
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading{State University}{City, ST}{B.S. in Computer Science}{Sep 2019 -- May 2023}
  \resumeSubHeadingListEnd
```

**Experience**
```latex
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading{Software Engineer}{Jun 2023 -- Present}{Acme Corp}{City, ST}
      \resumeItemListStart
        \resumeItem{Tailored bullet grounded in facts/experience.yaml#acme-b1.}
      \resumeItemListEnd
  \resumeSubHeadingListEnd
```

**Projects**
```latex
\section{Projects}
  \resumeSubHeadingListStart
    \resumeProjectHeading{\textbf{Foo} $|$ \emph{Go, SQLite}}{2024}
      \resumeItemListStart
        \resumeItem{Tailored bullet grounded in facts/projects.yaml#foo-b1.}
      \resumeItemListEnd
  \resumeSubHeadingListEnd
```

**Technical Skills**
```latex
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: Python, Go, JavaScript, SQL} \\
     \textbf{Frameworks}{: React, Flask} \\
     \textbf{Developer Tools}{: Docker, AWS, Git, PostgreSQL} \\
    }}
 \end{itemize}
```

Close the document with `\end{document}`.

---

## One-page density rules (order to apply when trimming)

1. **Spacing / margins / font.** You may nudge the negative `\vspace` values,
   widen margins toward `-0.7in`, or drop to `10pt` document class size.
   Do not go below `10pt` or make it visually cramped.
2. **Cut weakest bullets.** Remove the least JD-relevant bullets first
   (target 3–5 bullets for the most relevant role, 1–2 for older ones).
3. **Drop least-relevant sections/items.** Coursework and certifications go
   first, then the least-relevant project.
4. **Condense wording.** Shorten bullets; one line each is ideal, two max.

Never drop the header or education. Keep it to **one page** — verify with
`pdfinfo` before finishing.

## Filling the page (order to apply when there's leftover white space)

A one-page resume should **use the whole page**. Visible empty space at the
bottom (or a short, sparse-looking page) is a defect, not a feature — it's fine
and encouraged to include real content that's a weaker match for the specific
JD rather than leave space blank. Apply in this order:

1. **Restore trimmed bullets.** Add back a 4th/5th bullet on a role or project
   you'd otherwise capped for brevity, as long as it's grounded in `facts/`.
2. **Surface an off-topic-but-real entry.** Add another experience, project, or
   research entry from `facts/` even if it's not a strong JD match (e.g. add the
   FPAA/Hopfield research entry to an embedded-systems resume, or a software
   project to a hardware-leaning one) — genuine breadth beats blank space.
3. **Broaden Technical Skills.** Include more of the owner's real skill
   categories/items instead of trimming to only the JD-relevant subset.
4. **Add coursework/certifications/activities** back if previously cut for space.
5. Only as a last resort, loosen spacing slightly (toward less-negative
   `\vspace`, e.g. `-0.5in` margins instead of `-0.7in`) to spread content out —
   don't just add blank vertical space; prefer real content first.

Never invent content to fill space — only add material that's already true and
present in `facts/`/`context/` but was cut for relevance/brevity.

## ATS + formatting conventions
- Single column only. No tables for layout beyond the provided `\resumeSubheading`
  patterns. No images, no text boxes, no multi-column.
- **Escape LaTeX special characters** in all content pulled from `facts/`,
  `profile/`, and `context/`: `&` → `\&`, `%` → `\%`, `$` → `\$`, `#` → `\#`,
  `_` → `\_`, `{`/`}` → `\{`/`\}`. For `~` write `\textasciitilde{}` (a bare `~`
  is a non-breaking space and will silently vanish), and for `^` use
  `\textasciicircum{}`. For "approximately", prefer writing `\raisebox{0.5ex}{\texttildelow}`
  or just the word "approx." rather than a literal `~`.
- Start bullets with strong action verbs; quantify only with **real** numbers.
- Keep tense consistent (present for current role, past for prior).
- Use standard section names ("Experience", "Education", "Projects",
  "Technical Skills") for ATS keyword parsing.
