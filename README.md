# Higher-Ed Retention Dashboard Demo

A synthetic higher-education retention dashboard demo with model QA and a stakeholder reporting structure. Everything in this repo runs on **clearly synthetic data** — no real student records, no real institution.

Built as a portfolio piece demonstrating how an institutional research analyst would design, document, and QA a retention reporting suite before it ever touches production data.

## What's inside

| Path | Description |
|---|---|
| `generate_retention_data.py` | Seeded Python script that generates a synthetic student-term dataset (pandas). Reproducible via `--seed`. |
| `dashboard_spec.md` | Full dashboard specification: 4 pages, KPIs, filters, layouts, and stakeholder notes. |
| `data_dictionary.md` | Field-level documentation for the synthetic dataset. |

## Quickstart

```bash
pip install pandas numpy
python generate_retention_data.py --seed 42 --n-students 5000 --terms 6 --out data/retention_synthetic.csv
```

The generator prints a summary (cohort size, overall retention rate, DFW rate) so you can sanity-check the output immediately.

## The 4 dashboard pages

1. **Executive Overview** — headline KPIs for leadership: fall-to-fall retention, 6-year graduation proxy, DFW rate, equity gap headline.
2. **Persistence & Retention** — term-to-term persistence curves by entry cohort, with drill-downs by college, admit type, and first-gen status.
3. **Equity Gaps** — disaggregated outcomes (Pell-eligible, first-gen, URM status) with gap-vs-reference-group calculations and plain-language callouts.
4. **Technical QA** — the analyst's page: data freshness, row-count reconciliation vs. the warehouse, null-rate monitors, and model QA metrics (only shown if a risk model is connected).

See `dashboard_spec.md` for the complete spec an actual BI developer could build from.

## Design principles

- **Synthetic-first:** every number is generated, seeded, and labeled synthetic. The patterns (retention curves, equity gaps) are realistic; the students are not.
- **Stakeholder-aware:** each page names its audience and the decision it supports. No vanity metrics.
- **QA is a first-class page:** if leadership can't see data quality, they can't trust the dashboard.

## Tech notes

- Python 3.9+, `pandas`, `numpy` only — no heavy dependencies.
- The generator uses a fixed RNG seed by default so results are reproducible and reviewable.
- Designed to feed Power BI / Tableau: one flat `student_term` grain table, documented in `data_dictionary.md`.
