---
name: overnight-run
description: >
  Unattended overnight batch: verify the top N Open Postings rows are live, build and export a
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
  - `Open Postings` (sorted best first): A Tier | B Likelihood score | C Company | D Role | E Location | F Term |
    G Posted | H Apply link | I Why it scored | J Citizen pool | K In Log? (formula).
  - `Log`: the only status tracker. Skip any company + role already there.
  - `Companies`: A Company | B Source | ... | H Connections / club notes (for the summary's networking line).
  - **All status lives in the Log** (user, 2026-11-28). Never add a status column or status text to Open Postings
    or any other tab.
- Candidate facts: `CLAUDE.md`, `.claude/skills/job-application-assistant/01-candidate-profile.md`, `10-bullet-bank.md`.

## Step 0 - Pick roles
Save `get_values` dumps of `'Open Postings'!A1:K300` and `Log!A1:I1000` to `documents/overnight/<YYYY-MM-DD>/`,
then run `python tools/auto_apply.py postings-cap --postings <postings.json> --log <log.json>`. Walk its `keep`
list in order (it is already sorted best first); its `drop` list goes under "Over company cap".
- **Company rule (user, 2026-11-28): 2-3 roles per company, 3 max.** If the Log already shows 2+ submitted roles
  at a company (date in B or any result in G), take no more of its roles. Otherwise take at most 3 minus the number
  already applied. The script does this, counting General Dynamics divisions (GDMS, GD OTS, ...) together and
  keeping RTX units ("RTX (Pratt & Whitney)", "RTX (Collins)", "RTX (Raytheon)") separate. Roles you pick in this
  run count toward the cap too. Also skip a role if a near-identical one at the same company is already in `Log`.
- Grace Gong-only companies (Companies `Source` = "Grace Gong list") that are aerospace or not Fit A are fine to
  build CVs for, but flag them "apply personally" in the summary (the user won't auto-apply them). Never pick an
  international company.
- **Verify before building anything:** check the posting is live on the employer's own system (memory rule: req ID +
  title before calling it closed; otherwise "couldn't verify") and that the term is Summer or Fall 2027 (no Spring).
  Closed, unverifiable, or out-of-scope rows don't count toward N; keep walking down the `keep` list until N roles are
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

## Step 2b - Hiring manager message
Draft one message per role for the user to send on LinkedIn (they have Premium). Keep it short: about 4-5 sentences,
under ~600 characters. Write it in the user's plain voice (see the `feedback-application-answer-voice` memory: no colons,
aphorisms, tricolons, or "not just X"). Run the AI detector on it if `tools/ai_detector.py` exists; otherwise note that
it wasn't checked. Structure: applied for [Role] today → one concrete hook → one line on why this team → "happy to
answer any questions" + thanks. No coffee-chat ask.

Pick the hook to match the role type, using bullet-bank facts only, and match it to the tailored CV's top entry:
| Role type | Hook |
|---|---|
| Controls / GNC / embedded | TVC: C++ PID firmware on Teensy 4.1, IMU fusion |
| Test / I&T | TVC: staged ground tests, two static fires, telemetry root cause, test stand redesign |
| Propulsion / fluids | LRI: P&ID + fluid system integration for the IPA/LOX engine, pressurant tank trade |
| Manufacturing / fabrication | Flight Club composite/wing build (high school, so pair with a current TVC 3D-printed build) |
| CAD / mechanical design | Siemens NX: LRI pressurant tank integration, F-101 reconstruction |
| Software-leaning | Investment platform (Python/Flask/SQL) |
The "why this team" line may only use facts stated in the posting itself. Never invent company claims.

## Step 3 - Morning summary
```
# Overnight run <date> - <k> CVs ready

## Ready to apply (in rank order)
### [Company] - [Role] | posting URL
- CV: cv/Marcus Yang Resume [Company] - [Role].pdf
- Networking: <Companies col H notes, or "none on file">; add "apply personally" for flagged Grace Gong companies
- Questions: <exact question + limit> (or "not available")
- Extra uploads: <...>
- Hiring manager message (hook: <type>): <draft>

## Over company cap
## Closed / couldn't verify / out of scope
## CV notes (keyword gaps, deferred leadership edits)
```
Use bare full URLs (no markdown links). Don't update the Log tab; the user logs what they actually submit.
