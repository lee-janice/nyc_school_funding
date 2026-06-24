import pandas as pd
import numpy as np
from scipy import stats

# =============================================================================
#  Define functions for validating data
# =============================================================================
# -----> Fix and flag within-year discrepancies in start balance, income, expenditure, and end balance 
def flag_and_correct_balances_wy(funding_data, pct_threshold = 0.01, abs_threshold = 10_000):

    # initialize audit columns 
    funding_data["correction_applied"] = "none"
    funding_data["tolerance"] = (funding_data["pta_end_balance"].abs() * pct_threshold).clip(lower=0.01)

    def calculate_implied(df): 
        df["pta_end_balance_implied"] = (
            df["pta_start_balance"] 
            + df["pta_income"]
            - df["pta_expenditure"]
        )
        df["pta_end_balance_diff"] = abs(df["pta_end_balance"] - df["pta_end_balance_implied"])
        df["pta_end_balance_pct_diff"] = df["pta_end_balance_diff"] / funding_data["pta_end_balance"]
        return df

    funding_data = calculate_implied(funding_data)

    # case 1: try scaling start_balance by 1/100 
    is_anomaly = (funding_data["pta_end_balance_diff"] > funding_data["tolerance"]) & (funding_data["pta_category"] == "Active")
    candidate = funding_data[is_anomaly].copy()
    candidate["pta_start_balance"] = candidate["pta_start_balance"] / 100

    candidate = calculate_implied(candidate)
    fixed_by_start = ~(abs(candidate["pta_end_balance_diff"]) > candidate["tolerance"]) | (candidate["pta_category"] != "Active")
    
    fixed_start_idx = fixed_by_start[fixed_by_start].index
    funding_data.loc[fixed_start_idx, "pta_start_balance"] /= 100
    funding_data.loc[fixed_start_idx, "correction_applied"] = "start_balance_div100"
    funding_data = calculate_implied(funding_data)
    
    # case 2: try scaling expenditure by 1/100 
    # only on records still inconsistent after pass 2
    still_inconsistent = (funding_data["pta_end_balance_diff"] > funding_data["tolerance"]) & (funding_data["pta_category"] == "Active")

    candidate2 = funding_data[still_inconsistent].copy()
    candidate2["pta_expenditure"] = candidate2["pta_expenditure"] / 100

    candidate2 = calculate_implied(candidate2)
    fixed_by_exp = ~(abs(candidate2["pta_end_balance_diff"]) > candidate2["tolerance"]) | (candidate2["pta_category"] != "Active")

    fixed_exp_idx = fixed_by_exp[fixed_by_exp].index
    funding_data.loc[fixed_exp_idx, "pta_expenditure"] /= 100
    funding_data.loc[fixed_exp_idx, "correction_applied"] = "expenditure_div100"
    funding_data = calculate_implied(funding_data)

    # case 3: try scaling income by 1/100 
    still_inconsistent = (funding_data["pta_end_balance_diff"] > funding_data["tolerance"]) & (funding_data["pta_category"] == "Active")

    candidate3 = funding_data[still_inconsistent].copy()
    candidate3["pta_income"] = candidate3["pta_income"] / 100

    candidate3 = calculate_implied(candidate3)
    fixed_by_income =  ~(abs(candidate3["pta_end_balance_diff"]) > candidate3["tolerance"]) | (candidate3["pta_category"] != "Active")

    fixed_inc_idx = fixed_by_income[fixed_by_income].index
    funding_data.loc[fixed_inc_idx, "pta_income"] /= 100
    funding_data.loc[fixed_inc_idx, "correction_applied"] = "income_div100"
    funding_data = calculate_implied(funding_data)

    # case 4: flag remaining as unresolvable
    still_inconsistent = (funding_data["pta_end_balance_diff"] > funding_data["tolerance"]) & (funding_data["pta_category"] == "Active")
    funding_data.loc[still_inconsistent, "correction_applied"] = "unresolvable"

    # flag unresolved cases
    funding_data["balance_wy_diff_flag"] = (
        (funding_data["correction_applied"] == "unresolvable") & 
        (funding_data["pta_end_balance_diff"] > abs_threshold)
    )

    funding_data = funding_data.drop(columns=["tolerance"])

    return funding_data


# -----> Flag cross-year discrepancies in Y0 end balance -> Y1 start balance
def flag_ets_balances(funding_data, pct_threshold = 0.01, abs_threshold = 10_000): 

    funding_data = funding_data.assign(

        # create lag variable to compare end->start balance 
        lag_pta_end_balance = lambda x: x.groupby("dbn")["pta_end_balance"].shift(1), 
        ets_balance_diff = lambda x: abs(x["pta_start_balance"] - x["lag_pta_end_balance"]),
        ets_balance_pct_diff = lambda x: x["ets_balance_diff"] / x["pta_start_balance"].clip(lower=0.01),

        # flag differences
        ets_balance_diff_cat = lambda x: pd.cut(
            x["ets_balance_pct_diff"],
            bins=[-np.inf, 0, 0.01, 0.05, 0.50, 1.00, 2.00, 5.00, np.inf],
            labels=["exact_match", "under_0.01", "under_0.05", "under_0.50", "under_1.00", "under_2.00", "under_5.00", "extreme_outlier"],
            right=True
        ),

        ets_balance_diff_flag = lambda x: (x["ets_balance_pct_diff"] > pct_threshold) & (x["ets_balance_diff"] > abs_threshold)
    )

    return funding_data


# -----> Flag within-year, cross-school anomalies 
def flag_transactions_wy(funding_data, transaction_vars, std_threshold = 3): 
    # cross-sectional z-score on log-transformed values, within each year
    funding_data = (
        funding_data
        .assign(**{
            f"{var}_log": lambda df, v=var: np.log(df[v] - np.min(df[v]) + 1)
            for var in transaction_vars
        })
        .assign(**{
            f"{var}_zscore": lambda df, v=var: (
                df.groupby("year")[f"{v}_log"]
                .transform(lambda x: stats.zscore(x, nan_policy="omit"))
            )
            for var in transaction_vars
        })
        # flag if greater than threshold (only in positive direction to capture values that are far too high)
        .assign(**{
            f"{var}_wy_transaction_flag": lambda df, v=var: df[f"{v}_zscore"] > std_threshold
            for var in transaction_vars
        })
    )

    funding_data = funding_data.drop(columns=funding_data.filter(regex='_log$|_zscore$').columns)

    return funding_data


# -----> Flag cross-year, within-school anomalies 
def flag_transactions_ws(funding_data, transaction_vars, std_threshold = 3):
    
    # deviation from school's own median
    funding_data = (
        funding_data
        .assign(**{
            f"{var}_school_median": lambda df, v=var: (
                df.groupby("dbn")[v]
                .transform("median")
            )
            for var in transaction_vars
        })
        # flag if greater than threshold (only in positive direction, to capture values that are far too high)
        .assign(**{
            f"{var}_ws_transaction_flag": lambda df, v=var: (
                (df[v] - df[f"{v}_school_median"]) > std_threshold * df.groupby("dbn")[v].transform("std")
            )
            for var in transaction_vars
        })
    )

    funding_data = funding_data.drop(columns=funding_data.filter(regex='_school_median$').columns)

    return funding_data