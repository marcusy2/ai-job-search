# Overnight Run - Setup Checklist

## One-time (about 10 minutes)
- [ ] **Windows power:** Settings > System > Power > "When plugged in, put my device to sleep after" = **Never**. Plug in the laptop.
- [ ] **Chrome Memory Saver off:** chrome://settings/performance > Memory Saver **off** (otherwise background tabs get unloaded and the filled forms are lost).
- [ ] **Simplify:** signed in to the Chrome extension, profile up to date.
- [ ] **Portal-only password:** create a NEW password used only for job portals (not your email, bank, or school password). In PowerShell:
      `setx JOB_PORTAL_PW "your-portal-password"`
      Then restart Claude Code. Never put this password in the repo, because the repo is pushed to GitHub.
- [ ] **Gmail connector:** approve it the first time Claude asks (it's used to click verification links).
- [ ] **Claude in Chrome:** extension connected, with the ATS domains allowed (myworkdayjobs.com, greenhouse.io, lever.co, ashbyhq.com, icims.com).

## Every night
1. Close tabs you don't need, keep Chrome open, and leave the laptop plugged in.
2. In Claude Code in this repo: `/overnight-run 15`
3. Go to bed.

## Every morning
1. Open `documents/overnight/<date>/run.md`.
2. **Ready to submit:** go through the run tab group, make small edits, and click Submit. For Workday drafts, log in and submit from "My Applications".
3. **Needs you:** answer the listed questions and finish those forms.
4. Log submitted applications in the sheet as usual.

## Limits
- About 15 roles per night is realistic (CVs plus browser filling use roughly 2-4M tokens, an estimate). Two nights cover about 30 a week.
- Unattended runs can stall (extension disconnect, CAPTCHA). The summary shows where the run stopped.
