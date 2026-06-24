from src.processing.validate import flag_ets_balances
from load import write_to_csv
from load import write_to_db
from extract import read_pta
from extract import read_fsf
from extract import read_dem
from validate import flag_transactions_ws
from transform import transform_data
from transform import define_sample
from transform import merge_data
from transform import clean_column_names
from transform import add_quintiles
from transform import add_pta_derivatives
from validate import flag_transactions_wy
from validate import flag_and_correct_balances_wy
import textwrap
import pandas as pd
import sys
import matplotlib.pyplot as plt


def extract(): 
    try: 
        print("\nExtracting data...")

        # Read in Demographic Snapshot data (2019-2025)
        print("\tReading in demographic data...")
        dem_data = read_dem()
        
        # Read in Fair Student Funding data (2019-2025)
        print("\tReading in Fair Student Funding data...")
        fsf_data = read_fsf()

        # Read in PTA fundraising data (2019-2025)
        print("\tReading in PTA fundraising data...")
        pta_data = read_pta()

        return (dem_data, fsf_data, pta_data)

    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        sys.exit(1)
  

def transform(dem_data, fsf_data, pta_data): 
    try: 
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

        # stack to create a long/panel dataset
        funding_2019_2025 = pd.concat(
            [funding["2019"], funding["2020"], funding["2021"], funding["2022"], funding["2023"], funding["2024"], funding["2025"]], 
            axis=0, 
            ignore_index=True
        )

        return funding_2019_2025

    except Exception as e:
        print(f"Transformation failed: {str(e)}")
        sys.exit(1)
  

