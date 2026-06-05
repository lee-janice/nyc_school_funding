from src.analysis.descriptives_helpers import mean_by_category
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from adjustText import adjust_text   

RACE_COLS = {
    "p_white":      "White",
    "p_black":      "Black",
    "p_hispanic":   "Hispanic",
    "p_asian":      "Asian",
    "p_other_race": "Other Race",
}

RACE_COLS_ORDERED = ["White", "Black", "Hispanic", "Asian", "Other Race"]

RACE_COLORS = {
    "Black":       "#2166ac",
    "Hispanic":    "#92c5de",
    "Other Race":  "#878787",
    "Asian":       "#f4a582",
    "White":       "#d6604d",
}

QUINTILE_COLORS = {
    "Q1":  "#2166ac",
    "Q2":  "#92c5de",
    "Q3":  "#878787",
    "Q4":  "#f4a582",
    "Q5":  "#d6604d",
}

QUINTILE_LEGEND_LABELS = {
    "Q1": "Q1 (lowest need)",
    "Q2": "Q2",
    "Q3": "Q3",
    "Q4": "Q4",
    "Q5": "Q5 (highest need)",
}

# =============================================================================
#  PTA expenditure percentile plot
# =============================================================================
def plot_pta_expenditure_percentiles(
    df,
    expenditure_col="pp_pta_expenditure",
    category_col="pta_category",
    year_col="year",
    years=None,          
    highlight_pcts=None, # percentiles to annotate, e.g. [75, 90, 95, 99]
    save_path=None,
):
    # -----> filter data 
    active = df[
        (df[category_col] == "Active") 
    ].copy()

    if years is not None:
        active = active[active[year_col].isin(years)]

    # -----> compute percentile profile 
    pcts = np.arange(1, 100)  # 1st through 99th percentile
    values = np.percentile(active[expenditure_col].dropna(), pcts)

    # ------> build figure 
    fig, ax = plt.subplots(
        figsize=(8.5, 5.5),
        constrained_layout=True
    )

    ax.plot(
        pcts, values,
        color="#2166ac", linewidth=2.2, zorder=3
    )
    ax.fill_between(
        pcts, 0, values,
        alpha=0.10, color="#2166ac", zorder=2
    )

    # -----> highlight percentiles 
    if highlight_pcts is None:
        highlight_pcts = [75, 90, 95, 99]

    for p in highlight_pcts:
        v = np.percentile(active[expenditure_col].dropna(), p)
        ax.axvline(
            p, color="#d6604d", linewidth=1.2,
            linestyle="--", alpha=0.7, zorder=4
        )
        ax.text(
            p + 0.5, ax.get_ylim()[1] * 0.95,
            f"P{p}\n${v:,.0f}",
            fontsize=8, color="#d6604d", va="top"
        )

    # ----> formatting 
    ax.set_xlabel("Percentile rank of school", fontsize=11)
    ax.set_ylabel("Per-pupil PTA expenditure ($)", fontsize=11)
    ax.set_xlim(1, 99)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(
        mtick.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    # -----> add N and year info to subtitle 
    year_str = (
        "pooled 2019–2025" if years is None
        else "–".join(str(y) for y in sorted(years))
    )
    n = len(active)

    fig.suptitle(
        f"Per-pupil PTA expenditure by percentile rank\n"
        f"Active PTAs only — NYC Public Schools, Districts 1–32 "
        f"({year_str}, N={n:,})",
        fontsize=13, fontweight="bold"
    )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig, pcts, values  


# =============================================================================
#  School racial composition by PTA income quantile
# =============================================================================
def plot_racial_comp_by_pta_quantile(
    df,
    quantile_col = "pp_pta_expenditure_quintile",
    category_col = "pta_category",
    year_col="year",
    years=None,          
    save_path = None,
):
    # -----> aggregate and filter data 
    active = df[df[category_col] == "Active"].copy()

    if years is not None:
        active = active[active[year_col].isin(years)]
 
    plot_data = (
        mean_by_category(
            active,
            category_cols=[year_col, quantile_col],
            value_cols=["p_white", "p_black", "p_hispanic", "p_asian", "p_other_race"])
        .multiply(100)
        .round(1)
        .stack()
        .rename(columns=RACE_COLS)
        .reset_index()
    ) 

    plot_data = plot_data.set_index(quantile_col)

    x_labels = [str(q) for q in plot_data.index]
    x_pos    = np.arange(len(x_labels))

    # ----- build figure 
    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    bottoms = np.zeros(len(plot_data))

    for race in RACE_COLS_ORDERED:
        vals = plot_data[race].values  # already a 1D array, one value per quantile

        ax.bar(
            x_pos,
            vals,
            bottom=bottoms,
            color=RACE_COLORS[race],
            label=race,
            width=0.6,
            edgecolor="white",
            linewidth=0.8,
            alpha=0.8,
        )

        # label segments wider than 5%
        for i, (val, bot) in enumerate(zip(vals, bottoms)):
            if val > 5:
                ax.text(
                    i, bot + val / 2,
                    f"{val:.0f}%",
                    ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold"
                )

        bottoms += vals


    # ----- formatting 
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=30, ha="right")
    ax.set_xlabel("PTA income quantile", fontsize=11)
    ax.set_ylabel("Mean share of school enrollment (%)", fontsize=11)

    # -----> add N and year info to suptitle 
    year_str = (
        "pooled 2019–2025" if years is None
        else "–".join(str(y) for y in sorted(years))
    )
    n = len(active)

    fig.suptitle(
        f"Mean school racial composition by PTA income quantile\n"
        f"Active PTAs only — NYC Public Schools, Districts 1-32 "
        f"({year_str}, N={n:,})",
        fontsize=13, fontweight="bold"
    )

    ax.set_ylim(0, 105)  # headroom for labels
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    ax.legend(
        loc="upper center",
        ncol=5,
        frameon=False,
        fontsize=10,
        bbox_to_anchor=(0.5, -0.15),
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig


# =============================================================================
#  ENI vs. log(pp_pta_expenditure)
# =============================================================================
def plot_eni_vs_expenditure_scatter(
    df,
    year,
    eni_col = "eni_n",
    expenditure_col = "pp_pta_expenditure",
    quintile_col = "eni_quintile",
    category_col = "pta_category",
    save_path = None,
):
    active = df[
        (df["year"] == year) &
        (df[category_col] == "Active") &
        (df[expenditure_col] > 0)
    ].copy()

    active["log_expenditure"] = np.log(active[expenditure_col])

    fig, ax = plt.subplots(figsize=(10, 6))

    # -----> plot points by quintile 
    for quintile, color in QUINTILE_COLORS.items():
        subset = active[active[quintile_col] == quintile]
        ax.scatter(
            subset[eni_col],
            subset["log_expenditure"],
            color=color,
            label=QUINTILE_LEGEND_LABELS[quintile],
            alpha=0.45,
            s=25,
            edgecolors="none",
            zorder=3,
        )

    # -----> OLS trend line 
    x = active[eni_col].values
    y = active["log_expenditure"].values
    m, b = np.polyfit(x, y, deg=1)
    x_line = np.linspace(x.min(), x.max(), 200)
    ax.plot(
        x_line, m * x_line + b,
        color="black", linewidth=1.5,
        linestyle="--", alpha=0.6,
        label=f"OLS trend (slope={m:.2f})",
        zorder=4,
    )

    # -----> formatting 
    ax.set_xlabel("Economic Need Index")
    ax.set_ylabel("Log per-pupil PTA expenditure")

    # secondary y-axis labels showing raw dollar values
    # at round log values for interpretability
    log_ticks = ax.get_yticks()
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(log_ticks)
    ax2.set_yticklabels([
        f"${np.exp(t):,.0f}" if np.isfinite(t) else ""
        for t in log_ticks
    ], fontsize=8, color="#555555")
    ax2.set_ylabel("Per-pupil expenditure ($)", fontsize=9, color="#555555")

    ax.set_title(
        f"Economic need vs. PTA expenditure per pupil — {year}\n"
        f"Active PTAs with non-zero expenditures only — NYC Public Schools, Districts 1–32 (N={len(active):,})",
    )
    ax2.spines["top"].set_visible(False)

    ax.legend(frameon=False, fontsize=9, loc="lower left")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig


# =============================================================================
#  Annotated scatterplot
# =============================================================================
def plot_top_schools_annotated(
    df,
    year,
    school_name_col = "school_name",
    eni_col = "eni_n",
    expenditure_col = "pp_pta_expenditure",
    pct_fsf_col = "pta_expenditure_as_p_of_fsf",
    category_col = "pta_category",
    top_n = 15,
    save_path = None,
):
    active = df[
        (df["year"] == year) &
        (df[category_col] == "Active") 
    ].copy()

    #  -----> identify top N schools by pp expenditure
    top = active.nlargest(top_n, expenditure_col)
    rest = active[~active.index.isin(top.index)]

    # -----> color: above 15% FSF = dark red, below = dark blue
    # top["dot_color"] = top[pct_fsf_col].apply(
    #     lambda x: "#d6604d" if x >= 15 else "#2166ac"
    # )
    # # -----> color: anomaly flag
    # top["dot_color"] = top["anomaly_flag"].apply(
    #     lambda x: "#d6604d" if x else "#2166ac"
    # )

    fig, ax = plt.subplots(figsize=(9, 5))

    #  -----> background: all other active schools
    ax.scatter(
        rest[eni_col], rest[expenditure_col],
        color="#cccccc", alpha=0.3, s=15,
        edgecolors="none", zorder=2,
        label="All other active PTAs"
    )

    #  -----> top N schools
    for _, row in top.iterrows():
        ax.scatter(
            row[eni_col], row[expenditure_col],
            color="steelblue",
            alpha=0.85,
            edgecolors="white", linewidth=0.8,
            zorder=4,
        )

    # -----> labels with adjustText to avoid overlap
    texts = []
    for _, row in top.iterrows():
        pct_label = f"{row[pct_fsf_col]:.0f}% of FSF"
        texts.append(ax.text(
            row[eni_col], row[expenditure_col],
            f"{row[school_name_col]}\n({pct_label})",
            fontsize=7.5, color="#222222",
            ha="left", va="bottom",
        ))

    adjust_text(
        texts, ax=ax,
        arrowprops=dict(arrowstyle="-", color="#aaaaaa", lw=0.8),
        expand_points=(1.5, 1.5),
    )

    #  -----> reference line at median expenditure
    median_exp = active[expenditure_col].median()
    ax.axhline(
        median_exp, color="#555555", linewidth=1.0,
        linestyle=":", alpha=0.6, zorder=1
    )
    ax.text(
        0.98, median_exp,
        f"Median: ${median_exp:,.0f}",
        transform=ax.get_yaxis_transform(),
        fontsize=8, color="#555555",
        ha="right", va="bottom"
    )


    #  -----> formatting 
    ax.set_xlabel("Economic Need Index", fontsize=11)
    ax.set_ylabel("Per-pupil PTA expenditure ($)", fontsize=11)
    ax.yaxis.set_major_formatter(
        mtick.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    ax.set_title(
        f"Top {top_n} schools by per-pupil PTA expenditure — {year}\n"
        f"Active PTAs only — NYC Public Schools, Districts 1–32"
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig