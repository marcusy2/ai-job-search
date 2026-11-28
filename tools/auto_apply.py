#!/usr/bin/env python3
"""Deterministic helpers for the /auto-apply skill.

The browser work and judgment calls happen in Claude Code (Playwright MCP); this
script does the parts that should never vary between runs:

    triage URL                      which portal is this, and can it be auto-applied?
    queue --log F --history F       pick today's rows from the Log tab (JSON dumps)
          [--companies F]           ... holding back Grace Gong companies not approved for auto-apply
    postings-cap --postings F --log F   Open Postings rows to keep under the per-company rule
    qbank --values F                parse the Question Bank tab into Q/A pairs
    delays --n N                    random human-like pauses for the run

Sheet dumps are the raw `values` arrays from the Google Sheets connector's
get_values (row 1 = header), saved to a JSON file by the skill.
"""

import argparse
import difflib
import json
import random
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / ".claude" / "skills" / "auto-apply" / "config.json"

# Portals whose public application form needs no account. Matched on hostname suffix.
AUTO_HOSTS = {
    "greenhouse.io": "greenhouse",
    "lever.co": "lever",
    "ashbyhq.com": "ashby",
    "bamboohr.com": "bamboohr",
    "jobs.gem.com": "gem",
    "jobs.gusto.com": "gusto",
    "ats.rippling.com": "rippling",
    "pinpointhq.com": "pinpoint",
    "jobs.smartrecruiters.com": "smartrecruiters",
    "workable.com": "workable",
}

# Portals that need an account, a login, or a third-party ToS before you can apply.
MANUAL_HOSTS = {
    "myworkdayjobs.com": ("workday", "Workday account/login required"),
    "myworkdaysite.com": ("workday", "Workday account/login required"),
    "careers.rtx.com": ("workday", "RTX career site hands off to Workday (account required)"),
    "icims.com": ("icims", "iCIMS login required"),
    "taleo.net": ("taleo", "Taleo account required"),
    "brassring.com": ("brassring", "BrassRing account required"),
    "ripplematch.com": ("ripplematch", "RippleMatch account + ToS required"),
    "oraclecloud.com": ("oracle", "Oracle Recruiting account/email verification required"),
    "adp.com": ("adp", "ADP account required"),
    "successfactors.com": ("successfactors", "SuccessFactors account required"),
    "successfactors.eu": ("successfactors", "SuccessFactors account required"),
    "linkedin.com": ("linkedin", "LinkedIn automation excluded (ToS / account risk)"),
    "usajobs.gov": ("usajobs", "USAJOBS login required"),
    "usastaffing.gov": ("usajobs", "USAJOBS login required"),
    "paylocity.com": ("paylocity", "Paylocity multi-page portal"),
    "ultipro.com": ("ukg", "UKG/UltiPro account required"),
    "paycomonline.net": ("paycom", "Paycom multi-page portal"),
    "eightfold.ai": ("eightfold", "Eightfold portal (account required)"),
    "jobs.deere.com": ("eightfold", "Deere Eightfold portal (account required)"),
    "ttcportals.com": ("workday", "Parker career site hands off to Workday (account required)"),
    "joinhandshake.com": ("handshake", "Handshake login required"),
}

MANUAL_STATUSES = ("applied", "manual review", "needs manual review", "unconfirmed")


def _host_match(host: str, suffix: str) -> bool:
    return host == suffix or host.endswith("." + suffix)


def triage(url: str) -> dict:
    """Classify an apply link: tier auto | manual | attempt (unknown, try once)."""
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if not host:
        return {"ats": "unknown", "tier": "manual", "reason": "No valid apply link"}
    for suffix, (ats, reason) in MANUAL_HOSTS.items():
        if _host_match(host, suffix):
            return {"ats": ats, "tier": "manual", "reason": reason}
    for suffix, ats in AUTO_HOSTS.items():
        if _host_match(host, suffix):
            return {"ats": ats, "tier": "auto", "reason": ""}
    query = parse_qs(parsed.query)
    if "gh_jid" in query:
        return {"ats": "greenhouse-embed", "tier": "auto", "reason": ""}
    if "ashby_jid" in query:
        return {"ats": "ashby-embed", "tier": "auto", "reason": ""}
    if "lever-source" in query or "lever-origin" in query:
        return {"ats": "lever-embed", "tier": "auto", "reason": ""}
    return {
        "ats": "unknown",
        "tier": "attempt",
        "reason": "Company career site; follow Apply and re-triage the destination",
    }


def _norm(text: str) -> str:
    text = text.lower().replace("&", " and ")
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


