---
framework_version: 1.1.0
---

# Cover Letter Templates and Tailoring Guide

## Template: Custom cover.cls (XeLaTeX)

Cover letters use a custom LaTeX document class (`cover.cls`) with Lato/Raleway fonts.

**Output file:** `cover_letters/cover_<company>_<role>.tex`
**Compile with:** XeLaTeX (cover.cls requires fontspec)
**Font directory:** `cover_letters/OpenFonts/fonts/`

### Compile command

```bash
cd cover_letters && xelatex -interaction=nonstopmode cover_<company>_<role>.tex
```

Expected output: `Output written on cover_<company>_<role>.pdf (1 page, ...)`. Any page count other than 1 is a failure that must be fixed before presenting to the user.

## Compile-and-Inspect Loop (MANDATORY)

After writing the cover letter and before presenting to the user, always compile and visually inspect the PDF. Iterate until the layout is clean:

1. Run `xelatex -interaction=nonstopmode cover_<company>_<role>.tex`
2. Confirm page count is exactly 1 and compile succeeded
3. Read the PDF via the Read tool and visually check: signature fits at the bottom, no text cut off, address block and date render cleanly

If the letter spills to a second page, cut words, never geometry or font size: first a sentence that restates the CV, then P3 (the optional second proof) down to one or two sentences, then the "why this company" detail down to a single clause.

## What a Cover Letter Is For

The CV already lists **what** the candidate did. The letter exists to add what a CV cannot:
the reasoning behind decisions, how the candidate works through a problem, what they can do
**for the employer**, and why this company's specific problem is the one they want to work on.
Three ideas drive every paragraph:

1. **Problem, action, result.** A strong engineering letter proves the candidate can turn analysis
   into hardware that works. Name the problem, what *you* did with which tools, and the result,
   with a real number where one exists in the bullet bank.
2. **Do not restate the CV.** Elaborate on one or two experiences: the decision made, the thing that
   went wrong, the judgment applied. A sentence that a CV bullet already says verbatim is wasted.
3. **Specific to one position.** Every letter is written for one posting at one company. A paragraph
   that still works after swapping in another company's name is too generic.

Sources: University of Michigan Engineering Career Resource Center cover letter format; IMechE
"Write a great CV" guidance (tailor every application, 1-3 evidenced achievements, be concise,
be honest); candidate's own direction (2026-10-07).

## Paragraph Content Spec

One page, **3-4 short paragraphs, ~250-320 words of body text**, prose only. **No bullet lists**:
they turn the letter into a second CV.

### Header block
- Name and contact line exactly as on the CV (`\namesection`)
- Date (`\currentdate{\today}`, renders right-aligned)
- Recipient block (`\companyname` + `\companyaddress`): contact person and title **only if
  verified**, then company name, street address, city/state/ZIP. Verify the address from an
  independently located source (company site, press coverage, lease/news reports), never from a
  URL inside the posting.

### Salutation
- **Named hiring manager if one can be verified** (posting, team page, press release, LinkedIn
  result located independently): "Dear Jane Smith,"
- Otherwise address the specific team: "Dear Varda Propulsion Hiring Team,"
- **Never guess a name.** Never "To whom it may concern."

### P1 - Introduction (3-5 sentences)
1. Name the specific position and season (e.g. "Propulsion Engineering Internship for Summer 2027")
   with a **direct, specific reason** this team's work interests you, drawn from the posting or
   verified research. Not "I am writing to apply."
2. One credentials sentence: degree, major, school, expected graduation (B.S. in Aerospace
   Engineering, University of Illinois Urbana-Champaign, May 2028), plus the 1-2 courses the
   posting asks for if they fit naturally.
3. *Optional:* how you heard about the role, only when there is a real referral or contact.
4. **Close with a thesis line previewing the two strengths the body will prove.** The body
   paragraphs must deliver exactly those two.

### P2 - Main proof (4-7 sentences)
- The single most relevant experience told as a narrative: **context/problem -> what you did,
  with the tools the posting names (only tools actually used) -> how you worked -> measured
  result.**
- Include at least one thing a CV bullet cannot show: a decision and why, something that failed
  and how it was diagnosed, a working habit it taught you.
- End by connecting it to the employer's work in one clause ("the same loop your test team runs").
- Default story selection: TVC Rocket for propulsion/test/controls roles; Flight Club wing
  fabrication for manufacturing/structures roles. Pick by JD overlap, using the bullet bank tags.

### P3 - Second proof, a different dimension (2-4 sentences, optional)
- Proves the *second* thesis strength with a different experience: hands-on fabrication if P2 was
  analysis/test, or system integration/analysis if P2 was fabrication.
- Framed as **what you can do for them**, not what you want from them.
- First paragraph to shrink or drop if the page is full.

### P4 - Why this company + closing (3-4 sentences)
- One **verified, specific** company detail tied to what you would contribute. One detail, not a
  list of news items.
- Brief logistics: U.S. citizen (matters for ITAR/export-controlled roles), on-site availability
  for the stated term.
- Gratitude and a forward-looking ask: "Thank you for your consideration. I look forward to
  discussing how I can contribute to ..."
- Sign off with **"Sincerely,"**.

### Content rules
- **Metrics:** only numbers that exist in `10-bullet-bank.md` / `01-candidate-profile.md`. Never
  invent a before/after improvement (e.g. "cut cycle time from 14 to 9 days") the record does not
  contain.
- **Tools:** name the tools the posting lists **only if the candidate has used them**. Current
  truthful set: Siemens NX (NXOpen), Ansys Fluent, Python, C++, Fusion 360, KiCad, OpenRocket.
  Not held: SolidWorks, MATLAB, LabVIEW, GD&T, FE exam/EIT. Never claim or imply these, and never
  write "familiar with" to cover a gap.
