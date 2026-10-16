#!/usr/bin/env python3
"""
generate_retention_data.py — Synthetic higher-education retention dataset generator.

Creates a clearly SYNTHETIC student-term grain table suitable for prototyping
retention dashboards. No real students, no real institution. All patterns
(retention decay, equity gaps, DFW rates) are plausible but invented.

Usage:
    python generate_retention_data.py --seed 42 --n-students 5000 --terms 6 \
        --out data/retention_synthetic.csv

Dependencies: pandas, numpy
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def build_students(n_students: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate one row per synthetic student with entry-cohort attributes."""
    cohorts = rng.choice([2021, 2022, 2023], size=n_students, p=[0.32, 0.34, 0.34])
    colleges = rng.choice(
        ["Arts & Sciences", "Business", "Engineering", "Health & Human Services", "Education"],
        size=n_students, p=[0.35, 0.22, 0.18, 0.15, 0.10],
    )
    df = pd.DataFrame({
        "student_id": [f"SYN-{i:06d}" for i in range(1, n_students + 1)],
        "entry_cohort": cohorts,
        "college": colleges,
        "admit_type": rng.choice(["First-time Freshman", "Transfer"], size=n_students, p=[0.78, 0.22]),
        "first_gen": rng.choice(["Yes", "No"], size=n_students, p=[0.34, 0.66]),
        "pell_eligible": rng.choice(["Yes", "No"], size=n_students, p=[0.31, 0.69]),
        # Synthetic demographic flag for equity-gap analysis. Values are
        # invented and carry no real-world meaning beyond the demo.
        "urm_status": rng.choice(["URM", "Non-URM"], size=n_students, p=[0.28, 0.72]),
        "hs_gpa_band": rng.choice(["<2.75", "2.75-3.24", "3.25-3.74", "3.75+"], size=n_students,
                                  p=[0.12, 0.28, 0.35, 0.25]),
    })
    return df


def expand_terms(students: pd.DataFrame, n_terms: int, rng: np.random.Generator) -> pd.DataFrame:
    """Expand to student-term grain; simulate enrollment, GPA, DFW, and retention."""
    rows = []
    for _, s in students.iterrows():
        # Baseline persistence probability shaped by synthetic risk factors.
        base = 0.94
        if s["first_gen"] == "Yes":
            base -= 0.03
        if s["pell_eligible"] == "Yes":
            base -= 0.02
        if s["urm_status"] == "URM":
            base -= 0.025
        if s["hs_gpa_band"] == "<2.75":
            base -= 0.05
        elif s["hs_gpa_band"] == "3.75+":
            base += 0.02
        if s["admit_type"] == "Transfer":
            base -= 0.015

        enrolled = True
        for term_num in range(1, n_terms + 1):
            if not enrolled:
                break
            # Term label like "Fall 2021", "Spring 2022", ...
            year = int(s["entry_cohort"]) + (term_num - 1) // 2
            season = "Fall" if term_num % 2 == 1 else "Spring"
            term = f"{season} {year}"

            term_gpa = float(np.clip(rng.normal(3.0, 0.65), 0.0, 4.0))
            credits_attempted = int(rng.choice([12, 13, 14, 15, 16, 18],
                                              p=[0.08, 0.12, 0.22, 0.30, 0.20, 0.08]))
            # DFW-ish flag: synthetic "unsuccessful course outcome" proxy.
            dfw_flag = bool(rng.random() < (0.16 if term_gpa < 2.5 else 0.06))
            credits_earned = credits_attempted - (3 if dfw_flag and rng.random() < 0.7 else 0)

            rows.append({
                "student_id": s["student_id"],
                "entry_cohort": s["entry_cohort"],
                "term": term,
                "term_number": term_num,
                "college": s["college"],
                "admit_type": s["admit_type"],
                "first_gen": s["first_gen"],
                "pell_eligible": s["pell_eligible"],
                "urm_status": s["urm_status"],
                "hs_gpa_band": s["hs_gpa_band"],
                "term_gpa": round(term_gpa, 2),
                "credits_attempted": credits_attempted,
                "credits_earned": credits_earned,
                "dfw_flag": dfw_flag,
                "enrolled": True,
            })
            # Persistence to next term decays slightly each term (stop-out model).
            persist_p = base - 0.008 * term_num
            enrolled = bool(rng.random() < persist_p)

    df = pd.DataFrame(rows)
    # Retained flag: enrolled in the following term (fall-to-fall style logic
    # can be derived downstream from term_number).
    df["retained_next_term"] = df.groupby("student_id")["term_number"].transform(
        lambda x: x < x.max()
    )
    return df


def summarize(df: pd.DataFrame) -> None:
    n_students = df["student_id"].nunique()
    overall_retention = df["retained_next_term"].mean()
    dfw_rate = df["dfw_flag"].mean()
    gap = (df.loc[df["urm_status"] == "Non-URM", "retained_next_term"].mean()
           - df.loc[df["urm_status"] == "URM", "retained_next_term"].mean())
    print(f"Students (synthetic): {n_students:,}")
    print(f"Student-term rows:    {len(df):,}")
    print(f"Overall retention:    {overall_retention:.1%}")
    print(f"DFW rate:             {dfw_rate:.1%}")
    print(f"URM retention gap:    {gap:.1%} (synthetic, for demo only)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic retention data.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-students", type=int, default=5000)
    parser.add_argument("--terms", type=int, default=6)
    parser.add_argument("--out", type=str, default="data/retention_synthetic.csv")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    students = build_students(args.n_students, rng)
    df = expand_terms(students, args.terms, rng)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    print(f"Wrote {out} ({len(df):,} rows)")
    summarize(df)


if __name__ == "__main__":
    main()