_PREFIX = {"resume": "Marcus Yang Resume ", "cover": "Marcus Yang Cover Letter "}

# Words every intern title shares; matching on them paired "Thermal Engineering Intern"
# with "GNC Hardware Engineering Intern" (difflib 0.74).
_GENERIC = {
    "intern", "interns", "internship", "internships", "engineer", "engineering", "summer", "fall",
    "spring", "2026", "2027", "2028", "co", "op", "coop", "the", "and", "of", "a", "an", "in",
    "for", "to", "program", "student", "undergraduate", "college", "onsite", "position", "role",
}


def _key_tokens(text: str) -> set:
    return {t for t in _norm(text).split() if t not in _GENERIC}


def _role_score(want: str, have: str) -> float:
    """Share of the shorter title's distinctive words found in the other title.

    Generic-only titles ("Engineering Intern") fall back to a strict fuzzy ratio.
    """
    a, b = _key_tokens(want), _key_tokens(have)
    if not a or not b:
        ratio = difflib.SequenceMatcher(None, _norm(want), _norm(have)).ratio()
        return ratio if ratio >= 0.9 else 0.0
    return len(a & b) / min(len(a), len(b))


def find_document(company: str, role: str, folder: Path, kind: str = "resume"):
    """Best-matching exported PDF for company + role, or None.

    Filenames follow 'Marcus Yang Resume [Company] - [Role].pdf'. The Log's company
    can be a short form ("Freeform", "Vast"), so the company only has to be a
    token-prefix match, while the role must share >= 75% of its distinctive words
    (ties broken by overall fuzzy similarity).
    """
    prefix = _PREFIX[kind]
    want_company = _norm(company)
    if not want_company or not folder.is_dir():
        return None
    best, best_score = None, 0.0
    for pdf in folder.glob("*.pdf"):
        if not pdf.name.startswith(prefix) or " - " not in pdf.stem:
            continue
        file_company, file_role = pdf.stem[len(prefix):].split(" - ", 1)
        fc = _norm(file_company)
        if not (fc.startswith(want_company) or want_company.startswith(fc)):
            continue
        score = _role_score(role, file_role)
        score += 0.01 * difflib.SequenceMatcher(None, _norm(role), _norm(file_role)).ratio()
        if score > best_score:
            best, best_score = pdf, score
    if best is None or best_score < 0.75:
        return None
    return str(best.resolve())


def _cell(row: list, idx: int) -> str:
    return row[idx].strip() if idx < len(row) and isinstance(row[idx], str) else ""


_CORP_WORDS = {"inc", "corp", "corporation", "technologies", "technology", "industries", "company",
               "co", "llc", "ltd", "the"}
_PARENT_UNITS = ("rtx", "textron")  # "RTX (Collins)" -> the unit in parentheses is the company


def company_key(name: str) -> str:
    """Normalized company name used for the per-company cap and Companies-tab lookups.

    General Dynamics divisions (GDMS, GD OTS, ...) collapse to one company (user rule).
    RTX units stay separate: "RTX (Collins)" and "Collins Aerospace (RTX)" both -> "collins aerospace".
    """
    low = name.lower().strip()
    if "general dynamics" in low or re.match(r"^gd\b", low):
        return "general dynamics"
    for unit, key in (("collins", "collins aerospace"), ("raytheon", "raytheon"), ("pratt", "pratt whitney")):
        if unit in low:
            return key
    paren = re.search(r"\(([^)]*)\)", low)
    if paren and low.split("(")[0].strip() in _PARENT_UNITS:
        low = paren.group(1)
    words = [w for w in _norm(low).split() if w not in _CORP_WORDS]
    return " ".join(words)


def same_company(a: str, b: str) -> bool:
    """Keys match exactly, or a one-word key is the first word of the other ("varda" ~ "varda space")."""
    if not a or not b:
        return False
    if a == b:
        return True
    short, long_ = sorted((a, b), key=lambda k: len(k.split()))
    return len(short.split()) == 1 and long_.split()[0] == short


def applied_counts(log_values: list) -> dict:
    """company_key -> number of Log rows already submitted (date applied in B or any result in G)."""
    counts = {}
    for row in log_values[1:]:
        company = _cell(row, 4)
        if company and (_cell(row, 1) or _cell(row, 6)):
            key = company_key(company)
            counts[key] = counts.get(key, 0) + 1
    return counts


def count_for(company: str, counts: dict) -> int:
    key = company_key(company)
    return sum(n for k, n in counts.items() if same_company(key, k))


