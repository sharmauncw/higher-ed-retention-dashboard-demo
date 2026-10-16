# Dashboard Spec — Retention Reporting Suite

**Audience:** Provost's office, deans, IR analysts
**Data source:** `retention_synthetic.csv` (student-term grain, see `data_dictionary.md`)
**Refresh cadence:** Nightly after the warehouse ETL completes
**All figures in this spec are synthetic.**

## Global filters (apply to every page)

- Entry cohort (multi-select, default: latest 3)
- College (multi-select, default: all)
- Admit type: First-time Freshman / Transfer
- First-gen status, Pell eligibility

## Page 1 — Executive Overview

**Audience:** Provost, vice provosts. **Decision it supports:** "Are we on track, and where do I look closer?"

| KPI card | Definition | Target / benchmark |
|---|---|---|
| Fall-to-fall retention | % of fall entrants enrolled the following fall | ≥ 82% |
| 6-yr graduation (proxy) | Modeled completion within 6 years of entry | ≥ 68% |
| DFW rate | % of student-terms with an unsuccessful course outcome | ≤ 12% |
| Equity gap (headline) | Largest retention gap vs. reference group | trending down |

Layout: 4 KPI cards across the top (each with YoY delta arrow), one trend line (retention by entry cohort, 5 years), one bar chart (retention by college, latest cohort). A text box auto-generates the "one thing to know" — the KPI with the largest adverse YoY move.

**Stakeholder note:** this page is the *only* page most executives open. Every number here must be explainable in one sentence. Drill-through goes to Page 2.

## Page 2 — Persistence & Retention

**Audience:** Deans, advising directors, IR analysts. **Decision it supports:** "Which cohorts and populations are losing students, and when?"

- **Persistence curve:** % still enrolled by term number (1–6), one line per entry cohort. The steepest drop (typically term 1→2) is annotated.
- **Heatmap:** retention by college × admit type for the latest cohort.
- **Stop-out vs. drop-out:** of non-returning students, % who re-enroll within 2 terms (stop-outs) vs. not — stop-outs are a re-engagement opportunity, not a loss.
- **Drill-down:** click a college → student list (synthetic IDs only) with term GPA and credits earned for advisor outreach review.

**Stakeholder note:** term 1→2 attrition is the highest-leverage intervention point. Advising leadership owns this page's action items.

## Page 3 — Equity Gaps

**Audience:** Chief diversity officer, student success leadership. **Decision it supports:** "Where are outcome gaps largest, and are they closing?"

- **Gap chart:** retention rate by group (first-gen, Pell-eligible, URM status) vs. reference group, with the gap in percentage points labeled on every bar.
- **Trend:** gap size over the last 5 cohorts — "closing," "flat," or "widening" badge per group.
- **Intersection view:** e.g., first-gen × Pell-eligible, to avoid masking compounded disadvantage.
- **Plain-language callouts:** auto-text like "The first-gen gap narrowed 2.1 pts since 2021, driven by term-1 persistence gains." No jargon, no unexplained acronyms.

**Stakeholder note:** gaps are reported as *differences vs. reference group*, never as deficits of the group. Language matters in governance settings.

## Page 4 — Technical QA

**Audience:** IR analysts, data engineering. **Decision it supports:** "Can we trust what leadership is seeing?"

- **Freshness:** warehouse load timestamp, rows loaded vs. expected, "data as of" date.
- **Reconciliation:** dashboard cohort headcount vs. official census count — must match within ±0.5% or the page shows a blocking banner.
- **Null-rate monitors:** % nulls on key fields (`term_gpa`, `credits_earned`, `college`) with 30-day trend; alert threshold at 2× baseline.
- **Model QA (if a risk model is connected):** population stability index (PSI) by term, calibration curve, and precision/recall at the deployed threshold. If PSI > 0.25, the risk scores are suppressed from Pages 1–3 until revalidated.

**Stakeholder note:** this page is the reason executives trust the other three. QA failures page the analyst, not the provost.

## Build checklist (for the BI developer)

- [ ] One flat table at student-term grain; no snowflaking in the semantic model.
- [ ] All rate measures use `DIVIDE(numerator, denominator)`-style safe division.
- [ ] Cohort is *entry* cohort everywhere — never re-derive it from the latest term.
- [ ] Synthetic watermark on every page ("SYNTHETIC DEMO DATA") until pointed at production.
- [ ] Row-level security plan documented before go-live (advisor sees own caseload only).
