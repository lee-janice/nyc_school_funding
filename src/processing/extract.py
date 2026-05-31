import pandas as pd
from pathlib import Path

# =============================================================================
#  Define functions for reading in data 
# =============================================================================
def read_data(path, sheet_name=None, skiprows=None): 
    path_object = Path(path)

    match path_object.suffix.lower(): 
        case ".xlsx" | ".xls": 
            return pd.read_excel(path_object, sheet_name=sheet_name, skiprows=skiprows)
        case ".csv": 
            return pd.read_csv(path_object)
        case _: 
            print(f"Unknown filetype: {path_object.suffix}")
            return None


