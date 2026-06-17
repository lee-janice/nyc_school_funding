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

PTA_QUINTILE_LEGEND_LABELS = {
    "Q1": "Q1 (lowest)",
    "Q2": "Q2",
    "Q3": "Q3",
    "Q4": "Q4",
    "Q5": "Q5 (highest)",
}

ENI_QUINTILE_LEGEND_LABELS = {
    "Q1": "Q1 (lowest need)",
    "Q2": "Q2",
    "Q3": "Q3",
    "Q4": "Q4",
    "Q5": "Q5 (highest need)",
}

# =============================================================================
#  PTA financial quintiles over time 
# =============================================================================
def plot_pta_quintile_trends(
    df,
    title="",
    subtitle="",
    save_path=None,
):

    income = np.log(
        df
        .groupby("year")["pp_pta_income"].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).unstack(level=1)
        .rename(columns={0.2: "Q1", 0.4: "Q2", 0.6: "Q3", 0.8: "Q4", 1.0: "Q5"})
    )
    expenditure = np.log(
        df
        .groupby("year")["pp_pta_expenditure"].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).unstack(level=1)
        .rename(columns={0.2: "Q1", 0.4: "Q2", 0.6: "Q3", 0.8: "Q4", 1.0: "Q5"})
    )
    balance = np.log(
        df
        .groupby("year")["pp_pta_end_balance"].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).unstack(level=1)
        .rename(columns={0.2: "Q1", 0.4: "Q2", 0.6: "Q3", 0.8: "Q4", 1.0: "Q5"})
    )

    # -----> replace inf with 0
    income       = income.replace([-np.inf], 0)
    expenditure  = expenditure.replace([-np.inf], 0)
    balance      = balance.replace([-np.inf], 0)

    # -----> build x axis 
    x_labels = [YEAR_LABELS.get(y, str(y)) for y in income.index]
    x_pos    = np.arange(len(x_labels))

    # -----> figure layout 
    fig, axes = plt.subplots(
        1, 3, 
        figsize=(14, 4.5),
        dpi=100,              
        sharey=False,   
        layout="constrained",
    )

    panels = [
        (axes[0], income,      "Log per-pupil income ($)",         "(a) Annual income"),
        (axes[1], expenditure, "Log per-pupil expenditure ($)",    "(b) Annual expenditure"),
        (axes[2], balance,     "Log per-pupil ending balance ($)", "(c) Ending balance"),
    ]


    for ax, data, ylabel, sub in panels:
        prev_values = None

        # -----> plot one line per quintile 
        for col in data.columns:
            current_values = data[col].values

            ax.plot(
                x_pos,
                current_values,
                label=PTA_QUINTILE_LEGEND_LABELS[col],
                color=QUINTILE_COLORS[col],
                linewidth=2.2,
                marker="o",
                markersize=5,
                zorder=3,
            )

            if prev_values is not None:
                ax.fill_between(
                    x_pos, 
                    y1=current_values,  # Top boundary
                    y2=prev_values,     # Bottom boundary
                    color=QUINTILE_COLORS[col],
                    alpha=0.2,          # Lower alpha prevents dark overlapping tints
                    zorder=2            # Keeps fill behind the line markers
                )
            else:
                ax.fill_between(
                    x_pos, 
                    y1=current_values, 
                    y2=0, 
                    color=QUINTILE_COLORS[col],
                    alpha=0.2,
                    zorder=2
                )
            
            prev_values = current_values

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
        loc="outside lower center", 
        ncol=5,
        frameon=False,
        fontsize=10,
        title="PTA financial quintile",
        title_fontsize=10,
    )

    y0 = np.min(df["year"]) 
    y1 = np.max(df["year"]) 

    fig.suptitle(
        f"\n{title}\n{subtitle} ({y0}-{y1})\n", 
        fontsize=13, fontweight="bold"
    )

    if save_path:
        # enforce dimensions onto the saving canvas object
        fig.set_size_inches(10, 5)
        
        fig.savefig(
            save_path, 
            dpi=150,           
            bbox_inches=None   
        )
        print(f"Saved to {save_path}")

    return fig



# =============================================================================
#  PTA financials by ENI quintile over time
# =============================================================================
def plot_eni_quintile_trends(
    df,
    title="",
    subtitle="",
    save_path=None,
):
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
        figsize=(14, 4.5),
        dpi=100,              
        sharey=False,   
        layout="constrained",
    )

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
                label=ENI_QUINTILE_LEGEND_LABELS[col],
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
        loc="outside lower center", 
        ncol=5,
        frameon=False,
        fontsize=10,
        title="ENI quintile",
        title_fontsize=10,
    )

    y0 = np.min(df["year"]) 
    y1 = np.max(df["year"]) 

    fig.suptitle(
        f"\n{title}\n{subtitle} ({y0}-{y1})\n", 
        fontsize=13, fontweight="bold"
    )

    if save_path:
        # enforce dimensions onto the saving canvas object
        fig.set_size_inches(10, 5)
        
        fig.savefig(
            save_path, 
            dpi=150,           
            bbox_inches=None   
        )
        print(f"Saved to {save_path}")

    return fig


