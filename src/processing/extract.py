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


# -----> Read in demographic data
def read_dem(): 
    dem_data = dict() 

    # (2019-2020)
    dem_1620 = read_data("./data/raw/demographics/2019-20_Demographic_Snapshot_-_School.xlsx", sheet_name="Data")
    for yr in range(19, 21): 
        dem_data[f"20{yr}"] = dem_1620.query(f"Year == '20{yr-1}-{yr}'")

    # (2021-2025)
    dem_2125 = read_data("./data/raw/demographics/demographic-snapshot-2020-21-to-2024-25-public.xlsx", sheet_name="School")
    for yr in range(21, 26): 
        dem_data[f"20{yr}"] = dem_2125.query(f"Year == '20{yr-1}-{yr}'")

    return dem_data 


# -----> Read in Fair Student Funding data
def read_fsf(): 
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
    
    return fsf_data


# -----> Read in PTA Fundraising data
def read_pta(): 
    pta_data = dict()

    for yr in range(19, 26): 
        pta_data[f"20{yr}"] = read_data(f"./data/raw/pta/20{yr-1}-{yr}-pta-financial-reporting.xlsx", sheet_name = "School")

    return pta_data
