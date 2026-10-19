"""Generate synthetic retention prediction data for dashboard demos.

This script creates fake student-like records for public portfolio use. It does not
use institutional data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_FILE = OUTPUT_DIR / "synthetic_retention_predictions.csv"


def build_dataset(row_count: int = 3000, seed: int = 20260603) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    colleges = [
        "College of Science and Engineering",
        "College of Health and Human Services",
        "School of Business",
        "College of Humanities, Social Sciences, and the Arts",
        "College of Education",
        "Center for Academic Advising",
    ]

    df = pd.DataFrame(
        {
            "student_key": [f"SYN{idx:05d}" for idx in range(1, row_count + 1)],
            "cohort_year": 2025,
            "major_college": rng.choice(
                colleges, size=row_count, p=[0.28, 0.23, 0.21, 0.13, 0.06, 0.09]
            ),
            "spring_total_sch": rng.normal(12.5, 3.5, row_count).clip(0, 18).round(1),
            "spring_pass_rate": rng.beta(8, 2, row_count).round(3),
            "spring_failed": rng.poisson(0.35, row_count),
            "fall_failed": rng.poisson(0.28, row_count),
            "fall_withdrew": rng.poisson(0.18, row_count),
            "pell": rng.binomial(1, 0.32, row_count),
            "on_campus": rng.binomial(1, 0.58, row_count),
        }
    )

    risk_score = (
        1.8
        - 0.12 * df["spring_total_sch"]
        - 2.4 * df["spring_pass_rate"]
        + 0.55 * df["spring_failed"]
        + 0.35 * df["fall_failed"]
        + 0.25 * df["fall_withdrew"]
        + 0.18 * df["pell"]
        - 0.12 * df["on_campus"]
        + rng.normal(0, 0.35, row_count)
    )
    retention_probability = 1 / (1 + np.exp(risk_score))
    df["retention_probability"] = retention_probability.round(4)
    df["predicted_label"] = np.where(
        df["retention_probability"] >= 0.50,
        "Predicted Retained",
        "Predicted Not Retained",
    )

    df["risk_percentile"] = df["retention_probability"].rank(pct=True, ascending=True)
    df["risk_flag"] = pd.qcut(
        df["risk_percentile"],
        q=4,
        labels=["HIGH RISK", "MODERATE RISK", "LOW RISK", "LIKELY RETAINED"],
    )
    df["top_10pct_risk"] = df["risk_percentile"] <= 0.10
    df["top_25pct_risk"] = df["risk_percentile"] <= 0.25

    return df


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = build_dataset()
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(df):,} synthetic rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