def companies_lookup(companies_values: list) -> dict:
    """Companies tab dump -> company_key -> {source, fit, outside_aerospace, connections}.

    Companies columns: A Company | B Source | C What they do | D Location | E Sector | F Fit |
    G Outside aerospace? | H Connections / club notes | I Openings note.
    """
    out = {}
    for row in companies_values[1:]:
        if _cell(row, 0):
            out[company_key(_cell(row, 0))] = {
                "company": _cell(row, 0), "source": _cell(row, 1), "fit": _cell(row, 5),
                "outside_aerospace": _cell(row, 6), "connections": _cell(row, 7),
            }
    return out


def company_info(company: str, lookup: dict):
    key = company_key(company)
    if key in lookup:
        return lookup[key]
    return next((v for k, v in lookup.items() if same_company(key, k)), None)


def personal_only_reason(info) -> str:
    """Grace Gong companies the user hasn't approved for auto-apply (user, 2026-11-28).

    Only Fit A companies outside aerospace may be auto-applied when the company came from
    the Grace Gong list alone. Aerospace/space/drone ones the user applies to personally.
    """
    if not info or info["source"].strip().lower() != "grace gong list":
        return ""
    if info["fit"].upper().startswith("A") and info["outside_aerospace"].lower() == "yes":
        return ""
    return "Grace Gong company outside the approved auto-apply set (aerospace or not Fit A): apply personally"


def _history_urls(history_values: list) -> set:
    """Links already finished (applied / manual review / unconfirmed submit).

    History columns: Date | Log row | Company | Role | Link | Outcome | Blocker | Mode.
    The LATEST row per link decides, so 'Manual -> Retry -> Unconfirmed submit' stays
    finished (no double submit), while a Retry the user adds after a blocker re-opens it.
    Dry-run rows don't change a link's state.
    """
    latest = {}
    for row in history_values[1:]:
        link, outcome = _cell(row, 4), _cell(row, 5).lower()
        if not link or outcome.startswith("dry run"):
            continue
        latest[link] = outcome
    return {link for link, outcome in latest.items()
            if any(outcome.startswith(s) for s in MANUAL_STATUSES)}


def _dry_ready_urls(history_values: list) -> set:
    """Links whose latest history row is a clean dry run (used to walk the queue in dry mode)."""
    latest = {}
    for row in history_values[1:]:
        if _cell(row, 4):
            latest[_cell(row, 4)] = _cell(row, 5).lower()
    return {link for link, outcome in latest.items() if outcome.startswith("dry run")}


def build_queue(log_values: list, history_values: list, max_forms: int, repo: Path = REPO,
                skip_portals=(), skip_dry_ready: bool = False, companies_values=None,
                company_cap: int = 0) -> dict:
    """Log rows ready to apply: link in H, date applied (B) and results (G) empty.

    Log columns: A due date | B date applied | C Cover Letter? | D questions? |
    E company | F position | G results | H website | I location.
    skip_portals: ATS names (e.g. workday, adp) dropped silently: not opened, not logged.
    skip_dry_ready: also skip rows whose latest outcome is a clean dry run.
    companies_values: Companies tab dump; Grace Gong-only companies outside the approved set go to
        `personal` (not opened, no history row).
    company_cap: max submitted roles per company (Log rows already applied + this run). Rows past it
        go to `over_company_cap` (not opened, no history row). 0 = no cap.
    """
    done = _history_urls(history_values)
    if skip_dry_ready:
        done |= _dry_ready_urls(history_values)
    lookup = companies_lookup(companies_values or [])
    forms, manual, skipped, portal_skipped, personal = [], [], [], [], []
    for i, row in enumerate(log_values[1:], start=2):
        company, role, link = _cell(row, 4), _cell(row, 5), _cell(row, 7)
        if not link.startswith("http") or _cell(row, 1) or _cell(row, 6):
            continue
        if not company or not role:
            # A bare link with no company/position isn't a queued application; the user
            # doesn't want it re-logged as manual review on every run.
            portal_skipped.append({"row": i, "company": company, "ats": "incomplete-log-row"})
            continue
        if link in done:
            skipped.append({"row": i, "company": company, "link": link})
            continue
        item = {
            "row": i,
            "company": company,
            "role": role,
            "link": link,
            "location": _cell(row, 8),
            "due": _cell(row, 0),
            **triage(link),
        }
        if item["ats"] in skip_portals:
            portal_skipped.append({"row": i, "company": company, "ats": item["ats"]})
            continue
        reason = personal_only_reason(company_info(company, lookup))
        if reason:
            personal.append({"row": i, "company": company, "role": role, "link": link, "reason": reason})
            continue
        item["resume"] = find_document(company, role, repo / "cv", "resume")
        item["cover_letter"] = find_document(company, role, repo / "cover_letters", "cover")
        if item["tier"] == "manual":
            manual.append(item)
        elif item["resume"] is None:
            item["tier"] = "manual"
            item["reason"] = f"No tailored CV found (expected cv/Marcus Yang Resume {company} - {role}.pdf)"
            manual.append(item)
        else:
            forms.append(item)
    # Known no-account portals before career sites (which often hand off to Workday),
    # then rows with a due date (soonest first), then Log order.
    forms.sort(key=lambda r: (r["tier"] != "auto", _due_key(r["due"]), r["row"]))
    over_company_cap = []
    if company_cap:
        counts, kept = applied_counts(log_values), []
        for item in forms:
            n = count_for(item["company"], counts)
            if n >= company_cap:
                item["reason"] = f"Company cap: already {n} application(s) at {item['company']} (max {company_cap})"
                over_company_cap.append(item)
                continue
            key = company_key(item["company"])
            counts[key] = counts.get(key, 0) + 1  # this run's submit counts toward the next row
            kept.append(item)
        forms = kept
    return {
        "forms": forms[:max_forms],
        "over_cap": forms[max_forms:],
        "manual": manual,
        "already_done": skipped,
        "portal_skipped": portal_skipped,
        "personal": personal,
        "over_company_cap": over_company_cap,
    }


