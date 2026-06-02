import pandas as pd
import numpy as np
from scipy import stats

# =============================================================================
#  Define functions for validating data
# =============================================================================
# -----> Fix and flag within-year discrepancies in start balance, income, expenditure, and end balance 
def flag_and_correct_balances_wy(funding_data, tolerance = 1000):

    def implied(row):
        return (
            row["pta_start_balance"]
            + row["pta_income"]
            - row["pta_expenditure"]
        )

    def within_tol_or_NaN(row):
        return abs(row["pta_end_balance"] - implied(row)) <= tolerance or (row["pta_category"] != "Active")

    # initialize audit columns 
    funding_data["correction_applied"] = "none"
    funding_data["balance_wy_diff"] = (
        funding_data["pta_end_balance"] - (
            funding_data["pta_start_balance"]
            + funding_data["pta_income"]
            - funding_data["pta_expenditure"]
        )
    ).abs()

    # case 0: already consistent 
    consistent_mask = funding_data.apply(within_tol_or_NaN, axis=1)
    # no action needed for these rows

    # case 1: try scaling start_balance by 1/100 
    needs_fix = ~consistent_mask
    candidate = funding_data[needs_fix].copy()
    candidate["pta_start_balance"] = candidate["pta_start_balance"] / 100

    fixed_by_start = candidate.apply(within_tol_or_NaN, axis=1)

    funding_data.loc[needs_fix & fixed_by_start.reindex(funding_data.index, fill_value=False), "pta_start_balance"] /= 100
    funding_data.loc[needs_fix & fixed_by_start.reindex(funding_data.index, fill_value=False), "correction_applied"] = "start_balance_div100"
    
    # case 2: try scaling expenditure by 1/100 
    # only on records still inconsistent after pass 2
    still_inconsistent = ~funding_data.apply(within_tol_or_NaN, axis=1)

    candidate2 = funding_data[still_inconsistent].copy()
    candidate2["pta_expenditure"] = candidate2["pta_expenditure"] / 100

    fixed_by_exp = candidate2.apply(within_tol_or_NaN, axis=1)

    funding_data.loc[still_inconsistent & fixed_by_exp.reindex(funding_data.index, fill_value=False), "pta_expenditure"] /= 100
    funding_data.loc[still_inconsistent & fixed_by_exp.reindex(funding_data.index, fill_value=False), "correction_applied"] = "expenditure_div100"

    # case 3: try scaling income by 1/100 
    still_inconsistent = ~funding_data.apply(within_tol_or_NaN, axis=1)

    candidate3 = funding_data[still_inconsistent].copy()
    candidate3["pta_income"] = candidate3["pta_income"] / 100

    fixed_by_income = candidate3.apply(within_tol_or_NaN, axis=1)

    funding_data.loc[still_inconsistent & fixed_by_income.reindex(funding_data.index, fill_value=False), "pta_income"] /= 100
    funding_data.loc[still_inconsistent & fixed_by_income.reindex(funding_data.index, fill_value=False), "correction_applied"] = "income_div100"

    # case 4: flag remaining as unresolvable
    still_inconsistent = ~funding_data.apply(within_tol_or_NaN, axis=1)
    funding_data.loc[still_inconsistent, "correction_applied"] = "unresolvable"

    # recompute discrepancy after corrections 
    funding_data["balance_wy_diff_post"] = (
        funding_data["pta_end_balance"] - (
            funding_data["pta_start_balance"]
            + funding_data["pta_income"]
            - funding_data["pta_expenditure"]
        )
    ).abs()

    # flag unresolved cases
    funding_data["balance_wy_diff_flag"] = funding_data["correction_applied"] == "unresolvable"

    return funding_data


# -----> Flag cross-year discrepancies in Y0 end balance -> Y1 start balance
def flag_balances_xy(funding_data): 

    funding_data = funding_data.assign(
        # create lag variable to compare end->start balance 
        lag_pta_end_balance = lambda x: x.groupby("dbn")["pta_end_balance"].shift(1), 
        end_to_start_balance_diff = lambda x: abs(x["pta_start_balance"] - x["lag_pta_end_balance"]),

        # flag differences
        balance_xy_diff_cat = lambda x: pd.cut(
            x["end_to_start_balance_diff"],
            bins=[-np.inf, 0, 500, 5000, 100_000, np.inf],
            labels=["exact_match", "small_diff", "moderate_diff", "large_diff", "extreme_outlier"],
            right=True
        ),

        balance_xy_diff_flag = lambda x: x["balance_xy_diff_cat"].isin(["large_diff", "extreme_outlier"])
    )

    return funding_data


# -----> Flag within-year, cross-school anomalies 
def flag_transactions_wy(funding_data, transaction_vars, std_threshold = 3): 
    # cross-sectional z-score on log-transformed values, within each year
    funding_data = (
        funding_data
        .assign(**{
            # f"{var}_log": lambda df, v=var: np.log1p(df[v]+LOG_SHIFT)
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
        # flag if greater than threshold
        .assign(**{
            f"{var}_transaction_flag": lambda df, v=var: df[f"{v}_zscore"].abs() > std_threshold
            for var in transaction_vars
        })
    )
    transaction_flags  = [f"{v}_transaction_flag" for v in transaction_vars]

    # flag if any transaction flag
    funding_data = (
        funding_data
        .assign(
            any_transaction_flag=lambda df: df[transaction_flags].any(axis=1),
        )
    )

    return funding_data