def validate_wy_balances(funding_2019_2025): 
    # correct and flag within-year discrepancies in balances/incomes/expenditures
    # creates a flag: balance_wy_diff_flag if unresolvable and difference is greater than 10,000
    funding_2019_2025 = flag_and_correct_balances_wy(funding_2019_2025, pct_threshold=0.05, abs_threshold=10_000)

    print("Within-year balance correction summary:")
    print(textwrap.indent(funding_2019_2025["correction_applied"].value_counts().to_string(), prefix="\t"))
    print(f"\n\tShare resolved: "
        f"{(funding_2019_2025['correction_applied'] != 'unresolvable').mean():.1%}")
    print(f"\tShare unresolvable: "
        f"{(funding_2019_2025['correction_applied'] == 'unresolvable').mean():.1%}")

    print(f"\n\tAverage post-discrepancy for no correction applied: "
        f"{funding_2019_2025.query("correction_applied == 'none'")["pta_end_balance_diff"].mean().round(1)}")
    print(f"\tAverage post-discrepancy for one correction applied: "
        f"{funding_2019_2025.query("correction_applied != 'none' and correction_applied != 'unresolvable'")["pta_end_balance_diff"].mean().round(1)}")
    print(f"\tAverage post-discrepancy for unresolvable obs: "
        f"{funding_2019_2025.query("correction_applied == 'unresolvable'")["pta_end_balance_diff"].mean().round(1)}")

    print("\nPercent flagged:")
    print(textwrap.indent(funding_2019_2025["balance_wy_diff_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))
    
    return funding_2019_2025


def validate_ets_balances(funding_2019_2025): 
    # flag cross-year discrepancies in end-> start balances
    # creates a flag: ets_balance_diff_flag if discrepancy > 5% of starting balance and is more than $(abs_threshold)
    abs_threshold = 50_000
    funding_2019_2025 = flag_ets_balances(funding_2019_2025, pct_threshold=0.05, abs_threshold=abs_threshold)

    print("\nCross-year end->start balance discrepancies:")
    print(textwrap.indent(funding_2019_2025["ets_balance_diff_cat"].value_counts().to_string(), prefix="\t"))

    print(f"\nLimited to where difference > ${abs_threshold}:")
    print(textwrap.indent((funding_2019_2025.query(f"ets_balance_diff > {abs_threshold}"))["ets_balance_diff_cat"].value_counts().to_string(), prefix="\t"))

    print("\nPercent flagged:")
    print(textwrap.indent(funding_2019_2025["ets_balance_diff_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))

    # plt.hist(funding_2019_2025["ets_balance_diff"], bins=10, range=(0, 100_000))
    # plt.show()

    return funding_2019_2025


def validate_transactions(funding_2019_2025):
    # flag within-year, cross-school anomalous transactions using z-score on log-transformed values
    # creates *_transaction_flag if z-score > 3
    transaction_vars = ["pta_start_balance", "pta_income", "pta_expenditure", "pta_end_balance"]
    funding_2019_2025 = flag_transactions_wy(funding_2019_2025, transaction_vars, std_threshold=3)

    # flag cross-year, within-school anomalous transactions
    # make z-score threshold a little lower, 0 obs were flagged at threshold of 3
    # funding_2019_2025 = flag_transactions_ws(funding_2019_2025, transaction_vars, std_threshold=2.6)
    funding_2019_2025 = flag_transactions_ws(funding_2019_2025, transaction_vars, std_threshold=2.65)

    wy_transaction_flags  = [f"{v}_wy_transaction_flag" for v in transaction_vars]
    ws_transaction_flags  = [f"{v}_ws_transaction_flag" for v in transaction_vars]

    # flag if any transaction flag
    funding_2019_2025 = (
        funding_2019_2025
        .assign(
            any_wy_transaction_flag = lambda df: df[wy_transaction_flags].any(axis=1),
            any_ws_transaction_flag = lambda df: df[ws_transaction_flags].any(axis=1),
            any_transaction_flag    = lambda df: df[wy_transaction_flags+ws_transaction_flags].any(axis=1),
        )
    )
    
    print("\nTransaction discrepancies:")
    for t in transaction_vars:
        print(textwrap.indent(funding_2019_2025[f"{t}_wy_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))
        print(textwrap.indent(funding_2019_2025[f"{t}_ws_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))
        print()
    print(textwrap.indent(funding_2019_2025["any_wy_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))
    print(textwrap.indent(funding_2019_2025["any_ws_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))
    print(textwrap.indent(funding_2019_2025["any_transaction_flag"].value_counts(normalize=True).mul(100).round(1).to_string(), prefix="\t"))

    return funding_2019_2025


def validate(funding_2019_2025): 
    try: 
        print("\nValidating data...")

        funding_2019_2025 = validate_wy_balances(funding_2019_2025)
        funding_2019_2025 = validate_ets_balances(funding_2019_2025)
        funding_2019_2025 = validate_transactions(funding_2019_2025)

        # mark if observation has any flag 
        funding_2019_2025 = (
            funding_2019_2025
            .assign(anomaly_flag = lambda x: x["balance_wy_diff_flag"] | x["ets_balance_diff_flag"] | x["any_transaction_flag"])
        )

        print("\nPercent of anomalous observations:")
        print(
            textwrap
            .indent(
                funding_2019_2025["anomaly_flag"]
                .value_counts(normalize=True)
                .mul(100).round(1).to_string(), 
                prefix="\t"
            )
        )

        return funding_2019_2025


    except Exception as e:
        print(f"Validation failed: {str(e)}")
        sys.exit(1)
  

def load(funding_2019_2025):
    try:
        print("\nLoading data...")
        write_to_csv(funding_2019_2025, "./data/processed/funding_2019_2025.csv")
        write_to_db(funding_2019_2025, "./data/processed/school_funding.db", "funding", drop=True)

        flagged = (
            funding_2019_2025
            .query("balance_wy_diff_flag or ets_balance_diff_flag or any_transaction_flag")
            .filter(regex='school_name_x|year|^pta.*balance$|^pta.*income$|^pta.*expenditure$|lag_pta*|end_to_start*|.*flag')
        )
        write_to_csv(flagged, "./data/processed/flagged.csv")

    except Exception as e:
        print(f"Load failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("\nPipeline execution started...")
    
    # -----> EXTRACT
    (dem_data, fsf_data, pta_data) = extract()
    
    # -----> TRANSFORM
    funding_2019_2025 = transform(dem_data, fsf_data, pta_data)

    # -----> VALIDATE
    funding_2019_2025 = validate(funding_2019_2025)

    # -----> Calculate variables
    print("\nCalculating derivative and quintile variables...")
    funding_2019_2025 = add_pta_derivatives(funding_2019_2025) 
    funding_2019_2025 = add_quintiles(funding_2019_2025)

    # -----> LOAD
    load(funding_2019_2025)

    print("\nPipeline execution complete!")