def cap_postings(postings_values: list, log_values: list, stop_at: int = 2, cap: int = 3) -> dict:
    """Apply the per-company rule to the Open Postings tab (rows already in score order).

    Open Postings columns: A Tier | B Score | C Company | D Role | E Location | F Term | G Posted |
    H Apply link | I Why | J Citizen pool | K In Log?.
    A company with >= stop_at roles already applied in the Log gets no more postings (user,
    2026-11-28). Otherwise keep its best (cap - applied) rows. Rows marked In Log = Yes are dropped.
    """
    counts, taken = applied_counts(log_values), {}
    keep, drop = [], []
    for i, row in enumerate(postings_values[1:], start=2):
        company = _cell(row, 2)
        if not company:
            continue
        entry = {"row": i, "company": company, "role": _cell(row, 3), "link": _cell(row, 7)}
        if _cell(row, 10).lower() == "yes":
            drop.append({**entry, "reason": "already in Log"})
            continue
        n = count_for(company, counts)
        key = company_key(company)
        if n >= stop_at:
            drop.append({**entry, "reason": f"already applied to {n} roles at this company"})
        elif n + taken.get(key, 0) >= cap:
            drop.append({**entry, "reason": f"company cap ({cap} incl. {n} applied)"})
        else:
            taken[key] = taken.get(key, 0) + 1
            keep.append(entry)
    return {"keep": keep, "drop": drop}


def _due_key(due: str):
    m = re.match(r"^(\d{1,2})/(\d{1,2})", due or "")
    return (0, int(m.group(1)), int(m.group(2))) if m else (1, 0, 0)


def history_slot(history_values: list, link: str):
    """Sheet row to overwrite for this link (one row per role), or None to append."""
    for i, row in enumerate(history_values[1:], start=2):
        if _cell(row, 4) == link.strip():
            return i
    return None


def parse_question_bank(values: list) -> list:
    """Question Bank tab: question row, answer row(s), blank row, repeat (column A).

    A block with only a question (no answer yet) is kept with answer "" so the
    skill can tell 'question known, no answer' from 'question unknown'.
    """
    pairs, block = [], []
    for row in values + [[]]:
        text = _cell(row, 0) if row else ""
        if text:
            block.append(text)
            continue
        if block:
            pairs.append({"question": block[0], "answer": "\n".join(block[1:])})
            block = []
    return pairs


MIDWEST = {
    "IL", "IN", "IA", "KS", "MI", "MN", "MO", "NE", "ND", "OH", "SD", "WI",
    "ILLINOIS", "INDIANA", "IOWA", "KANSAS", "MICHIGAN", "MINNESOTA", "MISSOURI", "NEBRASKA",
    "NORTH DAKOTA", "OHIO", "SOUTH DAKOTA", "WISCONSIN",
}


