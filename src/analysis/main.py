from src.analysis.anomalies import investigate_anomalies
from src.analysis.modeling import model_anomalies
from src.analysis.trends import pta_trends_analysis
from src.analysis.cross_sectional import pta_cross_sectional_analysis
import pandas as pd
import sys

def run_descriptives(funding_data):

    try:
        # run descriptives on full sample 
        print("\nRunning trends-over-time analysis with full sample...")
        pta_trends_analysis(funding_2019_2025, "./output/trends.txt")

        print("\nRunning cross-sectional analysis for 2025 with full sample...")
        pta_cross_sectional_analysis(funding_2019_2025, 2025, "./output/cross_sectional_2025.txt")

        # sensitivity analysis: run descriptives without flagged transactions/anomalies 

        # SENSITIVITY ANALYSIS 1
        # but don't exclude within-year, cross-school anomalies- 
        # these are mostly schools in the long right tail 
        # that have valid but very large PTA values (compared to other schools) 
        funding_sensitivity = funding_2019_2025.query(
            "not balance_wy_diff_flag and not ets_balance_diff_flag and not any_ws_transaction_flag"
        )

        print("\nRunning trends-over-time analysis without anomalies...")
        pta_trends_analysis(funding_sensitivity, "./output/trends_SA1.txt")

        print("\nRunning cross-sectional analysis for 2025 without anomalies...")
        pta_cross_sectional_analysis(funding_sensitivity, 2025, "./output/cross_sectional_2025_SA1.txt")


        # SENSITIVITY ANALYSIS 2
        # also run with not excluding balance flags - which are also mostly high-income schools
        funding_sensitivity = funding_2019_2025.query(
            "not any_ws_transaction_flag"
        )

        print("\nRunning trends-over-time analysis excluding only cross-year, within-school anomalies...")
        pta_trends_analysis(funding_sensitivity, "./output/trends_SA2.txt")

        print("\nRunning cross-sectional analysis excluding only cross-year, within-school anomalies...")
        pta_cross_sectional_analysis(funding_sensitivity, 2025, "./output/cross_sectional_2025_SA2.txt")
        

        # SENSITIVITY ANALYSIS 3
        # run with excluding within-year balance discrepancies (implied end balance != reported end balance) 
        funding_sensitivity = funding_2019_2025.query(
            "not balance_wy_diff_flag"
        )

        print("\nRunning trends-over-time analysis excluding within-year balance discrepancies...")
        pta_trends_analysis(funding_sensitivity, "./output/trends_SA3.txt")

        print("\nRunning cross-sectional analysis excluding only within-year balance discrepancies...")
        pta_cross_sectional_analysis(funding_sensitivity, 2025, "./output/cross_sectional_2025_SA3.txt")
        


    except Exception as e:
        print(f"Running descriptives failed: {str(e)}")
        sys.exit(1)


def run_models(funding_data): 

    try:
        print("\nModeling anomalies...")
        model_anomalies(funding_data)

    except Exception as e: 
        print(f"Running models failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__": 
    print("\nLoading in data...") 
    funding_2019_2025 = pd.read_csv("data/processed/funding_2019_2025.csv")

    investigate_anomalies()
    run_descriptives(funding_2019_2025)
    run_models(funding_2019_2025)


