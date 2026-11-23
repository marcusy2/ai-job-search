---
name: overnight-run
description: >
  Unattended overnight batch: verify the top N Internship Pipeline postings are live, build and export a
  tailored CV for each, and list every application's questions (from ATS APIs) in a morning summary. No browser form filling (the user runs Simplify). Triggers on: /overnight-run,
  overnight run, bedtime run, batch CVs overnight
---

# /overnight-run [N] - Overnight CVs + Application Questions

Bedtime prompt: `/overnight-run 10` (default N = 10). The user then works through the list in the
morning: open each posting, run Simplify autofill, upload the ready CV, answer the listed questions, submit.

The user is asleep. **Never ask questions mid-run.** If something blocks a role, log it and move on.
**Never fill or submit application forms, create accounts, type passwords, or accept terms.**

## Sources
- Sheet `Junior Internship List` (id `1HXQA89p1nO1-vMFXUi75t6xJtUdvEWHlXMFn6lgGerY`), read-only for this skill:
  - `Internship Pipeline`: Rank, Company, Role, Apply link (col I), My status (col N).
  - `Log`: skip any company + role already there.
- Candidate facts: `CLAUDE.md`, `.claude/skills/job-application-assistant/01-candidate-profile.md`, `10-bullet-bank.md`.

## Step 0 - Pick roles
Walk the pipeline in Rank order. Take rows where **My status (col N) is empty** and the role isn't in `Log`.
- **Company cap: at most 4 roles per company** in one run, counting the ones already in `Log` that have no result yet.
  Count by the Company column as written (e.g. "RTX (Pratt & Whitney)" and "RTX (Collins)" are separate). When a
  company has more eligible rows, keep the best role-fit ones and list the rest under "Over company cap".
- **Verify before building anything:** check the posting is live on the employer's own system (memory rule: req ID +
  title before calling it closed; otherwise "couldn't verify") and that the term is Summer or Fall 2027 (no Spring).
  Closed, unverifiable, or out-of-scope rows don't count toward N; keep walking down the pipeline until N roles are
  verified or ~25 rows have been checked.
- Write the list to `documents/overnight/<YYYY-MM-DD>/run.md` immediately and update it after every role.

## Step 1 - CVs
For each verified role, in rank order:
1. Reuse an existing `cv/main/main_<company>_<role>.tex` if one matches. Otherwise tailor one by building from the
   closest recent tailored CV (same role type), following the job-application-assistant skill and every CV memory
   rule (one-page-times template, bullet-bank wording only, TVC max 5 bullets, page-composition limits). Leadership
   (Flight Club/AAA) stays untouched, and any leadership edit idea goes into the summary instead of being applied.
2. Compile with lualatex. Run `tools/verify_pdf.py --pages 1` and `tools/measure_cv_density.py`. Confirm in code
   that the header, Education rows, Skills, and Leadership are byte-identical to the base CV.
3. Export as `cv/Marcus Yang Resume [Company] - [Role].pdf`.
4. Log named keyword gaps (JD terms with no honest bullet-bank match).

## Step 2 - Application questions (machine-readable, no browser filling)
Pull the posting's application questions from the ATS's public API where one exists:
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/<board>/jobs/<id>?questions=true`
- Lever: `https://api.lever.co/v0/postings/<company>/<id>` (custom questions appear on the apply page; fetch `.../apply` if needed)
- Ashby: `https://api.ashbyhq.com/posting-api/job-board/<board>?includeCompensation=true` (or the posting's application form JSON)
- Workday / iCIMS / Taleo / SuccessFactors / RippleMatch: no public question API; write "questions not available" and move on.

List each question beyond standard fields (name/contact/EEO/work authorization, which Simplify handles) as its exact
text + any word/char limit, plus required uploads beyond a resume. **Don't match them to Question Bank answers and don't
draft answers**; the user does that.

## Step 3 - Morning summary
```
# Overnight run <date> - <k> CVs ready

## Ready to apply (in rank order)
### [Company] - [Role] | posting URL
- CV: cv/Marcus Yang Resume [Company] - [Role].pdf
- Questions: <exact question + limit> (or "not available")
- Extra uploads: <...>

## Over company cap
## Closed / couldn't verify / out of scope
## CV notes (keyword gaps, deferred leadership edits)
```
Use bare full URLs (no markdown links). Don't update the Log tab; the user logs what they actually submit.
