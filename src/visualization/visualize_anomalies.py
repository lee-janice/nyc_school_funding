import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# =============================================================================
#  Flags vs. PTA funding
# =============================================================================
def plot_flag_vs_funding_boxplot(
    df, 
    funding_col, 
    funding_label,
    flags,
    flag_labels,
    save_path = None
):

    school_summary = (
        df
        .groupby("dbn")
        .agg(
            mean_funding       = (funding_col, "mean"),
            n_obs              = ("year", "count"),
            wy_b_flag_rate     = ("balance_wy_diff_flag", "mean"),
            xy_b_flag_rate     = ("ets_balance_diff_flag", "mean"),
            wy_t_flag_rate     = ("any_wy_transaction_flag", "mean"),
            ws_t_flag_rate     = ("any_ws_transaction_flag", "mean"),
            any_flag_rate      = ("anomaly_flag", "mean"),
        )
        .assign(
            log_mean_funding     = lambda df: np.log1p(df["mean_funding"]),
            ever_wy_b_flagged = lambda df: (df["wy_b_flag_rate"] > 0).astype(int),
            ever_xy_b_flagged = lambda df: (df["xy_b_flag_rate"] > 0).astype(int),
            ever_wy_t_flagged = lambda df: (df["wy_t_flag_rate"] > 0).astype(int),
            ever_ws_t_flagged = lambda df: (df["ws_t_flag_rate"] > 0).astype(int),
        )
        .reset_index()
    )

    fig, axes = plt.subplots(1, len(flags), figsize=(12, 5))

    for ax, flag, title in zip(
        axes,
        flags,
        flag_labels
    ):
        sns.boxplot(
            data=school_summary,
            x=flag, y="log_mean_funding",
            ax=ax,
            boxprops=dict(alpha=0.8)
        )
        ax.set_title(title)
        ax.set_xlabel("Ever flagged")
        ax.set_ylabel(f"Log mean {funding_label}")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig


def plot_flag_vs_funding_scatter(
    df, 
    funding_col, 
    funding_label,
    flags, 
    save_path = None
):

    school_summary = (
        df
        .groupby("dbn")
        .agg(
            mean_funding     = (funding_col, "mean"),
            log_mean_funding = (funding_col, lambda x: np.log1p(x.mean())),
            n_wy_b_flags     = ("balance_wy_diff_flag", "sum"),
            n_xy_b_flags     = ("ets_balance_diff_flag", "sum"),
            n_wy_t_flags     = ("any_wy_transaction_flag", "sum"),
            n_ws_t_flags     = ("any_ws_transaction_flag", "sum"),
            n_obs            = ("year", "count"),
            mean_eni         = ("eni_n", "mean")
        )
        .assign(
            total_flags       = lambda df: df[flags].sum(axis=1),
            flag_rate         = lambda df: df["total_flags"] / df["n_obs"],
        )
        .reset_index()
    )

    fig, ax = plt.subplots(1, 1, figsize=(14, 6))

    scatter = ax.scatter(
        x=school_summary["log_mean_funding"],
        y=school_summary["total_flags"],
        c=school_summary["mean_eni"],       
        cmap="coolwarm",
        alpha=0.6,
        edgecolors="none",
        s=40
    )
    
    ax.set_xlabel(f"Log mean {funding_label}")
    ax.set_ylabel("Number of times flagged")
    ax.set_title(f"{funding_label} vs. number of times flagged")
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.colorbar(scatter, ax=ax, label="Economic Need Index")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig


def plot_flag_vs_funding_hist(
    df, 
    funding_col, 
    funding_label,
    flags,
    flag_labels,
    save_path = None
):

    school_summary = (
        df
        .groupby("dbn")
        .agg(
            mean_funding       = (funding_col, "mean"),
            n_obs              = ("year", "count"),
            wy_b_flag_rate     = ("balance_wy_diff_flag", "mean"),
            xy_b_flag_rate     = ("ets_balance_diff_flag", "mean"),
            wy_t_flag_rate     = ("any_wy_transaction_flag", "mean"),
            ws_t_flag_rate     = ("any_ws_transaction_flag", "mean"),
            any_flag_rate      = ("anomaly_flag", "mean"),
            mean_eni           = ("eni_n", "mean")
        )
        .assign(
            log_mean_funding  = lambda df: np.log1p(df["mean_funding"]),
            ever_wy_b_flagged = lambda df: (df["wy_b_flag_rate"] > 0).astype(int),
            ever_xy_b_flagged = lambda df: (df["xy_b_flag_rate"] > 0).astype(int),
            ever_wy_t_flagged = lambda df: (df["wy_t_flag_rate"] > 0).astype(int),
            ever_ws_t_flagged = lambda df: (df["ws_t_flag_rate"] > 0).astype(int),
        )
        .reset_index()
    )

    fig, axes = plt.subplots(1, len(flags), figsize=(12, 5))

    for ax, flag, title in zip(
        axes,
        flags,
        flag_labels,
        # ["ever_wy_flagged", "ever_xy_flagged"],
        # ["Within-year balance flag", "Cross-year balance flag"]
    ):
        for flagged, color, label in [(False, "steelblue", "Not flagged"), (True, "firebrick", "Flagged")]:
            subset = school_summary[school_summary[flag] == flagged]
            ax.hist(
                subset["log_mean_funding"],
                bins=30,
                alpha=0.5,
                color=color,
                label=label,
                density=True      # normalize 
            )
        ax.set_title(title)
        ax.set_xlabel(f"Log mean {funding_label}")
        ax.set_ylabel("Density")
        ax.legend()

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")

    return fig
