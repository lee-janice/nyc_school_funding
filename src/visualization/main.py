from src.visualization.visualize_anomalies import plot_flag_vs_funding_boxplot
from src.visualization.visualize_anomalies import plot_flag_vs_funding_scatter
from src.visualization.visualize_anomalies import plot_flag_vs_funding_hist
from src.visualization.visualize_cross_sectional import plot_pta_expenditure_percentiles
from src.visualization.visualize_cross_sectional import plot_top_schools_annotated
from src.visualization.visualize_cross_sectional import plot_eni_vs_expenditure_scatter
from src.visualization.visualize_cross_sectional import plot_racial_comp_by_pta_quantile
from src.visualization.visualize_trends import plot_quintile_trends
import pandas as pd
import matplotlib.pyplot as plt
import sys

def create_figures():
    try:
        print("\nLoading data...") 
        funding_2019_2025 = pd.read_csv("data/processed/funding_2019_2025.csv")


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

        
        # -----> Balance anomalies
        fig = plot_flag_vs_funding_boxplot(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_b_flagged", "ever_xy_b_flagged"],
            flag_labels = ["Within-year balance flag", "Cross-year balance flag"],
            save_path="output/figures/fig1a_balance_flag_vs_expenditure_boxplot.png"
        )

        fig = plot_flag_vs_funding_scatter(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["n_wy_b_flags", "n_xy_b_flags"],
            save_path="output/figures/fig1b_balance_flag_vs_expenditure_scatter.png"
        )

        fig = plot_flag_vs_funding_hist(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_b_flagged", "ever_xy_b_flagged"],
            flag_labels = ["Within-year balance flag", "Cross-year balance flag"],
            save_path="output/figures/fig1c_balance_flag_vs_expenditure_hist.png"
        )


        # -----> Transaction anomalies
        fig = plot_flag_vs_funding_boxplot(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_t_flagged", "ever_ws_t_flagged"],
            flag_labels = ["Within-year, cross-school transaction flag", "Within-school, cross-year transaction flag"],
            save_path="output/figures/fig2a_transaction_flag_vs_expenditure_boxplot.png"
        )

        fig = plot_flag_vs_funding_scatter(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["n_wy_t_flags"],
            save_path="output/figures/fig2b_wy_transaction_flag_vs_expenditure_scatter.png"
        )

        fig = plot_flag_vs_funding_scatter(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["n_ws_t_flags"],
            save_path="output/figures/fig2b_ws_transaction_flag_vs_expenditure_scatter.png"
        )

        fig = plot_flag_vs_funding_hist(
            funding_2019_2025, 
            funding_col = "pta_expenditure",
            funding_label = "PTA expenditure",
            flags = ["ever_wy_t_flagged", "ever_ws_t_flagged"],
            flag_labels = ["Within-year, cross-school transaction flag", "Within-school, cross-year transaction flag"],
            save_path="output/figures/fig2c_transaction_flag_vs_expenditure_hist.png"
        )

        # based on anomaly and sensitivity analysis,
        # exclude observations which are flagged for cross-year, within-school anomalies
        funding_wout_flagged = funding_2019_2025.query("not any_ws_transaction_flag")
        # active PTAs only 
        active = funding_wout_flagged.query("pta_category == 'Active'")


        # -----> Percentile rank by expendtiures
        fig, pcts, values = plot_pta_expenditure_percentiles(
            funding_wout_flagged,
            years=[2025],
            highlight_pcts=[50, 75, 90, 95, 99],
            title="Per-pupil PTA expenditure by percentile rank", 
            subtitle="All schools — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig4_expenditure_percentiles.png",
        )

        fig, pcts, values = plot_pta_expenditure_percentiles(
            active,
            years=[2025],
            highlight_pcts=[50, 75, 90, 95, 99],
            title="Per-pupil PTA expenditure by percentile rank", 
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32 ",
            save_path="output/figures/fig4_expenditure_percentiles_active.png",
        )


        # ------> Top schools annotated
        fig = plot_top_schools_annotated(
            funding_wout_flagged, year=2025,
            school_name_col="school_name_x",
            top_n=15,
            subtitle="All schools — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig7_top_schools_annotated.png"
        )
        fig = plot_top_schools_annotated(
            active, year=2025,
            school_name_col="school_name_x",
            top_n=15,
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig7_top_schools_annotated_active.png"
        )


        # ------> Racial composition by PTA expenditures
        fig = plot_racial_comp_by_pta_quantile(
            funding_wout_flagged, 
            years=[2025],
            quantile_col="pp_pta_expenditure_quintile",
            title="Mean school racial composition by PTA expenditure quantile\n",
            subtitle="All schools — NYC Public Schools, Districts 1-32 ",
            save_path="output/figures/fig5_racial_comp_by_pta.png"
        )
        fig = plot_racial_comp_by_pta_quantile(
            active, 
            years=[2025],
            quantile_col="pp_pta_expenditure_quintile",
            title="Mean school racial composition by PTA expenditure quantile\n",
            subtitle="Active PTAs only — NYC Public Schools, Districts 1-32 ",
            save_path="output/figures/fig5_racial_comp_by_pta_active.png"
        )



        # ------> ENI vs. PTA expenditure
        fig = plot_eni_vs_expenditure_scatter(
            funding_wout_flagged, year=2025,
            subtitle="Active PTAs with non-zero expenditures only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig6_eni_vs_expenditure.png"
        )


        # -----> Quintile trends over time
        fig = plot_quintile_trends(
            funding_wout_flagged,
            title="Median per-pupil PTA finances by Economic Need Index quintile\n",
            subtitle="All schools — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig3_quintile_trends.png"
        )
        fig = plot_quintile_trends(
            active,
            title="Median per-pupil PTA finances by Economic Need Index quintile\n",
            subtitle="Active PTAs only — NYC Public Schools, Districts 1–32",
            save_path="output/figures/fig3_quintile_trends_active.png"
        )


    except Exception as e:
        print(f"Create figures failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_figures()
