from src.analysis.descriptives_helpers import median_by_category
from src.analysis.descriptives_helpers import mean_by_category
from src.analysis.descriptives_helpers import category_counts
import pandas as pd
import textwrap
import contextlib

# =============================================================================
#  Trends-over-time analysis
# =============================================================================
def pta_trends_analysis(funding_data, output_path): 

    with open(output_path, "w") as f:
        # forces all floats in dataframes to show 2 decimal places
        pd.set_option('display.float_format', '{:.2f}'.format)

        with contextlib.redirect_stdout(f):

            print("\n-------------------------------------------------------------------------------")
            print(  "  PTA Activity Trends                                                          ")
            print(  "-------------------------------------------------------------------------------")
            # -----> PTA activity categories 
            print("\nFrequencies of PTA activity categories over time:")
            pta_activity_counts = (
                category_counts(funding_data, category_col="pta_category")
                .reindex(columns=["Active", "Inactive", "Missing"], fill_value=0)
                .assign(Total = lambda x: x.sum(axis=1))
            )
            print(textwrap.indent(pta_activity_counts.to_string(), prefix="\t"))


            print("\n-------------------------------------------------------------------------------")
            print(  "  ENI Trends                                                                   ")
            print(  "-------------------------------------------------------------------------------")
            print("\nMean ENI of within PTA activity category over time:")
            print(textwrap.indent(
                mean_by_category(
                    funding_data, 
                    category_cols=["year", "pta_category"], 
                    value_cols="eni_n")
                .to_string(), 
                prefix="\t")
            )

            # -----> ENI quintiles (within year) 
            print("\nENI quintiles, by year:")
            print(textwrap.indent(
                funding_data.groupby("year")["eni_n"].quantile([0.2, 0.4, 0.6, 0.8]).unstack(level=1).to_string(), 
                prefix="\t")
            )

            print("\nShare of schools with active PTAs by ENI quintile over time:")
            active_ptas_by_eni_quintile = (
                funding_data
                .groupby(["year", "eni_quintile"])
                .apply(lambda g: (g["pta_category"] == "Active").mean())
                .round(2)
                .unstack("eni_quintile")
            )
            print(textwrap.indent(
                active_ptas_by_eni_quintile.to_string(), 
                prefix="\t")
            )

            # separate out schools with active PTAs
            active_2019_2025 = funding_data.query("pta_category == 'Active'")

            print("\nMedian per-pupil PTA income by ENI quintile (active PTAs only):")
            print(textwrap.indent(
                median_by_category(  # noqa: F821
                    active_2019_2025, 
                    category_cols=["year", "eni_quintile"],
                    value_cols="pp_pta_income")
                .to_string(), 
                prefix="\t")
            )

            print("\nMedian per-pupil PTA expenditure by ENI quintile (active PTAs only):")
            print(textwrap.indent(
                median_by_category(
                    active_2019_2025, 
                    category_cols=["year", "eni_quintile"], 
                    value_cols="pp_pta_expenditure")
                .to_string(), 
                prefix="\t")
            )

            print("\nMedian per-pupil PTA ending balance by ENI quintile (active PTAs only):")
            print(textwrap.indent(
                median_by_category(
                    active_2019_2025, 
                    category_cols=["year", "eni_quintile"], 
                    value_cols="pp_pta_end_balance")
                .to_string(), 
                prefix="\t")
            )


            print("\n-------------------------------------------------------------------------------")
            print(  "  PTA Income Trends                                                            ")
            print(  "-------------------------------------------------------------------------------")
            # -----> PTA income quintiles (active PTAs, within year)
            print("\nPTA income quintiles for active PTAs, by year:")
            print(textwrap.indent(
                active_2019_2025.groupby("year")["pp_pta_income"].quantile([0.2, 0.4, 0.6, 0.8]).unstack(level=1).to_string(), 
                prefix="\t")
            )

            # -----> Racial composition by PTA income quintiles
            print("\nRacial composition by PTA income quintiles (active PTAs only):")
            print(textwrap.indent(
                mean_by_category(
                    active_2019_2025,
                    category_cols=["year", "pp_pta_income_quintile"],
                    value_cols=["p_white", "p_black", "p_hispanic", "p_asian"])
                .multiply(100)
                .round(1)
                .to_string(), 
                prefix="\t")
            )


            print("\n-------------------------------------------------------------------------------")
            print(  "  PTA Expenditure Trends                                                       ")
            print(  "-------------------------------------------------------------------------------")
            # -----> PTA expenditure quintiles (active PTAs, within year)
            print("\nPTA expenditure quintiles for active PTAs, by year:")
            print(textwrap.indent(
                active_2019_2025.groupby("year")["pp_pta_expenditure"].quantile([0.2, 0.4, 0.6, 0.8]).unstack(level=1).to_string(), 
                prefix="\t")
            )

            # -----> Racial composition by PTA expenditure quintiles
            print("\nRacial composition by PTA expenditure quintiles (active PTAs only):")
            print(textwrap.indent(
                mean_by_category(
                    active_2019_2025,
                    category_cols=["year", "pp_pta_expenditure_quintile"],
                    value_cols=["p_white", "p_black", "p_hispanic", "p_asian"])
                .multiply(100)
                .round(1)
                .to_string(), 
                prefix="\t")
            )


            print("\n-------------------------------------------------------------------------------")
            print(  "  PTA End Balance Trends                                                       ")
            print(  "-------------------------------------------------------------------------------")
            # -----> PTA end balance quintiles (active PTAs, within year)
            print("\nPTA end balance quintiles for active PTAs, by year:")
            print(textwrap.indent(
                active_2019_2025.groupby("year")["pp_pta_end_balance"].quantile([0.2, 0.4, 0.6, 0.8]).unstack(level=1).to_string(), 
                prefix="\t")
            )

            # -----> Racial composition by PTA end balance quintiles
            print("\nRacial composition by PTA end balance quintiles (active PTAs only):")
            print(textwrap.indent(
                mean_by_category(
                    active_2019_2025,
                    category_cols=["year", "pp_pta_end_balance_quintile"],
                    value_cols=["p_white", "p_black", "p_hispanic", "p_asian"])
                .multiply(100)
                .round(1)
                .to_string(), 
                prefix="\t")
            )


            print("\n-------------------------------------------------------------------------------")
            print(  "  Median PTA Expenditure as Percent of FSF and Total Budget by ENI Q.          ")
            print(  "-------------------------------------------------------------------------------")
            print("\nMedian PTA expenditure as a percent of FSF allocations and total budget by ENI quartile (active PTAs only):")
            print(textwrap.indent(
                median_by_category(
                    active_2019_2025,
                    category_cols=["year", "eni_quintile"],
                    value_cols=["pta_expenditure_as_p_of_fsf", "pta_expenditure_as_p_of_budget"])
                .round(1)
                .to_string(), 
                prefix="\t")
            )

    print(f"\tTrends-over-time analysis output written to {output_path}!")