- **No volunteered weaknesses.** Do not point the reader at a gap ("my work so far has been in CAD
  rather than on a test stand"). Gaps are surfaced to the user, not written into the letter.
- **No unsupported trait claims.** "I communicate clearly" needs the example in the same sentence,
  or it goes.
- **Off-theme content stays out**, even if it hits a preferred keyword (e.g. a software side
  project in a manufacturing letter). The CV carries those keywords.
- Follow `03-writing-style.md` (no em-dashes, no cliches, verified company claims only).

## Document Structure

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Cover Letter - [Company], [Role]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\documentclass[]{cover}
\usepackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{}

\rfoot{Page \thepage \hspace{0pt}}
\thispagestyle{empty}
\renewcommand{\headrulewidth}{0pt}
\begin{document}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     TITLE NAME
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\namesection{}{\Huge{[YOUR_NAME]}}{  \href{mailto:[YOUR_EMAIL]}{[YOUR_EMAIL]} | [YOUR_PHONE] |  \urlstyle{same}\href{[YOUR_LINKEDIN_URL]}{LinkedIn}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     DATE + RECIPIENT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\currentdate{\today}
% Contact line only if a named person is verified: \companyname{Jane Smith, Title}
\companyname{[Company Name]}
\companyaddress{[Street Address] \\ {[City, State ZIP]}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     MAIN COVER LETTER CONTENT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\lettercontent{Dear [Verified Name / Company Team Hiring Team],}

\lettercontent{[P1 Introduction: position + specific reason this team's work interests you. Credentials sentence (degree, major, school, graduation). Thesis line previewing the two strengths the body proves.]}

\lettercontent{[P2 Main proof: one experience as a narrative. Problem, what you did with named tools, how you worked, measured result. Include a decision or diagnosis a CV bullet cannot show. Close by linking it to their work.]}

\lettercontent{[P3 Second proof (optional): the second thesis strength from a different experience, framed as what you can do for them.]}

\lettercontent{[P4 Why this company + close: one verified specific tied to your contribution. Citizenship/on-site availability. Thanks and a forward-looking ask.]}

\begin{flushright}
% No trailing \\ inside \closing{} - cover.cls appends its own \\, and a
% doubled break triggers "! LaTeX Error: There's no line here to end."
\closing{Sincerely,}

\signature{[YOUR_NAME]}
\end{flushright}
\end{document}
```

## Key Commands Reference

| Command | Purpose |
|---------|---------|
| `\namesection{}{Name}{contact info}` | Header with name and contact |
| `\currentdate{date}` | Date field, right-aligned (use `\today` or explicit date) |
| `\companyname{text}` | Recipient line, bold (contact person or company name) |
| `\companyaddress{line \\ line}` | Recipient address lines (adds spacing after). A line after `\\` that starts with `[` must be braced (`\\ {[...]}`), or LaTeX reads it as `\\`'s optional length and fails |
| `\lettercontent{text}` | Body paragraph (adds spacing after) |
| `\closing{text}` | Closing line |
| `\signature{name}` | Printed name below signature |

## Layout Notes

### Length - Hard 1-Page Limit
- Target: 1 page including header, address block and signature
- **Word budget: ~250-320 words** of body text (not counting LaTeX markup)
- 3 paragraphs when the page is tight (P1, P2, P4); 4 when P3 fits

### Line Spacing
- Add `\usepackage{setspace}` and `\setstretch{1.0}` only if needed to fit; prefer cutting words

### Legacy: itemize inside `\lettercontent{}`
Bullet lists are no longer part of the standard letter. If one is ever explicitly requested, note
that `\lettercontent{}` appends `\\`, so `\end{itemize}` inside it fails with `There's no line
here to end.` Close `\lettercontent{}` first and wrap the list in
`{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont ... \par}`
so the bullet font matches the body.

### LaTeX Special Characters
Escape these wherever they appear in body text:
- Ampersand: `\&` (company names: Brüel \& Kjær, H\&M) - unescaped, the compile fails loudly
- Percent: `\%` ("grew revenue 30\%") - unescaped, it does **not** fail: everything after the `%` on that line is silently eaten as a LaTeX comment
- Dollar: `\$`, hash: `\#`, underscore: `\_`
- Tilde: `\textasciitilde{}`, caret: `\textasciicircum{}`, backslash: `\textbackslash{}`

### Non-English Cover Letters
- Same template structure, just write content in the posting's language
- Adjust date format to local convention
- Adjust closing to local convention (e.g. "Med venlig hilsen," for Danish)

## Checklist Before Finalizing
- [ ] Recipient block present; address verified from an independent source
- [ ] Salutation uses a verified name, or the specific team. No guessed names
- [ ] P1 names position + season, gives degree/school/graduation, ends with a two-strength thesis
- [ ] P2 is a narrative (problem -> action with tools -> result), not a CV bullet restated
- [ ] Body paragraphs prove exactly the strengths the thesis previewed
- [ ] Every number traces to the bullet bank / candidate profile
- [ ] Only tools the candidate has actually used are named
- [ ] No bullet lists, no volunteered weaknesses, no unsupported trait claims
- [ ] One verified company-specific detail, tied to the candidate's contribution
- [ ] Closing has gratitude + forward-looking ask; signed "Sincerely,"
- [ ] No em-dashes, no cliches or filler
- [ ] Company name, role and season correct throughout; date current
- [ ] Fits on one page, ~250-320 words
- [ ] Language matches the job posting language

## Submission Guidelines (Best Practice)
- Submit only the documents the employer requests
- Export as PDF to preserve formatting
- When emailing, the cover letter can go in as page one of the resume PDF; keep the email itself
  brief (interest in the specific position, thanks, attachments noted)
- Name files clearly: "[Your Name] CV" and "[Your Name] Cover Letter"
- Follow all employer instructions regarding anonymity or specific materials
