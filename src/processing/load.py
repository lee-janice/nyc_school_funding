import duckdb
import numpy as np
import pandas as pd

# =============================================================================
#  Define functions for loading data 
# =============================================================================
def write_to_db(df, db, table_name, drop=False): 

    with duckdb.connect(db) as conn:

        if drop: 
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")

        # write the dataframe to the database file
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df;")
        
        # print number of rows written
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        print(f"\t{result[0]} rows successfully written to {db} at table {table_name}.")


def write_to_csv(df, path): 
    df.to_csv(path)
    print(f"\tData written to CSV at {path}.")