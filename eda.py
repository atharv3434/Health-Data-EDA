"""Core exploratory data analysis functions: summary stats, missing-value
reporting, distribution/correlation plots, outlier detection, and simple
group comparisons with a t-test.

Every function returns plain data (DataFrames, dicts) rather than printing
directly, so generate_report.py can both display results and write them
into the markdown report.
"""

import os

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")


def summary_statistics(df, numeric_columns):
    """Descriptive statistics (count, mean, std, quartiles, etc.) for numeric columns."""
    return df[numeric_columns].describe().T


def missing_value_report(df):
    """Count and percentage of missing values per column."""
    missing = df.isna().sum()
    pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({"missing_count": missing, "missing_pct": pct})
    return report[report["missing_count"] > 0].sort_values("missing_count", ascending=False)


def outlier_summary(df, numeric_columns, multiplier=1.5):
    """IQR-based outlier counts per numeric column, computed with numpy."""
    rows = []
    for col in numeric_columns:
        values = df[col].to_numpy(dtype="float64")
        finite = values[~np.isnan(values)]
        if finite.size == 0:
            continue
        q1, q3 = np.percentile(finite, [25, 75])
        iqr = q3 - q1
        lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
        outliers = ((values < lower) | (values > upper)) & ~np.isnan(values)
        rows.append({
            "column": col,
            "lower_bound": round(float(lower), 2),
            "upper_bound": round(float(upper), 2),
            "n_outliers": int(outliers.sum()),
            "pct_outliers": round(float(outliers.sum()) / finite.size * 100, 2),
        })
    return pd.DataFrame(rows).set_index("column")


def plot_distributions(df, numeric_columns, figures_dir):
    """Grid of histograms (with KDE) for each numeric column."""
    n = len(numeric_columns)
    ncols = 3
    nrows = -(-n // ncols)  # ceil division
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3.5 * nrows))
    axes = np.array(axes).reshape(-1)

    for ax, col in zip(axes, numeric_columns):
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#3B6E8F")
        ax.set_title(col)
        ax.set_xlabel("")

    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle("Distributions of numeric variables", fontsize=14)
    fig.tight_layout()
    path = os.path.join(figures_dir, "distributions.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_correlation_heatmap(df, numeric_columns, figures_dir):
    """Correlation heatmap across numeric columns."""
    corr = df[numeric_columns].corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax, vmin=-1, vmax=1)
    ax.set_title("Correlation between numeric variables")
    fig.tight_layout()
    path = os.path.join(figures_dir, "correlation_heatmap.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path, corr


def plot_categorical_counts(df, categorical_columns, figures_dir):
    """Bar chart of value counts for each categorical column."""
    n = len(categorical_columns)
    fig, axes = plt.subplots(1, n, figsize=(4.5 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, categorical_columns):
        counts = df[col].value_counts().sort_index()
        sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax, color="#8C5E58")
        ax.set_title(col)
        ax.set_ylabel("Count")

    fig.tight_layout()
    path = os.path.join(figures_dir, "categorical_counts.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def group_comparison(df, group_col, value_col):
    """Compare `value_col` between the two groups of a binary `group_col`,
    reporting group means and an independent two-sample t-test.
    """
    groups = sorted(df[group_col].dropna().unique())
    if len(groups) != 2:
        return None

    g0 = df.loc[df[group_col] == groups[0], value_col].dropna()
    g1 = df.loc[df[group_col] == groups[1], value_col].dropna()

    t_stat, p_value = stats.ttest_ind(g0, g1, equal_var=False)

    return {
        "group_col": group_col,
        "value_col": value_col,
        f"mean_{group_col}_{groups[0]}": round(float(g0.mean()), 2),
        f"mean_{group_col}_{groups[1]}": round(float(g1.mean()), 2),
        "t_stat": round(float(t_stat), 3),
        "p_value": round(float(p_value), 4),
        "significant_at_0.05": bool(p_value < 0.05),
    }
