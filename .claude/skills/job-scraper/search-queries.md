# Search Queries for Job Scraper

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search` (both enabled by default - good fit for a US market search). The Danish portal demos (Jobindex, Jobbank, Jobdanmark, Jobnet) ship disabled and stay disabled - not relevant to a US-based search. You do **not** need a matching `site:` line below for CLI-covered portals to run.

The `site:` query templates in this file are the **WebSearch fallback** - for portals without a CLI, company career pages, or when a CLI fails.

**Language scope:** English only (see CLAUDE.md Languages table). No translation needed.

## Search Sites

Primary:
- **linkedin.com/jobs** - also covered by `linkedin-search` CLI
- **Handshake** (handshake.com) - university career platform, strong for internships; no CLI yet, use WebSearch fallback
- Also covered by `freehire-search` CLI

Secondary (company career pages via Google):
- Direct Google searches with `site:` filters for known target companies (see Target Sectors in CLAUDE.md: SpaceX, Blue Origin, Boeing, Northrop Grumman, Lockheed Martin, Sierra Space, Relativity Space, Firefly Aerospace, Anduril, GE Aerospace, Collins Aerospace, Honeywell Aerospace, Caterpillar, John Deere)

## Query Categories

Queries are grouped by priority. Every category should include the keywords "intern", "summer 2027", and "engineering" as the candidate specified - combine with role-specific terms below rather than searching those keywords alone.

**Organize by function, not job title.** The same underlying work carries different titles across companies (e.g. "Manufacturing Engineering Intern" vs. "Manufacturing Engineer Co-op").

### Priority 1: Aerospace & Mechanical Engineering Internships

The candidate's strongest and most desired career direction.

```
site:linkedin.com/jobs "aerospace engineering intern" "summer 2027"
site:linkedin.com/jobs "mechanical engineering intern" "summer 2027"
"aerospace engineering intern" "summer 2027" engineering
"mechanical engineering intern" "summer 2027" engineering
"propulsion engineering intern" "summer 2027"
"structures engineering intern" "summer 2027"
```

### Priority 2: Manufacturing Engineering Internships

The candidate's second explicitly requested direction - direct fabrication/manufacturing experience (composites, CNC, laser cutting, 3D printing) applies here.

```
site:linkedin.com/jobs "manufacturing engineering intern" "summer 2027"
"manufacturing engineer intern" "summer 2027" engineering
"manufacturing engineering co-op" "summer 2027"
"process engineering intern" manufacturing "summer 2027"
```

### Priority 3: Controls / Embedded Engineering Internships (adjacent pivot)

Suggested based on the TVC Rocket project's controls/embedded-systems depth (PID control, sensor fusion, firmware) - worth casting this net alongside the primary aerospace/mechanical/manufacturing search.

```
"controls engineering intern" "summer 2027" engineering
"embedded systems engineering intern" "summer 2027"
"GNC engineering intern" "summer 2027"
"test engineering intern" aerospace "summer 2027"
```

### Priority 4: Broader Engineering Internships (wider net)

```
site:linkedin.com/jobs "engineering intern" "summer 2027" aerospace
site:linkedin.com/jobs "engineering intern" "summer 2027" mechanical
"engineering intern" "summer 2027" manufacturing
```

## Location Filter

Relocation is not a constraint for this candidate - internships anywhere in the US are in scope. No geographic tier restriction applies; do not filter out a posting for being far from Champaign, IL. Only filter on:
- **Must be in-person** (remote-only postings are a deal-breaker - see CLAUDE.md Deal-breakers)
- **Must be paid** (unpaid internships are a deal-breaker)

## Language Filter

English only - no Language Gate concerns for a US-market search.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. Given the "summer 2027" target, also include postings without a specific date if they are clearly part of an employer's Summer 2027 internship cycle. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape propulsion" -> Priority 1 queries + custom propulsion-specific queries
