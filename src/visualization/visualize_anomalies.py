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




# =============================================================================
#  Dot plot of balance diff
# =============================================================================
def plot_balance_diff_dotplot(
    df,
    year_col="year",
    diff_col="pta_end_balance_diff", 
    pct_diff_col="pta_end_balance_pct_diff",
    abs_threshold=10_000,
    ylog=True,
    title="",
    subtitle="",
    save_path=None,
):
    if ylog: 
        df[diff_col] = np.log(df[diff_col])

    # -----> color and size mappings
    YEAR_COLORS = {
        2019: "#1f6bb0",
        2020: "#6aaed6",
        2021: "#999999",
        2022: "#f4a582",
        2023: "#d6604d",
        2024: "#d6604d",
        2025: "#d6604d",
    }

    # scale dot size by % diff
    size_scale = 0.5   # tweak to taste
    min_size   = 10
    max_size   = 100
    sizes = (df[pct_diff_col].clip(lower=0) * size_scale + min_size).clip(upper=max_size)

    colors = df[year_col].map(YEAR_COLORS)

    # -----> jitter x positions within each quintile
    year_order = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    x_center = {q: i for i, q in enumerate(year_order)}
    rng = np.random.default_rng(seed=47)
    x_jitter = df[year_col].map(x_center) + rng.uniform(-0.3, 0.3, size=len(df))

    # -----> build figure
    fig, ax = plt.subplots(figsize=(10, 6))

    sc = ax.scatter(
        x_jitter,
        df[diff_col],
        c=colors,
        s=sizes,
        alpha=0.5,
        linewidths=0.3,
        edgecolors="white",
    )

    # -----> absolute threshold line
    ax.axhline(
        np.log(abs_threshold) if ylog else abs_threshold,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label=f"Exclusion threshold (${abs_threshold:,.0f})",
    )

    # -----> axes
    ax.set_xticks(range(len(year_order)))
    ax.set_xticklabels(year_order)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Log of end balance difference ($)" if ylog else "End balance difference ($)", fontsize=11)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))


    # -----> size legend (manual)
    for pct, label in [(1, "Dot size corresponds to % difference")]:
        ax.scatter([], [], s=pct * size_scale + min_size,
                   color="gray", alpha=0.6, label=label)

    ax.legend(
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=9,
        bbox_to_anchor=(0.5, -0.12),
    )


    n = len(df)
    fig.suptitle(
        f"{title}\n{subtitle} (2019-2025, N={n:,})",
        fontsize=13, fontweight="bold",
    )

    plt.tight_layout()

    if ylog:
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())

        # explicitly include the threshold value as a tick
        threshold_log = np.log(10000)
        log_ticks = sorted(set(ax.get_yticks().tolist() + [threshold_log]))

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