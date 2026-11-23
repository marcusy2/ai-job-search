---
name: overnight-run
description: >
  Unattended overnight batch: tailor CVs for the top N Internship Pipeline rows, then prefill
  each application in Chrome (Simplify autofill + tailored CV + Question Bank answers) and stop
  before Submit, leaving a morning summary. Triggers on: /overnight-run, overnight run,
  bedtime run, prefill applications overnight
---

# /overnight-run [N] - Overnight CV + Application Prefill

Bedtime prompt: `/overnight-run 15` (default N = 15). Setup checklist: `OVERNIGHT_SETUP.md`.

The user is asleep. **Never ask questions mid-run.** When something blocks a role, log it and move to
the next role. **Never click Submit / Send / Finish on any application.**

## Sources
- Sheet `Junior Internship List` (id `1HXQA89p1nO1-vMFXUi75t6xJtUdvEWHlXMFn6lgGerY`)
  - `Internship Pipeline` tab: Rank, Company, Role, Apply link (col I), My status (col N).
  - `Question Bank` tab: question in col A, answer on the row directly below, blank row between entries.
  - Read-only for this skill. Never write to Log, Sheet3, Internship Pipeline, or Question Bank.
- Candidate facts: `CLAUDE.md`, `.claude/skills/job-application-assistant/01-candidate-profile.md`,
  `10-bullet-bank.md`.

## Step 0 - Pick roles
Take the top N rows by Rank where **My status (col N) is empty**. Skip rows already in the `Log` tab
(same company + role). Write the list to `documents/overnight/<YYYY-MM-DD>/run.md` immediately, then
update that file after every role so a stalled run still leaves a usable record.

## Step 1 - CVs (all roles, before opening any form)
For each role in rank order:
1. Fetch the posting. Before calling it closed, follow the memory rule (check the employer ATS by req
   ID + title); if unverifiable, mark "couldn't verify" and still build the CV.
2. Reuse an existing `cv/main/main_<company>_<role>.tex` if one matches; otherwise tailor a new one
   following the job-application-assistant skill and every CV memory rule (one-page-times template,
   bullet bank only, TVC max 5 bullets, Flight Club/AAA leadership untouched - **any leadership
   bullet edit is deferred to the morning summary, not applied**).
3. Compile with lualatex, run `tools/verify_pdf.py` and `tools/measure_cv_density.py`, exactly 1 page.
4. Export as `cv/Marcus Yang Resume [Company] - [Role].pdf`.
5. Log uncovered JD keywords (named gaps) for the summary.

If usage runs low, stop CV work at a role boundary and still do Step 2 for the CVs already finished.

## Step 2 - Prefill (Chrome)
Load the Chrome tools in one ToolSearch call (core set + `find`, `form_input`, `file_upload`,
`get_page_text`). Call `tabs_context_mcp` first. Open each role in a **new tab**, keep all run tabs
together, and never close or reuse the user's own tabs.

**Order:** Workday / iCIMS / Taleo / SuccessFactors first; Greenhouse / Lever / Ashby / other single-page
forms last (they hold state only in the open tab).

Per role:
1. Open the apply link, click Apply.
2. **Account needed?** Use the user's normal application email and the password from the Windows user env
   var `JOB_PORTAL_PW` (read it with `powershell -c "[Environment]::GetEnvironmentVariable('JOB_PORTAL_PW','User')"`
   only at the moment of entry; never echo it, write it to a file, or put it in a log/summary). If the var is
   unset or the extension refuses password entry, mark the role "needs login" and move on. Fetch
   verification emails via the Gmail connector (search the portal sender, newest first) and open the link.
3. Click Simplify's in-page autofill. Wait for it to finish (poll with a screenshot, max ~60s). If no
   in-page Simplify control exists, fill standard fields from the candidate profile directly.
4. Replace the resume upload with the tailored CV from Step 1.
5. Review every field: fix wrong or blank required fields using profile facts only (U.S. Citizen, no
   sponsorship, grad May 2028, GPA 3.57, Champaign IL). EEO/voluntary fields: keep Simplify's value; if
   blank, leave blank and flag.
6. Essay / short-answer questions: paste the **best-matching Question Bank answer verbatim**, trimmed only
   if a hard word/char limit requires it (flag any trim). No reasonable match → leave blank and copy the
   exact question text + limit into the summary. **Do not draft new answers.**
7. Uncertain dropdowns/yes-no not covered by the profile (e.g. "willing to travel 50%?") → leave as-is and flag.
8. Advance to the final review page. Multi-page portals: click "Save and Continue" / "Save" at every step
   so a draft persists server-side. **Stop before Submit.**
9. CAPTCHA, crash, or the extension disconnecting → log the step reached, move on. Don't retry the
   same failing action more than twice.

## Step 3 - Morning summary
Finish `documents/overnight/<date>/run.md`:

```
# Overnight run <date> - <k>/<N> ready

## Ready to submit (tab open / draft saved)
- [Company] - [Role] | ATS | CV: <filename> | tab or "Workday draft: log in at <url>"

## Needs you
- [Company] - [Role] | what's missing: <unmatched question text + limit / login / CAPTCHA / field>

## Not prefilled
- [Company] - [Role] | reason (closed? / couldn't verify / stalled at step X)

## CV notes
- named keyword gaps, deferred leadership edits
```

Put every URL in as a bare full URL (no markdown links). The user submits each application
themselves. Do not update the Log tab; that happens after the user actually submits.
