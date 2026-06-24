from src.analysis.descriptives_helpers import mean_by_category
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns 
from adjustText import adjust_text   

RACE_COLS = {
    "p_white":      "White",
    "p_black":      "Black",
    "p_hispanic":   "Hispanic",
    "p_asian":      "Asian",
    "p_other_race": "Other Race",
}

RACE_COLS_ORDERED = ["White", "Asian", "Black", "Hispanic", "Other Race"]

RACE_COLORS = {
    "Black":       "#2166ac",
    "Hispanic":    "#92c5de",
    "Other Race":  "#878787",
    "Asian":       "#f4a582",
    "White":       "#d6604d",
}

FUNDING_COLS = {
    "pp_fsf":             "Per-pupil FSF allocations",
    "pp_non_fsf":         "Per-pupil non-FSF allocations",
    "pp_pta_expenditure": "Per-pupil PTA expenditure",
}

FUNDING_COLS_ORDERED = ["Per-pupil FSF allocations", "Per-pupil non-FSF allocations", "Per-pupil PTA expenditure"]

FUNDING_COLORS = {
    "Per-pupil FSF allocations":        "#2166ac",
    "Per-pupil non-FSF allocations":    "#f4a582",
    "Per-pupil PTA expenditure":        "#d6604d",
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
# TODO: make sure to update pipeline to handle any dataset, not restricted to just Active PTA 
def plot_pta_expenditure_percentiles(
    df,
    expenditure_col="pp_pta_expenditure",
    category_col="pta_category",
    year_col="year",
    years=None,          
    title="", 
    subtitle="", 
    highlight_pcts=None, # percentiles to annotate, e.g. [75, 90, 95, 99]
    save_path=None,
):
    # -----> filter data 
    if years is not None:
        df = df[df[year_col].isin(years)]

    # -----> compute percentile profile 
    pcts = np.arange(1, 100)  # 1st through 99th percentile
    values = np.percentile(df[expenditure_col].dropna(), pcts)

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
        v = np.percentile(df[expenditure_col].dropna(), p)
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
    n = len(df)

    fig.suptitle(
        f"{title}\n"
        f"{subtitle} "
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
    title="", 
    subtitle="", 
    save_path = None,
):
    # -----> aggregate and filter data 
    # active = df[df[category_col] == "Active"].copy()

    if years is not None:
        df = df[df[year_col].isin(years)]
 
    plot_data = (
        mean_by_category(
            df,
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
    ax.set_xlabel("PTA funding quantile", fontsize=11)
    ax.set_ylabel("Mean share of school enrollment (%)", fontsize=11)

    # -----> add N and year info to suptitle 
    year_str = (
        "pooled 2019–2025" if years is None
        else "–".join(str(y) for y in sorted(years))
    )
    n = len(df)

    fig.suptitle(
        f"{title}"
        f"{subtitle} "
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
#  ENI vs. finance column
# =============================================================================
def plot_eni_vs_finance_scatter(
    df,
    year,
    finance_col,
    ylabel,
    ylog=True,
    eni_col="eni_n",
    quintile_col="eni_quintile",
    show_ols=True,
    title="",
    subtitle="",
    legend_loc="lower left",
    save_path = None,
):
    df = df[(df["year"] == year)]

    if ylog:
        df[finance_col] = np.log(df[finance_col])

    fig, ax = plt.subplots(figsize=(10, 6))

    # -----> plot points by quintile 
    for quintile, color in QUINTILE_COLORS.items():
        subset = df[df[quintile_col] == quintile]
        ax.scatter(
            subset[eni_col],
            subset[finance_col],
            color=color,
            label=QUINTILE_LEGEND_LABELS[quintile],
            alpha=0.45,
            s=25,
            edgecolors="none",
            zorder=3,
        )

    # -----> OLS trend line 
    if show_ols:
        x = df[eni_col].values
        y = df[finance_col].values
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
    ax.set_ylabel(ylabel)

    ax.set_title(
        f"{title}"
        f"{subtitle} "
        f"({year}, N={len(df):,})\n",
    )

    ax.legend(frameon=False, fontsize=9, loc=legend_loc)

    plt.tight_layout()

    if ylog:
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())

        log_ticks = sorted(set(ax.get_yticks().tolist()))

        ax2.set_yticks(log_ticks)
        ax2.set_yticklabels([
            f"${np.exp(t):,.0f}" if np.isfinite(t) else ""
            for t in log_ticks
        ], fontsize=8, color="#555555")
        ax2.set_ylabel("Raw dollar values", fontsize=9, color="#555555")
        ax2.spines["top"].set_visible(False)

        # set this LAST, after any layout calls, right before save/show
        ax2.set_ylim(ax.get_ylim())

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
    title = "",
    subtitle = "", 
    top_n = 15,
    save_path = None,
):
    df = df[(df["year"] == year)].copy()

    #  -----> identify top N schools by pp expenditure
    top = df.nlargest(top_n, expenditure_col)
    rest = df[~df.index.isin(top.index)]

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
        # label="All other active PTAs"
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
    median_exp = df[expenditure_col].median()
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

    n = len(df)
    ax.set_title(
        f"Top {top_n} schools by per-pupil PTA expenditure\n"
        f"{subtitle} "
        f"({year}, N={n:,})\n"
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig


# =============================================================================
#  Stacked histogram of PTA expenditure, FSF, and non-FSF allocations
# =============================================================================
def plot_funding_stacked(
    df,
    year=None,          
    funding_cols=["pp_fsf", "pp_non_fsf", "pp_pta_expenditure"],
    quantile_col="eni_quintile",
    title="", 
    subtitle="", 
    save_path = None,
):
    df = df[df["year"] == year]

    plot_data = (
        mean_by_category(
            df,
            category_cols=[quantile_col],
            value_cols=funding_cols)
        .round(1)
        .unstack(level=0)
        .rename(columns=FUNDING_COLS)
        .reset_index()
    ) 

    plot_data = plot_data.set_index(quantile_col)

    x_labels = [str(q) for q in plot_data.index]
    x_pos    = np.arange(len(x_labels))

    # ----- build figure 
    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    bottoms = np.zeros(len(plot_data))

    for f in FUNDING_COLS_ORDERED:
        vals = plot_data[f].values  # already a 1D array, one value per quantile

        ax.bar(
            x_pos,
            vals,
            bottom=bottoms,
            color=FUNDING_COLORS[f],
            label=f,
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
                    f"{val:.0f}",
                    ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold"
                )

        bottoms += vals


    # ----- formatting 
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=30, ha="right")
    ax.set_xlabel("ENI quantile", fontsize=11)
    ax.set_ylabel("Mean dollar amount", fontsize=11)

    # -----> add N and year info to suptitle 
    n = len(df)
    fig.suptitle(
        f"{title}"
        f"{subtitle} "
        f"({year}, N={n:,})",
        fontsize=13, fontweight="bold"
    )

    # ax.set_ylim(0, 105)  # headroom for labels
    # ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_ylim(0, plot_data[FUNDING_COLS_ORDERED].sum(axis=1).max() * 1.1)

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
#  Dot plot of total funding
# =============================================================================
def plot_total_funding_dotplot(
    df,
    year=None,
    total_funding_col="pp_total_funding", 
    public_funding_col="pp_total_public",  
    pta_share_col="pta_expenditure_as_p_of_total", 
    quantile_col="eni_quintile",
    title="",
    subtitle="",
    save_path=None,
):
    df = df[df["year"] == year].copy()

    # -----> reference line: Q5 mean PUBLIC funding only
    q5_mean_public = df.loc[df[quantile_col] == "Q5", public_funding_col].mean()

    # -----> color and size mappings
    QUINTILE_COLORS = {
        "Q1": "#1f6bb0",
        "Q2": "#6aaed6",
        "Q3": "#999999",
        "Q4": "#f4a582",
        "Q5": "#d6604d",
    }

    # scale dot size by PTA share; schools with no PTA get minimum size
    size_scale = 30   # tweak to taste
    min_size   = 10
    sizes = df[pta_share_col].clip(lower=0) * size_scale + min_size

    colors = df[quantile_col].map(QUINTILE_COLORS)

    # -----> jitter x positions within each quintile
    quintile_order = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    x_center = {q: i for i, q in enumerate(quintile_order)}
    rng = np.random.default_rng(seed=47)
    x_jitter = df[quantile_col].map(x_center) + rng.uniform(-0.3, 0.3, size=len(df))

    # -----> build figure
    fig, ax = plt.subplots(figsize=(10, 6))

    sc = ax.scatter(
        x_jitter,
        df[total_funding_col],
        c=colors,
        s=sizes,
        alpha=0.5,
        linewidths=0.3,
        edgecolors="white",
    )

    # -----> Q5 public funding reference line
    ax.axhline(
        q5_mean_public,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label=f"Q5 mean public funding (${q5_mean_public:,.0f})",
    )

    # -----> axes
    ax.set_xticks(range(len(quintile_order)))
    ax.set_xticklabels(quintile_order)
    ax.set_xlabel("ENI quintile", fontsize=11)
    ax.set_ylabel("Total per-pupil funding ($)", fontsize=11)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    # -----> size legend (manual)
    for pct, label in [(1, "1%"), (5, "5%"), (10, "10%")]:
        ax.scatter([], [], s=pct * size_scale + min_size,
                   color="gray", alpha=0.6, label=f"PTA share: {label}")

    # -----> color legend
    for q, c in QUINTILE_COLORS.items():
        ax.scatter([], [], color=c, alpha=0.8,
                   label=q + (" (lowest need)" if q == "Q1" else
                               " (highest need)" if q == "Q5" else ""))

    ax.legend(
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=9,
        bbox_to_anchor=(0.5, -0.12),
    )

    n = len(df)
    fig.suptitle(
        f"{title}\n{subtitle} ({year}, N={n:,})",
        fontsize=13, fontweight="bold",
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig