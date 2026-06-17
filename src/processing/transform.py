from src.analysis.descriptives_helpers import top_n_by_col
import pandas as pd
import numpy as np
import janitor

# =============================================================================
#  Define functions for merging and transforming
# =============================================================================
def clean_column_names(df):
    return (
        df
        .clean_names()
        .replace("&","and")
        .rename(columns=lambda x:x.lower().replace("%","p"))
        .rename(columns=lambda x:x.lower().replace("#","n")
    )
    )

# -----> Merging data 
def merge_data(dem, fsf, pta, year, by="dbn"): 

    # create DBN column in FSF data for 2019, 2020, 2025
    if year in [2019]: 
        fsf = fsf.assign(dbn = lambda x: x["district"].astype(str).str.zfill(2) + x["school_code"])

    if year in [2020, 2025]: 
        fsf = fsf.assign(dbn = lambda x: x["school_code"])
            
    # merge demographics, FSF, and PTA data
    return dem.merge(
            fsf, 
            left_on = "dbn", right_on = "dbn", 
            how = "outer", 
            indicator = True
        ).rename(columns={"_merge":"first_merge"}).merge(
            pta,
            left_on = "dbn", right_on = "dbn", 
            how = "outer", 
            indicator = True
        ).rename(columns={"_merge":"second_merge"})


# -----> Defining sample of schools 
def define_sample(funding_data): 
    return funding_data.assign(
            district_n = pd.to_numeric(funding_data["district"], errors="coerce")
        ).assign(
            in_sample = lambda x: 
                # limit to Districts 1-32
                (x["district_n"] >= 1) & (x["district_n"] <= 32) &
                # limit to schools in all datasets
                (x["first_merge"] == "both") & (x["second_merge"] == "both")
        )


# -----> Creating new columns 
def transform_data(funding_data, year): 
    return funding_data.rename(
        columns = {
            "total_fsf_allocation_including_foundation_and_collective_bargaining_costs" : "total_fsf_allocations",
            "total_fsf_allocation_at_100p_including_foundation_&_adjusted_for_collective_bargaining_costs" : "total_fsf_at_100",
            "total_income": "pta_income",
            "total_expenses": "pta_expenditure",
            "beginning_balance": "pta_start_balance",
            "ending_balance": "pta_end_balance",
            "p_asian_and_pacific_islander": "p_asian"
        }
    ).assign(

        year = year,

        # clean FSF columns 
        total_fsf_allocations = lambda x: x["total_fsf_allocations"].astype(str).str.replace(r'[\$,]', '', regex=True).astype(float),
        total_fsf_at_100 = lambda x: x["total_fsf_at_100"].astype(str).str.replace(r'[\$,]', '', regex=True).astype(float),
        non_fsf_budget_allocations = lambda x: x['non_fsf_budget_allocations'].astype(str).str.replace(r'[\$,]', '', regex=True).astype(float),
        total_budget_allocation = lambda x: x['total_budget_allocation'].astype(str).str.replace(r'[\$,]', '', regex=True).astype(float),
        weighted_register_allocation = lambda x: x['total_budget_allocation'].astype(str).str.replace(r'[\$,]', '', regex=True).astype(float),

        # numeric Economic Need Index 
        eni_n = lambda x: np.where(
            (x["economic_need_index"] == "Above 95%") | (x["economic_need_index"] == "Above 95"), 
            0.95, 
            np.where(
                x["year"] <= 2020, 
                pd.to_numeric(x["economic_need_index"].astype(str).str.replace('%', ''), errors="coerce") / 100,
                pd.to_numeric(x["economic_need_index"].astype(str).str.replace('%', ''), errors="coerce")
            )
        ),

        # other race category 
        p_other_race = lambda x: 1 - x["p_black"] - x["p_hispanic"] - x["p_white"] - x["p_asian"], 

        # borough identifier 
        borough = funding_data["dbn"].str[2:3],

        # PTA category
        pta_category = lambda x: np.select(
            condlist=[
                # if missing all values, mark PTA as Missing
                x["pta_start_balance"].isnull() & x["pta_income"].isnull() & x["pta_expenditure"].isnull() & x["pta_end_balance"].isnull(), 

                # if has non-zero values anywhere, mark PTA as Active
                (x["pta_start_balance"] > 0) | (x["pta_income"] > 0) | (x["pta_expenditure"] > 0)  | (x["pta_end_balance"] > 0), 
            ],
            choicelist=[
                "Missing",
                "Active"
            ],
            default="Inactive"
        ),

        # active flag 
        pta_active = lambda x: pd.to_numeric(np.select(
            condlist=[
                x["pta_category"] == "Missing", 
                x["pta_category"] == "Inactive", 
                x["pta_category"] == "Active", 
            ],
            choicelist=[
                None,
                0,
                1
            ],
            default=None
        )),
    ).filter(
        items=[
            # school characteristics
            "dbn", "school_name_x", "year", "district", "school_type", "total_enrollment", "borough", "in_sample",

            # school demographics 
            "p_asian", "p_black", "p_hispanic", "p_multiple_race_categories_not_represented", "p_white", 
            "p_multi_racial", "p_asian_and_pacific_islander", "p_native_american", "p_missing_race_ethnicity_data", "p_other_race",
            "p_students_with_disabilities", "p_english_language_learners", 
            "p_poverty", "economic_need_index", "eni_n",

            # FSF variables
            "weighted_register_allocation", "total_fsf_allocations", "non_fsf_budget_allocations", 
            "total_budget_allocation", "fsf_as_p_of_total_budget_allocation" "p_funded",

            # PTA variables
            "pta_income", "pta_expenditure", "pta_start_balance", "pta_end_balance", "pta_category", "pta_active",
            ]
    )


# -----> Adding derivatives of PTA data
def add_pta_derivatives(funding_data): 
    return funding_data.assign(
        # create per-pupil values 
        pp_fsf = lambda x: x['total_fsf_allocations'] / x['total_enrollment'],
        pp_non_fsf = lambda x: x['non_fsf_budget_allocations'] / x['total_enrollment'],
        pp_total_public = lambda x: x['total_budget_allocation'] / x['total_enrollment'],

        pp_pta_income = lambda x: x['pta_income'] / x['total_enrollment'],
        pp_pta_expenditure = lambda x: x['pta_expenditure'] / x['total_enrollment'],
        pp_pta_start_balance = lambda x: x['pta_start_balance'] / x['total_enrollment'],
        pp_pta_end_balance = lambda x: x['pta_end_balance'] / x['total_enrollment'],

        # log transform PTA variables
        # log_pp_pta_end_balance = lambda x: np.log(x['pp_pta_end_balance'] + \
        #     np.abs(np.min(x["pp_pta_end_balance"])) + 1),

        # add total pp funding
        pp_total_funding = lambda x: x['pp_fsf'] + x['pp_non_fsf'] + x['pp_pta_expenditure'],

        # add PTA expenditure as a percent of FSF allocations and total budget allocation
        pta_expenditure_as_p_of_fsf = lambda x: x['pta_expenditure'] / x['total_fsf_allocations'] * 100,
        pta_expenditure_as_p_of_public = lambda x: x['pta_expenditure'] / x['total_budget_allocation'] * 100,
        pta_expenditure_as_p_of_total = lambda x: x['pta_expenditure'] / (x['total_budget_allocation'] + x['pta_expenditure']) * 100,
    )


# -----> Adding quintiles
def add_quintiles(funding_data): 
    # ENI 
    funding_data["eni_quintile"] = (
        funding_data
        .groupby("year")["eni_n"]
        .apply(lambda x: pd.qcut(
            x, q=5, duplicates="drop",
            labels=["Q1", "Q2", "Q3", "Q4", "Q5"]
        ))
        .reset_index(level=0, drop=True)
    )

    # PP-PTA income
    funding_data["pp_pta_income_quintile"] = (
        funding_data
        .query("pta_category == 'Active'")
        .groupby("year")["pp_pta_income"]
        .apply(lambda x: pd.qcut(
            x, q=5, duplicates="drop",
            # in 2021, Q1 and Q2 both have bin cutoffs at 0 - so we have to force only 4 quartiles 
            labels=["Q2", "Q3", "Q4", "Q5"] if x.name == 2021 else ["Q1", "Q2", "Q3", "Q4", "Q5"]
        ))
        .reset_index(level=0, drop=True)
    )

    # PP-PTA expenditure
    funding_data["pp_pta_expenditure_quintile"] = (
        funding_data
        .query("pta_category == 'Active'")
        .groupby("year")["pp_pta_expenditure"]
        .apply(lambda x: pd.qcut(
            x, q=5, duplicates="drop",
            # in 2021, Q1 and Q2 both have bin cutoffs at 0 - so we have to force only 4 quartiles 
            labels=["Q2", "Q3", "Q4", "Q5"] if x.name == 2021 else ["Q1", "Q2", "Q3", "Q4", "Q5"]
        ))
        .reset_index(level=0, drop=True)
    )
    
    # PP-PTA ending balance
    funding_data["pp_pta_end_balance_quintile"] = (
        funding_data
        .query("pta_category == 'Active'")
        .groupby("year")["pp_pta_end_balance"]
        .apply(lambda x: pd.qcut(
            x, q=5, duplicates="drop",
            # in 2021, Q1 and Q2 both have bin cutoffs at 0 - so we have to force only 4 quartiles 
            labels=["Q1", "Q2", "Q3", "Q4", "Q5"]
        ))
        .reset_index(level=0, drop=True)
    )

    return funding_data