def is_midwest(job_location: str) -> bool:
    """True if the job location names a Midwest state (e.g. 'Cedar Rapids, IA', 'Olathe, Kansas')."""
    text = (job_location or "").upper()
    # State codes only right after a comma ("Cedar Rapids, IA"), so "(in office)" isn't Indiana.
    codes = set(re.findall(r",\s*([A-Z]{2})\b", text))
    names = {s for s in MIDWEST if len(s) > 2 and re.search(rf"(?<![A-Z]){s}\b", text)}
    return bool((codes & MIDWEST) or names)


def location_for(job_location: str, profile: dict) -> str:
    """Single 'current location' answer: Champaign for Midwest jobs, else the home city."""
    if is_midwest(job_location):
        return profile.get("midwest_location", "Champaign, IL")
    return profile.get("current_location", "San Mateo, CA")


DETECTOR_PY = Path.home() / ".venvs" / "ai-detector" / "Scripts" / "python.exe"


def run_detector(path: str) -> int:
    """Run tools/ai_detector.py in its venv (keeps the skill's permission rule to one command)."""
    import os
    import subprocess

    if not DETECTOR_PY.exists():
        print(f"DETECTOR MISSING: {DETECTOR_PY}")
        return 2
    env = dict(os.environ, TRANSFORMERS_VERBOSITY="error", HF_HUB_DISABLE_PROGRESS_BARS="1")
    proc = subprocess.run(
        [str(DETECTOR_PY), str(REPO / "tools" / "ai_detector.py"), path],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    print(proc.stdout, end="")
    return proc.returncode


def delays(n: int, lo: float, hi: float, seed=None) -> list:
    rng = random.Random(seed)
    return [round(rng.uniform(lo, hi)) for _ in range(n)]


def _load_values(path: str) -> list:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("values", []) if isinstance(data, dict) else data


def main(argv=None) -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("triage")
    t.add_argument("url")
    q = sub.add_parser("queue")
    q.add_argument("--log", required=True)
    q.add_argument("--history", required=True)
    q.add_argument("--max", type=int, default=config.get("max_applications_per_day", 10))
    q.add_argument("--repo", type=Path, default=REPO, help="checkout whose cv/ and cover_letters/ to search")
    q.add_argument("--skip-dry-ready", action="store_true", help="dry mode: skip rows already dry-run clean")
    q.add_argument("--companies", help="Companies tab dump (Grace Gong auto-apply gate)")
    q.add_argument("--company-cap", type=int, default=config.get("company_cap", 3))
    pc = sub.add_parser("postings-cap", help="Open Postings rows to keep/drop under the per-company rule")
    pc.add_argument("--postings", required=True)
    pc.add_argument("--log", required=True)
    pc.add_argument("--stop-at", type=int, default=config.get("company_stop_at", 2))
    pc.add_argument("--cap", type=int, default=config.get("company_cap", 3))
    b = sub.add_parser("qbank")
    b.add_argument("--values", required=True)
    d = sub.add_parser("delays")
    d.add_argument("--n", type=int, required=True)
    lo, hi = config.get("delay_between_apps_sec", [45, 120])
    d.add_argument("--min", type=float, default=lo)
    d.add_argument("--max", type=float, default=hi)
    hs = sub.add_parser("history-slot", help="row to overwrite for a link in Auto-Apply Runs, or 'append'")
    hs.add_argument("--history", required=True)
    hs.add_argument("--link", required=True)
    det = sub.add_parser("detect", help="AI-detector gate on a text file")
    det.add_argument("file")
    loc = sub.add_parser("location", help="current-location answer for a job location")
    loc.add_argument("job_location")
    loc.add_argument("--profile", default=str(Path.home() / ".auto-apply" / "profile.json"))
    args = ap.parse_args(argv)

    if args.cmd == "history-slot":
        slot = history_slot(_load_values(args.history), args.link)
        print(slot if slot else "append")
        return 0
    if args.cmd == "detect":
        return run_detector(args.file)
    if args.cmd == "location":
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
        print(location_for(args.job_location, profile))
        return 0
    if args.cmd == "triage":
        out = triage(args.url)
    elif args.cmd == "queue":
        out = build_queue(_load_values(args.log), _load_values(args.history), args.max, args.repo,
                          skip_portals=tuple(config.get("skip_portals", [])),
                          skip_dry_ready=args.skip_dry_ready,
                          companies_values=_load_values(args.companies) if args.companies else None,
                          company_cap=args.company_cap)
    elif args.cmd == "postings-cap":
        out = cap_postings(_load_values(args.postings), _load_values(args.log), args.stop_at, args.cap)
    elif args.cmd == "qbank":
        out = parse_question_bank(_load_values(args.values))
    else:
        out = delays(args.n, args.min, args.max)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
