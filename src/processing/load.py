import sqlite3

# =============================================================================
#  Define functions for loading data 
# =============================================================================
def write_to_db(df, db, name): 
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # write to db
    df.to_sql(name=name, con=conn, if_exists="replace", index=False)

    # get number of obs
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    result = cursor.fetchone()

    print(f"\t{result[0]} rows successfully written to {db} at table {name}.")

    conn.close()

def write_to_csv(df, path): 
    df.to_csv(path)
    print(f"\tData written to CSV at {path}.")