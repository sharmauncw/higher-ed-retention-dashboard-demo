# Data Dictionary — `retention_synthetic.csv`

Grain: **one row per student per enrolled term.** All values synthetic.

| Field | Type | Description |
|---|---|---|
| `student_id` | string | Synthetic key, format `SYN-000001`. Stable across terms. |
| `entry_cohort` | int | Fall entry year (2021–2023). Never re-derived downstream. |
| `term` | string | Label, e.g. `Fall 2021`. |
| `term_number` | int | 1–6, sequential from entry. Use for persistence curves. |
| `college` | string | Synthetic college of enrollment. |
| `admit_type` | string | `First-time Freshman` or `Transfer`. |
| `first_gen` | string | `Yes` / `No` (synthetic). |
| `pell_eligible` | string | `Yes` / `No` (synthetic). |
| `urm_status` | string | `URM` / `Non-URM` (synthetic flag for equity-gap demos only). |
| `hs_gpa_band` | string | High-school GPA band (synthetic). |
| `term_gpa` | float | Term GPA, 0.00–4.00 (synthetic, roughly normal around 3.0). |
| `credits_attempted` | int | Credits attempted that term. |
| `credits_earned` | int | Credits earned (attempted minus synthetic unsuccessful outcomes). |
| `dfw_flag` | bool | Synthetic "unsuccessful course outcome" proxy for the term. |
| `enrolled` | bool | Always true (only enrolled terms are emitted). |
| `retained_next_term` | bool | Whether the student appears in the next term. |

## Known synthetic patterns (by design)

- Retention decays ~0.8 pts per term (stop-out model).
- First-gen, Pell-eligible, and URM students persist at slightly lower rates — this creates the equity gaps Page 3 visualizes. **These gaps are invented for the demo.**
- Students with `term_gpa < 2.5` have a higher `dfw_flag` rate.
- Transfer students persist slightly below first-time freshmen.

## What's intentionally NOT modeled

- Summer terms, part-time trajectories, major changes, or re-admits.
- Any real institution's actual rates — do not cite these numbers as benchmarks.
