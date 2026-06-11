from src.analysis.descriptives_helpers import median_by_category
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

YEAR_LABELS = {
    2019: "2018–19", 2020: "2019–20", 2021: "2020–21",
    2022: "2021–22", 2023: "2022–23", 2024: "2023–24",
    2025: "2024–25",
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
#  PTA financials by ENI quintile over time
# =============================================================================
def plot_quintile_trends(
    df,
    title="",
    subtitle="",
    save_path=None,
):
    # active = funding_data.query("pta_category == 'Active'")

    quintile_pp_income = (
        median_by_category(
            df, 
            category_cols=["year", "eni_quintile"],
            value_cols="pp_pta_income"
        )
    )
    quintile_pp_expenditure = (
        median_by_category(
            df, 
            category_cols=["year", "eni_quintile"],
            value_cols="pp_pta_expenditure"
        )
    )
    quintile_pp_end_balance = (
        median_by_category(
            df, 
            category_cols=["year", "eni_quintile"],
            value_cols="pp_pta_end_balance"
        )
    )

    # -----> replace inf with NaN so they plot as gaps 
    income       = quintile_pp_income.replace([np.inf, -np.inf], np.nan)
    expenditure  = quintile_pp_expenditure.replace([np.inf, -np.inf], np.nan)
    balance      = quintile_pp_end_balance.replace([np.inf, -np.inf], np.nan)

    # -----> build x axis 
    x_labels = [YEAR_LABELS.get(y, str(y)) for y in income.index]
    x_pos    = np.arange(len(x_labels))

    # -----> figure layout 
    fig, axes = plt.subplots(
        1, 3, 
        figsize=(24, 5.5),
        sharey=False,   
        constrained_layout=True,
    )

    # add more space above the subplots
    fig.set_constrained_layout_pads(w_pad=0.1, h_pad=0.5) 

    panels = [
        (axes[0], income,      "Median per-pupil income ($)",         "(a) Annual income"),
        (axes[1], expenditure, "Median per-pupil expenditure ($)",    "(b) Annual expenditure"),
        (axes[2], balance,     "Median per-pupil ending balance ($)", "(c) Ending balance"),
    ]

    for ax, data, ylabel, sub in panels:

        # -----> plot one line per quintile 
        for col in data.columns:
            ax.plot(
                x_pos,
                data[col].values,
                label=QUINTILE_LEGEND_LABELS[col],
                color=QUINTILE_COLORS[col],
                linewidth=2.2,
                marker="o",
                markersize=5,
                zorder=3,
            )

        # -----> formatting 
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, rotation=30, ha="right")
        ax.set_xlabel("School year", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(sub)
        ax.set_ylim(bottom=0)

    # -----> shared legend below both panels 
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels,
        loc="lower center",
        ncol=5,
        frameon=False,
        fontsize=10,
        bbox_to_anchor=(0.5, -0.12),
        title="ENI quintile",
        title_fontsize=10,
    )

    y0 = np.min(df["year"]) 
    y1 = np.max(df["year"]) 

    fig.suptitle(
        f"{title}"
        f"{subtitle} "
        f"({y0}-{y1})",
        fontsize=13, fontweight="bold", y=1.02
    )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig


