import pandas as pd
import numpy as np

# =============================================================================
#  Define functions for descriptives
# =============================================================================
# -----> Calculate counts by category
def category_counts(df, category_col): 
    return (
        df
        .groupby(["year", category_col])
        .size()
        .unstack(fill_value=0)
    )

# -----> Calculate means by category
def mean_by_category(df, category_cols, value_cols, roundby=2): 
    return (
        df
        .groupby(category_cols)[value_cols]
        .mean()
        .round(roundby)
        .unstack(level=1)
    )

# -----> Calculate medians by category 
def median_by_category(df, category_cols, value_cols, roundby=2): 
    return (
        df
        .groupby(category_cols)[value_cols]
        .median()
        .round(roundby)
        .unstack(level=1)
    )

# -----> Get top N rows by value 
def top_n_by_col(df, value_col, n, keep_cols): 
    return (
        df
        .sort_values(by=value_col, ascending=False)
        .head(n)
        .filter(items=keep_cols)
    )

