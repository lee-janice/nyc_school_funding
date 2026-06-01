from src.analysis.descriptives_helpers import *
import pandas as pd
import numpy as np
import textwrap
import contextlib

# forces all floats in dataframes to show 2 decimal places
pd.set_option('display.float_format', '{:.2f}'.format)

# =============================================================================
#  Run script
# =============================================================================
with open("./output/pta_cross_sectional_2025.txt", "w") as f:
    with contextlib.redirect_stdout(f):
        PROFILE_YEAR = 2025

        print("\nLoading in data...") 
        funding_2019_2025 = pd.read_csv("data/processed/funding_2019_2025.csv")
        funding_xsect = funding_2019_2025.query(f"year == {PROFILE_YEAR}")

        print("\n-------------------------------------------------------------------------------")
        print(  "  PTA Activity                                                                 ")
        print(  "-------------------------------------------------------------------------------")
        print(f"\nPTA activity categories in {PROFILE_YEAR}")
        print(textwrap.indent(
            funding_xsect["pta_category"].value_counts().to_string(),
            prefix="\t")
        )

        print("\n-------------------------------------------------------------------------------")
        print(  "  Top-15 Schools by PTA Financials                                             ")
        print(  "-------------------------------------------------------------------------------")
        print(f"\nTop 15 schools by per-pupil PTA income in {PROFILE_YEAR}")
        top_15_income = (
            top_n_by_col(
                funding_xsect, 
                value_col="pp_pta_income", n=15, 
                keep_cols = ["school_name_x", "pta_income", "pp_pta_income", "eni_n", "p_white", "p_black", "p_hispanic", "p_asian"]
            )
        )
        print(textwrap.indent(top_15_income.to_string(), prefix="\t"))
        print("\nMeans of top 15")
        print(textwrap.indent(top_15_income.mean(numeric_only=True).to_string(), prefix="\t"))


        print(f"\nTop 15 schools by per-pupil PTA expenditures in {PROFILE_YEAR}")
        top_15_expenditure = (
            top_n_by_col(
                funding_xsect, 
                value_col="pp_pta_expenditure", n=15, 
                keep_cols = ["school_name_x", "pta_expenditure", "pp_pta_expenditure", "pta_expenditure_as_p_of_fsf", "eni_n", "p_white", "p_black", "p_hispanic", "p_asian"]
            )
        )
        print(textwrap.indent(top_15_expenditure.to_string(), prefix="\t"))
        print("\nMeans of top 15")
        print(textwrap.indent(top_15_expenditure.mean(numeric_only=True).to_string(), prefix="\t"))


        print(f"\nTop 15 schools by per-pupil PTA ending balance in {PROFILE_YEAR}")
        top_15_end_balance = (
            top_n_by_col(
                funding_xsect, 
                value_col="pp_pta_end_balance", n=15, 
                keep_cols = ["school_name_x", "pta_end_balance", "pp_pta_end_balance", "eni_n", "p_white", "p_black", "p_hispanic", "p_asian"]
            )
        )
        print(textwrap.indent(top_15_end_balance.to_string(), prefix="\t"))
        print("\nMeans of top 15")
        print(textwrap.indent(top_15_end_balance.mean(numeric_only=True).to_string(), prefix="\t"))


        print("\n-------------------------------------------------------------------------------")
        print(  "  ENI Quintiles                                                                ")
        print(  "-------------------------------------------------------------------------------")

        # separate out schools with active PTAs
        active_xsect = funding_xsect.query("pta_category == 'Active'")

        # -----> Full financial profile by ENI quintile in 2025
        # shows income, expenditure, start and end balance together
        # to give a complete picture of PTA financial health by need level

        print(f"\nMedian per-pupil PTA financials by ENI quintile ({PROFILE_YEAR}, active PTAs only):")
        print(textwrap.indent(
            median_by_category(
                active_xsect,
                category_cols = "eni_quintile",
                value_cols=["pp_pta_income", "pp_pta_expenditure", "pp_pta_start_balance", "pp_pta_end_balance"]
            ).T.unstack(level=1).to_string(),
            prefix="\t")
        )

        print("\n-------------------------------------------------------------------------------")
        print(  "  Racial Composition by PTA Financials                                         ")
        print(  "-------------------------------------------------------------------------------")


        print(f"\nRacial composition by PTA income quintiles ({PROFILE_YEAR}, active PTAs only):")
        print(textwrap.indent(
            mean_by_category(
                active_xsect,
                category_cols=["year", "pp_pta_income_quintile"],
                value_cols=["p_white", "p_black", "p_hispanic", "p_asian"])
            .multiply(100)
            .round(1)
            .stack(level=0)
            .to_string(), 
            prefix="\t")
        )

        print(f"\nRacial composition by PTA expenditure quintiles ({PROFILE_YEAR}, active PTAs only):")
        print(textwrap.indent(
            mean_by_category(
                active_xsect,
                category_cols=["year", "pp_pta_expenditure_quintile"],
                value_cols=["p_white", "p_black", "p_hispanic", "p_asian"])
            .multiply(100)
            .round(1)
            .stack(level=0)
            .to_string(), 
            prefix="\t")
        )

        print(f"\nRacial composition by PTA end balance quintiles ({PROFILE_YEAR}, active PTAs only):")
        print(textwrap.indent(
            mean_by_category(
                active_xsect,
                category_cols=["year", "pp_pta_end_balance_quintile"],
                value_cols=["p_white", "p_black", "p_hispanic", "p_asian"])
            .multiply(100)
            .round(1)
            .stack(level=0)
            .to_string(), 
            prefix="\t")
        )

        print("\n-------------------------------------------------------------------------------")
        print(  "  Median PTA Expenditure as Percent of FSF and Total Budget by ENI Q.          ")
        print(  "-------------------------------------------------------------------------------")
        print("\nMedian PTA expenditure as a percent of FSF allocations and total budget by ENI quintile (active PTAs only):")
        print(textwrap.indent(
            median_by_category(
                active_xsect,
                category_cols=["year", "eni_quintile"],
                value_cols=["pta_expenditure_as_p_of_fsf", "pta_expenditure_as_p_of_budget"])
            .round(1)
            .stack(level=0)
            .to_string(), 
            prefix="\t")
        )





