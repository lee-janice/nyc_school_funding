from src.visualization.visualize_cross_sectional import plot_total_funding_dotplot
from src.visualization.visualize_cross_sectional import plot_funding_stacked
from src.visualization.visualize_cross_sectional import plot_eni_vs_finance_scatter
from src.visualization.visualize_trends import plot_pta_quintile_trends
from src.visualization.visualize_trends import plot_eni_quintile_trends
from src.visualization.visualize_anomalies import plot_flag_vs_funding_boxplot
from src.visualization.visualize_anomalies import plot_flag_vs_funding_scatter
from src.visualization.visualize_anomalies import plot_flag_vs_funding_hist
from src.visualization.visualize_cross_sectional import plot_pta_expenditure_percentiles
from src.visualization.visualize_cross_sectional import plot_top_schools_annotated
from src.visualization.visualize_cross_sectional import plot_racial_comp_by_pta_quantile
import pandas as pd
import matplotlib.pyplot as plt
import sys

def create_fig1(funding_df): 
    try: 
        plot_flag_vs_funding_boxplot(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_b_flagged", "ever_xy_b_flagged"],
            flag_labels = ["Within-year balance flag", "Cross-year balance flag"],
            save_path="output/figures/fig1a_balance_flag_vs_expenditure_boxplot.png"
        )

        plot_flag_vs_funding_scatter(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["n_wy_b_flags", "n_xy_b_flags"],
            save_path="output/figures/fig1b_balance_flag_vs_expenditure_scatter.png"
        )

        plot_flag_vs_funding_hist(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_b_flagged", "ever_xy_b_flagged"],
            flag_labels = ["Within-year balance flag", "Cross-year balance flag"],
            save_path="output/figures/fig1c_balance_flag_vs_expenditure_hist.png"
        )

    except Exception as e:
        print(f"Create figure 1 failed: {str(e)}")
        sys.exit(1)


def create_fig2(funding_df): 
    try: 
        plot_flag_vs_funding_boxplot(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_t_flagged", "ever_ws_t_flagged"],
            flag_labels = ["Within-year, cross-school transaction flag", "Within-school, cross-year transaction flag"],
            save_path="output/figures/fig2a_transaction_flag_vs_expenditure_boxplot.png"
        )

        plot_flag_vs_funding_scatter(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["n_wy_t_flags"],
            save_path="output/figures/fig2b_wy_transaction_flag_vs_expenditure_scatter.png"
        )

        plot_flag_vs_funding_scatter(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["n_ws_t_flags"],
            save_path="output/figures/fig2b_ws_transaction_flag_vs_expenditure_scatter.png"
        )

        plot_flag_vs_funding_hist(
            funding_df, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_t_flagged", "ever_ws_t_flagged"],
            flag_labels = ["Within-year, cross-school transaction flag", "Within-school, cross-year transaction flag"],
            save_path="output/figures/fig2c_transaction_flag_vs_expenditure_hist.png"
        )


    except Exception as e:
        print(f"Create figure 2 failed: {str(e)}")
        sys.exit(1)


def create_fig3(funding_df, active_df): 
    try: 
        fig, pcts, values = plot_pta_expenditure_percentiles(
            funding_df,
            years=[2025],
            highlight_pcts=[50, 75, 90, 95, 99],
            title="Per-pupil PTA expenditure by percentile rank", 
            subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig3_expenditure_percentiles.png",
        )

        fig, pcts, values = plot_pta_expenditure_percentiles(
            active_df,
            years=[2025],
            highlight_pcts=[50, 75, 90, 95, 99],
            title="Per-pupil PTA expenditure by percentile rank", 
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32 ",
            save_path="output/figures/fig3_expenditure_percentiles_active.png",
        )

    except Exception as e:
        print(f"Create figure 3 failed: {str(e)}")
        sys.exit(1)


def create_fig4(funding_df, active_df): 
    try: 
        plot_top_schools_annotated(
            funding_df, year=2025,
            school_name_col="school_name_x",
            top_n=15,
            subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig4_top_schools_annotated.png"
        )

        plot_top_schools_annotated(
            active_df, year=2025,
            school_name_col="school_name_x",
            top_n=15,
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig4_top_schools_annotated_active.png"
        )

    except Exception as e:
        print(f"Create figure 4 failed: {str(e)}")
        sys.exit(1)


def create_fig5(active_df): 
    try: 
        plot_eni_vs_finance_scatter(
            active_df.query("pp_pta_expenditure > 0"), year=2025,
            finance_col="pp_pta_expenditure",
            ylabel="Log per-pupil PTA expenditure",
            title="Economic need vs. per-pupil PTA expenditure per pupil\n",
            subtitle="Active PTAs with non-zero expenditures only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig5_eni_vs_expenditure.png"
        )

    except Exception as e:
        print(f"Create figure 5 failed: {str(e)}")
        sys.exit(1)


def create_fig6(active_df): 
    try: 
        plot_racial_comp_by_pta_quantile(
            active_df, 
            years=[2025],
            quantile_col="pp_pta_expenditure_quintile",
            title="Mean school racial composition by per=pupil PTA expenditure quantile\n",
            subtitle="Active PTAs only — NYC Public Schools, Districts 1-32 ",
            save_path="output/figures/fig6_racial_comp_by_pta_active.png"
        )

    except Exception as e:
        print(f"Create figure 6 failed: {str(e)}")
        sys.exit(1)


