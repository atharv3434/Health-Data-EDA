# Health Data EDA

An exploratory data analysis project built on **pandas**, **numpy**,
**matplotlib/seaborn**, and **scipy**. Ships with a synthetic patient health
dataset (age, BMI, blood pressure, cholesterol, glucose, smoking status,
exercise, hypertension) with realistic statistical relationships baked in,
so you can see a full EDA workflow run end to end immediately.

> **Synthetic data, for demonstration only.** `patient_health_data.csv` is
> randomly generated — it does not represent real patients, and nothing in
> the generated report is a real medical finding. This project is a
> template for practicing/running EDA, not a clinical tool.

## Project structure

```
health-data-eda/
├── config.yaml                     # which columns to analyze, comparisons to run
├── requirements.txt
├── data/
│   ├── generate_data.py            # (re)generates the synthetic dataset
│   └── patient_health_data.csv     # pre-generated sample data
├── src/
│   ├── utils.py                    # config + data loading
│   ├── eda.py                      # summary stats, plots, outliers, group tests
│   └── generate_report.py          # CLI: runs everything, writes the report
├── output/
│   ├── figures/                    # PNG charts land here
│   └── eda_report.md               # full markdown report
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Run it

```bash
python src/generate_report.py
```

This loads the data and produces:

- **`output/eda_report.md`** — a full markdown report: summary statistics,
  missing-value breakdown, an IQR-based outlier summary, distribution plots,
  categorical counts, a correlation heatmap, and group comparisons (with
  t-tests) between e.g. smokers vs. non-smokers.
- **`output/figures/`** — the individual PNG charts referenced in the report:
  `distributions.png`, `categorical_counts.png`, `correlation_heatmap.png`.

A summary also prints to the console:

```
Missing values found in 3 column(s).
Outlier columns with >0 outliers: 6
Group comparisons: 4/4 statistically significant at 0.05
```

## What it analyzes

- **Summary statistics** — count, mean, std, quartiles for every numeric column
- **Missing values** — which columns have gaps, and what percentage
- **Outliers** — detected with the IQR method (via `numpy.percentile`),
  reporting bounds and how many values fall outside them
- **Distributions** — histogram + KDE for every numeric column
- **Categorical counts** — bar charts for sex, smoker status, hypertension
- **Correlations** — a heatmap across all numeric variables, with the
  strongest pair called out automatically
- **Group comparisons** — mean differences between two groups (e.g. smokers
  vs. non-smokers) with an independent two-sample t-test (`scipy.stats.ttest_ind`)

## Using your own data

1. Replace `data/patient_health_data.csv` with your own CSV.
2. Update `config.yaml`:
   - `numeric_columns` / `categorical_columns` to match your schema
   - `group_comparisons` to whichever binary-group vs. numeric-value
     comparisons you care about
3. Re-run `python src/generate_report.py`.

To regenerate a fresh synthetic sample instead:

```bash
python data/generate_data.py --n 1000 --seed 7
```

## Extending this project

- **More group comparisons**: add entries to `group_comparisons` in
  `config.yaml` — no code changes needed.
- **Categorical-vs-categorical tests**: add a chi-square test function to
  `eda.py` (via `scipy.stats.chi2_contingency`) alongside `group_comparison`.
- **Interactive exploration**: the functions in `eda.py` are plain
  DataFrame-in, DataFrame/dict-out, so they drop straight into a Jupyter
  notebook if you'd rather explore interactively than run the CLI.
