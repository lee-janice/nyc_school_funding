from src.processing.load import write_to_db
from src.processing.transform import *
from src.processing.validate import *
from extract import read_data
import textwrap
import pandas as pd
import sys

def run_pipeline():
    try:
        print("\nPipeline execution started...")
        
        # -----> EXTRACT
        print("\nExtracting data...")

        # Read in Demographic Snapshot data (2019-2025)
        print("\tReading in demographic data...")
        dem_data = dict() 
        # (2019-2020)
        dem_1620 = read_data("./data/raw/demographics/2019-20_Demographic_Snapshot_-_School.xlsx", sheet_name="Data")
        for yr in range(19, 21): 
            dem_data[f"20{yr}"] = dem_1620.query(f"Year == '20{yr-1}-{yr}'")
        # (2021-2025)
        dem_2125 = read_data("./data/raw/demographics/demographic-snapshot-2020-21-to-2024-25-public.xlsx", sheet_name="School")
        for yr in range(21, 26): 
            dem_data[f"20{yr}"] = dem_2125.query(f"Year == '20{yr-1}-{yr}'")

        # Read in Fair Student Funding data (2019-2025)
        print("\tReading in Fair Student Funding data...")
        fsf_data = dict()
        fsf_sheet_names = ["LL16 Report", "Data", "FY21 LL16", "FY22 LL16", "FY 23 LL 16_Full Rpt", "FY 24 LL 16_Full Rpt", "LL16"]
        for i, sheet_name in enumerate(fsf_sheet_names): 
            yr = i + 19
            # conditionally pass in arguments for diff years
            match yr: 
                case 19: 
                    kwargs = {"skiprows": 3}
                case 25: 
                    kwargs = {"skiprows": 1}
                case _: 
                    kwargs = {}
            fsf_data[f"20{yr}"] = read_data(f"./data/raw/fsf/fy{yr}-local-law-16-final-report.xlsx", sheet_name = sheet_name, **kwargs)
                
        # Read in PTA fundraising data (2019-2025)
        print("\tReading in PTA fundraising data...")
        pta_data = dict()
        for yr in range(19, 26): 
            pta_data[f"20{yr}"] = read_data(f"./data/raw/pta/20{yr-1}-{yr}-pta-financial-reporting.xlsx", sheet_name = "School")

        
        # -----> TRANSFORM
        print("\nTransforming data...")
        funding = dict()

        for year in range(2019, 2026): 
            print(f"\t* Processing data for {year}!")

            dem = clean_column_names(dem_data[f"{year}"])
            fsf = clean_column_names(fsf_data[f"{year}"])
            pta = clean_column_names(pta_data[f"{year}"])

            df = merge_data(dem, fsf, pta, year, by="dbn")
            df = define_sample(df)
            df = df.query("in_sample == 1") # only keep schools in the sample 
            df = transform_data(df, year)

            funding[f"{year}"] = df


        # -----> VALIDATE
        print("\nValidating data...")
        # stack to create a long/panel dataset
        funding_2019_2025 = pd.concat(
            [funding["2019"], funding["2020"], funding["2021"], funding["2022"], funding["2023"], funding["2024"], funding["2025"]], 
            axis=0, 
            ignore_index=True
        )


        # correct and flag within-year discrepancies in balances/incomes/expenditures
        # creates a flag: balance_wy_diff_flag if unresolvable
        funding_2019_2025 = flag_and_correct_balances_wy(funding_2019_2025, tolerance=1000)

        print("Within-year balance correction summary:")
        print(textwrap.indent(funding_2019_2025["correction_applied"].value_counts().to_string(), prefix="\t"))
        print(f"\n\tShare resolved: "
            f"{(funding_2019_2025['correction_applied'] != 'unresolvable').mean():.1%}")
        print(f"\tShare unresolvable: "
            f"{(funding_2019_2025['correction_applied'] == 'unresolvable').mean():.1%}")

        print(f"\n\tAverage post-discrepancy for no correction applied: "
            f"{funding_2019_2025.query("correction_applied == 'none'")["balance_wy_diff_post"].mean().round(1)}")
        print(f"\tAverage post-discrepancy for one correction applied: "
            f"{funding_2019_2025.query("correction_applied != 'none' and correction_applied != 'unresolvable'")["balance_wy_diff_post"].mean().round(1)}")
        print(f"\tAverage post-discrepancy for unresolvable obs: "
            f"{funding_2019_2025.query("correction_applied == 'unresolvable'")["balance_wy_diff_post"].mean().round(1)}")


        # flag cross-year discrepancies in end-> start balances
        # creates a flag: balance_xy_diff_flag if discrepancy > 100,000
        funding_2019_2025 = flag_balances_xy(funding_2019_2025)

        print("\nCross-year end->start balance discrepancies:")
        print(textwrap.indent(funding_2019_2025["balance_xy_diff_cat"].value_counts().to_string(), prefix="\t"))

        # get schools with repeated discrepancies
        # print("\nSchools with repeated large or extreme discrepancies:")
        # print(textwrap.indent(outliers["school_name_x"].value_counts().head(15).to_string(), prefix="\t"))

        # flag anomalous transactions using z-score on log-transformed values
        # creates *_transaction_flag if z-score > 2
        transaction_vars = ["pta_start_balance", "pta_income", "pta_expenditure", "pta_end_balance"]
        funding_2019_2025 = flag_transactions_wy(funding_2019_2025, transaction_vars, std_threshold=2)

        print("\nTransaction discrepancies:")
        for t in transaction_vars:
            print(textwrap.indent(funding_2019_2025[f"{t}_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))
            print()
        print(textwrap.indent(funding_2019_2025["any_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))

    
        # -----> Calculate variables
        print("\nCalculating derivative and quintile variables...")
        funding_2019_2025 = add_pta_derivatives(funding_2019_2025)
        funding_2019_2025 = add_quintiles(funding_2019_2025)

        # -----> Load data 
        print("\nLoading data...")
        funding_2019_2025.to_csv("./data/processed/funding_2019_2025.csv")
        write_to_db(funding_2019_2025, "school_funding.db", "funding")

        flagged = (
            funding_2019_2025
            .query("balance_wy_diff_flag or balance_xy_diff_flag or any_transaction_flag")
            .filter(regex='school_name_x|year|^pta.*balance$|^pta.*income$|^pta.*expenditure$|lag_pta*|end_to_start*|.*flag')
        )
        flagged.to_csv("./data/processed/flagged.csv")
        write_to_db(flagged, "school_funding.db", "flagged")

        print("\nPipeline execution complete!")
        
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