def create_fig7(funding_df, active_df): 
    try: 
        plot_eni_quintile_trends(
            funding_df,
            title="Median per-pupil PTA finances by Economic Need Index quintile",
            subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig7_eni_quintile_trends.png"
        )
        plot_eni_quintile_trends(
            active_df,
            title="Median per-pupil PTA finances by Economic Need Index quintile",
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig7_eni_quintile_trends_active.png"
        )

    except Exception as e:
        print(f"Create figure 7 failed: {str(e)}")
        sys.exit(1)


def create_fig8(funding_df, active_df): 
    try: 
        plot_pta_quintile_trends(
            funding_df,
            title="Per-pupil PTA financial quintiles over time",
            subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig8_pta_quintile_trends.png"
        )
        plot_pta_quintile_trends(
            active_df,
            title="Per-pupil PTA financial quintiles over time",
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig8_pta_quintile_trends_active.png"
        )

    except Exception as e:
        print(f"Create figure 8 failed: {str(e)}")
        sys.exit(1)




if __name__ == "__main__":

    # globally set plotting parameters
    plt.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.titlesize': 12,          
        'axes.titlesize': 12,          
        'axes.titleweight': 'bold',   
        'axes.titlepad': 8,
        'axes.labelsize': 11,        
    })


    print("\nLoading data...") 
    funding_2019_2025 = pd.read_csv("data/processed/funding_2019_2025.csv")

    # based on anomaly and sensitivity analysis,
    # exclude observations which are flagged for 
    # within-year balance discrepancies
    # also, remove PTAs with missing records
    funding_final = funding_2019_2025.query(
        "not balance_wy_diff_flag and pta_category != 'Missing'"
        # "not any_ws_transaction_flag and not balance_wy_diff_flag"
        # "not balance_wy_diff_flag and not ets_balance_diff_flag" # too many schools are flagged
    )

    # pull out missing PTAs 
    missing = funding_2019_2025.query("pta_category == 'Missing'")
    print(f"\nNumber of schools missing PTA information: {missing["year"].value_counts().sort_index().to_string()}\n")
    missing.to_csv("./data/processed/omitted_because_missing.csv")

    # pull out the omitted observations
    flagged = funding_2019_2025.query("balance_wy_diff_flag")
    print(f"\nNumber of excluded observations: {flagged["year"].value_counts().sort_index().to_string()}\n")
    flagged.to_csv("./data/processed/omitted_because_flagged.csv")

    # isolate active PTAs only 
    active = funding_final.query("pta_category == 'Active'")


    # -----> Balance anomalies
    create_fig1(funding_2019_2025)

    # -----> Transaction anomalies
    create_fig2(funding_2019_2025)

    # -----> Percentile rank by expendtiures
    create_fig3(funding_df=funding_final, active_df=active)

    # ------> Top schools annotated
    create_fig4(funding_df=funding_final, active_df=active)

    # ------> ENI vs. PTA expenditure
    create_fig5(active_df=active)

    # ------> Racial composition by PTA expenditures
    create_fig6(active_df=active)

    # -----> ENI quintile trends over time
    create_fig7(funding_df=funding_final, active_df=active)

    # -----> PTA quintile trends over time
    create_fig8(funding_df=funding_final, active_df=active)

    plot_eni_vs_finance_scatter(
        funding_final.query("pp_fsf > 0"), year=2025,
        finance_col="pp_fsf",
        ylabel="Log per-pupil Fair Student Funding allocation",
        title="Economic need vs. Fair Student Funding (FSF) allocations\n",
        subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
        legend_loc="upper left",
        save_path="output/figures/fig9a_eni_vs_fsf.png"
    )

    plot_eni_vs_finance_scatter(
        funding_final.query("pp_non_fsf > 0"), year=2025,
        finance_col="pp_non_fsf",
        ylabel="Log per-pupil non-Fair Student Funding allocation",
        title="Economic need vs. non-Fair Student Funding (FSF) allocations\n",
        subtitle="All schools with non-missing FSF data — NYC Public Schools, Districts 1–32",
        legend_loc="upper left",
        save_path="output/figures/fig9b_eni_vs_non_fsf.png"
    )

    plot_funding_stacked(
        funding_final,
        year=2025,          
        funding_cols=["pp_fsf", "pp_non_fsf", "pp_pta_expenditure"],
        quantile_col="eni_quintile",
        title="Total school funding by ENI quintile\n", 
        subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
        save_path = "output/figures/fig10_funding_by_eni_quintile.png",
    )


    plot_eni_vs_finance_scatter(
        funding_final, year=2025,
        finance_col="pta_expenditure_as_p_of_total",
        ylog=False,
        ylabel="PTA expenditure as share of total funding (%)",
        show_ols=False,
        title="Economic need vs. PTA expenditure as share of total funding\n",
        subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
        legend_loc="upper right",
        save_path="output/figures/fig11a_eni_vs_pta_as_share_of_total.png"
    )


    plot_eni_vs_finance_scatter(
        funding_final, year=2025,
        finance_col="pta_expenditure_as_p_of_fsf",
        ylog=False,
        ylabel="PTA expenditure as share of FSF (%)",
        show_ols=False,
        title="Economic need vs. PTA expenditure as share of FSF allocations\n",
        subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
        legend_loc="upper right",
        save_path="output/figures/fig11b_eni_vs_pta_as_share_of_fsf.png"
    )

    plot_total_funding_dotplot(
        funding_final, year=2025,
        total_funding_col="pp_total_funding", 
        public_funding_col="pp_total_public",  
        pta_share_col="pta_expenditure_as_p_of_total", 
        quantile_col="eni_quintile",
        title="PTA expenditures relative to total funding by ENI quintile",
        subtitle="All schools with non-missing PTA data — NYC Public Schools, Districts 1–32",
        save_path="output/figures/fig12_total_funding_dotplot"
    )
