"""Generate a synthetic patient health dataset for EDA practice.

This project ships with pre-generated data already in place
(data/patient_health_data.csv), so you don't need to run this to try the
project out. Run it again for a fresh random sample, a different size, or a
different seed.

IMPORTANT: This data is entirely synthetic (randomly generated with
plausible statistical relationships) — it does not represent real patients
and must not be treated as medical fact.

Usage:
    python data/generate_data.py [--n 500] [--seed 42] [--out data/patient_health_data.csv]
    
"""

import argparse
import numpy as np
import pandas as pd


def generate_patients(n=500, seed=42):
    rng = np.random.default_rng(seed)

    age = rng.integers(18, 91, size=n)
    sex = rng.choice(["M", "F"], size=n)
    smoker = rng.choice([0, 1], size=n, p=[0.78, 0.22])

    # BMI: baseline + mild age effect + noise
    bmi = 23 + 0.04 * age + rng.normal(0, 4.0, size=n)
    bmi = np.clip(bmi, 15, 55)

    # Exercise: inversely related to BMI, with noise
    exercise_hours_per_week = np.clip(6 - 0.08 * (bmi - 23) + rng.normal(0, 2.0, size=n), 0, 20)

    # Blood pressure: rises with age, BMI, and smoking
    systolic_bp = (
        95
        + 0.35 * age
        + 0.9 * (bmi - 23)
        + 6 * smoker
        + rng.normal(0, 8, size=n)
    )
    diastolic_bp = (
        60
        + 0.15 * age
        + 0.5 * (bmi - 23)
        + 3 * smoker
        + rng.normal(0, 6, size=n)
    )

    # Cholesterol: rises with age and BMI
    cholesterol = (
        160
        + 0.9 * age
        + 1.1 * (bmi - 23)
        + 10 * smoker
        + rng.normal(0, 20, size=n)
    )

    # Glucose: rises with BMI, mild age effect
    glucose = (
        85
        + 0.5 * (bmi - 23)
        + 0.1 * age
        + rng.normal(0, 10, size=n)
    )

    # Hypertension flag: derived from BP thresholds plus some noise, so it's
    # a realistic (not perfectly deterministic) downstream label.
    hypertension_risk = (systolic_bp >= 135) | (diastolic_bp >= 85)
    flip = rng.random(n) < 0.05
    hypertension = np.where(flip, ~hypertension_risk, hypertension_risk).astype(int)

    df = pd.DataFrame({
        "patient_id": [f"P{1000 + i}" for i in range(n)],
        "age": age,
        "sex": sex,
        "bmi": np.round(bmi, 1),
        "smoker": smoker,
        "exercise_hours_per_week": np.round(exercise_hours_per_week, 1),
        "systolic_bp": np.round(systolic_bp, 0).astype(int),
        "diastolic_bp": np.round(diastolic_bp, 0).astype(int),
        "cholesterol": np.round(cholesterol, 0).astype(int),
        "glucose": np.round(glucose, 0).astype(int),
        "hypertension": hypertension,
    })

    # Sprinkle in some realistic missingness (labs not always drawn/recorded)
    for col, frac in [("bmi", 0.03), ("cholesterol", 0.06), ("glucose", 0.05)]:
        mask = rng.random(n) < frac
        df.loc[mask, col] = np.nan

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic patient health data.")
    parser.add_argument("--n", type=int, default=500, help="Number of patient records")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", default="data/patient_health_data.csv", help="Output CSV path")
    args = parser.parse_args()

    df = generate_patients(n=args.n, seed=args.seed)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} synthetic patient records to {args.out}")


if __name__ == "__main__":
    main()
