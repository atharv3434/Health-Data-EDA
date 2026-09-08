"""Run the full EDA and generate a markdown report with embedded figures.

Usage:
    python src/generate_report.py [--config config.yaml]
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))
from utils import load_config, load_data
import eda


def build_report_markdown(df, config, summary, missing, outliers, corr, comparisons, fig_paths):
    n_rows, n_cols = df.shape
    lines = []
    lines.append("# Exploratory Data Analysis Report")
    lines.append("")
    lines.append(
        "> Generated automatically from synthetic patient health data. "
        "This dataset is randomly generated for demonstration purposes and "
        "does not represent real patients or real medical findings."
    )
    lines.append("")
    lines.append(f"**Rows:** {n_rows}  |  **Columns:** {n_cols}")
    lines.append("")

    lines.append("## Summary statistics")
    lines.append("")
    lines.append(summary.round(2).to_markdown())
    lines.append("")

    lines.append("## Missing values")
    lines.append("")
    if missing.empty:
        lines.append("No missing values found.")
    else:
        lines.append(missing.to_markdown())
    lines.append("")

    lines.append("## Outlier summary (IQR method)")
    lines.append("")
    lines.append(outliers.to_markdown())
    lines.append("")

    lines.append("## Distributions")
    lines.append("")
    lines.append(f"![Distributions]({os.path.basename(fig_paths['distributions'])})")
    lines.append("")

    lines.append("## Categorical variable counts")
    lines.append("")
    lines.append(f"![Categorical counts]({os.path.basename(fig_paths['categorical'])})")
    lines.append("")

    lines.append("## Correlations")
    lines.append("")
    lines.append(f"![Correlation heatmap]({os.path.basename(fig_paths['correlation'])})")
    lines.append("")
    strongest = (
        corr.where(~corr.abs().eq(1.0))
        .unstack()
        .dropna()
        .abs()
        .sort_values(ascending=False)
    )
    if not strongest.empty:
        top_pair = strongest.index[0]
        top_val = corr.loc[top_pair[0], top_pair[1]]
        lines.append(
            f"The strongest correlation is between **{top_pair[0]}** and "
            f"**{top_pair[1]}** (r = {top_val:.2f})."
        )
    lines.append("")

    lines.append("## Group comparisons")
    lines.append("")
    for comp in comparisons:
        if comp is None:
            continue
        keys = [k for k in comp if k.startswith("mean_")]
        means_str = ", ".join(f"{k.replace('mean_', '')} = {comp[k]}" for k in keys)
        sig = "statistically significant" if comp["significant_at_0.05"] else "not statistically significant"
        lines.append(
            f"- **{comp['value_col']}** by **{comp['group_col']}**: {means_str} "
            f"(t = {comp['t_stat']}, p = {comp['p_value']}, {sig} at α = 0.05)"
        )
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate an EDA report.")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    os.makedirs(config["figures_dir"], exist_ok=True)

    print(f"Loading data from {config['data_path']} ...")
    df = load_data(config["data_path"])
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.\n")

    numeric_cols = config["numeric_columns"]
    categorical_cols = config["categorical_columns"]

    print("Computing summary statistics...")
    summary = eda.summary_statistics(df, numeric_cols)

    print("Checking for missing values...")
    missing = eda.missing_value_report(df)

    print("Detecting outliers (IQR method)...")
    outliers = eda.outlier_summary(df, numeric_cols, multiplier=config.get("iqr_multiplier", 1.5))

    print("Plotting distributions...")
    dist_path = eda.plot_distributions(df, numeric_cols, config["figures_dir"])

    print("Plotting categorical counts...")
    cat_path = eda.plot_categorical_counts(df, categorical_cols, config["figures_dir"])

    print("Plotting correlation heatmap...")
    corr_path, corr = eda.plot_correlation_heatmap(df, numeric_cols, config["figures_dir"])

    print("Running group comparisons...")
    comparisons = []
    for spec in config.get("group_comparisons", []):
        result = eda.group_comparison(df, spec["group_col"], spec["value_col"])
        comparisons.append(result)

    fig_paths = {"distributions": dist_path, "categorical": cat_path, "correlation": corr_path}
    report_md = build_report_markdown(df, config, summary, missing, outliers, corr, comparisons, fig_paths)

    with open(config["report_path"], "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\nReport saved to {config['report_path']}")
    print(f"Figures saved to {config['figures_dir']}/")

    print("\n--- Quick summary ---")
    print(f"Missing values found in {len(missing)} column(s).")
    print(f"Outlier columns with >0 outliers: {(outliers['n_outliers'] > 0).sum()}")
    sig_count = sum(1 for c in comparisons if c and c["significant_at_0.05"])
    print(f"Group comparisons: {sig_count}/{len(comparisons)} statistically significant at 0.05")


if __name__ == "__main__":
    main()
