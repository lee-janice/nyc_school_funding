import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from sklearn.preprocessing import StandardScaler

def model_anomalies(df): 

    school_summary = (
        df
        .groupby("dbn")
        .agg(
            mean_income        = ("pta_income", "mean"),
            mean_expenditure   = ("pta_expenditure", "mean"),
            mean_end_balance   = ("pta_end_balance", "mean"),
            n_obs              = ("year", "count"),
            wy_flag_rate       = ("balance_wy_diff_flag", "mean"),
            xy_flag_rate       = ("ets_balance_diff_flag", "mean"),
            any_flag_rate      = ("anomaly_flag", "mean"),
            mean_eni           = ("eni_n", "mean")
        )
        .assign(
            log_mean_income      = lambda df: np.log1p(df["mean_income"]),
            log_mean_expenditure = lambda df: np.log1p(df["mean_expenditure"]),
            log_mean_end_balance = lambda df: np.log1p(df["mean_end_balance"]),
            ever_wy_flagged      = lambda df: (df["wy_flag_rate"] > 0).astype(int),
            ever_xy_flagged      = lambda df: (df["xy_flag_rate"] > 0).astype(int),
        )
        .reset_index()
    )
    
    # standardize values
    std_scaler = StandardScaler()
    school_summary[["log_mean_income", "mean_eni"]] = std_scaler.fit_transform(school_summary[["log_mean_income", "mean_eni"]])

    for flag in ["ever_wy_flagged", "ever_xy_flagged"]:

        # bivariate (income only) 
        m1 = smf.logit(  # noqa: F821
            formula=f"{flag} ~ log_mean_income",
            data=school_summary.dropna(subset=["log_mean_income", "mean_eni", flag])
        ).fit(disp=False)

        # add ENI
        m2 = smf.logit(
            formula=f"{flag} ~ log_mean_income + mean_eni",
            data=school_summary.dropna(subset=["log_mean_income", "mean_eni", flag])
        ).fit(disp=False)

        # interaction: does the income-error relationship differ by ENI level?
        m3 = smf.logit(
            formula=f"{flag} ~ log_mean_income * mean_eni",
            data=school_summary.dropna(subset=["log_mean_income", "mean_eni", flag])
        ).fit(disp=False)

        print(f"\n{'='*55}")
        print(f"  {flag}")
        print(f"{'='*55}")
        for label, m in [("M1: Income only", m1), ("M2: + ENI", m2), ("M3: + Interaction", m3)]:
            tbl = m.summary2().tables[1][["Coef.", "Std.Err.", "P>|z|"]]
            print(f"\n--- {label} (Pseudo-R²: {m.prsquared:.3f}) ---")
            print(tbl)
