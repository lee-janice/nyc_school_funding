import contextlib
from pathlib import Path
import pandas as pd
import duckdb 


# =============================================================================
#  Define functions for anomaly analysis
# =============================================================================
def execute_queries(): 

    output_path = "./output/anomalies.txt"
    with open(output_path, "w") as f:

        conn = duckdb.connect("./data/processed/school_funding.db")
        sql_script = Path("./src/analysis/anomalies.sql").read_text()
        statements = duckdb.extract_statements(sql_script)

        with contextlib.redirect_stdout(f):
            # prevent print from breaking into multiple rows 
            pd.set_option('display.expand_frame_repr', False)

            for i, stmt in enumerate(statements, 1):
                result = conn.execute(stmt).df()
                print(f"{result}\n")
            
        print(f"\tAnomaly analysis output written to {output_path}!")


def investigate_end_balance_discrepancies(funding_data): 
    return