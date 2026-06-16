-- get number of flagged schools 
SELECT 
    YEAR, 
    COUNT(DISTINCT DBN) AS N_FLAGGED_SCHOOLS,
    SUM(BALANCE_WY_DIFF_FLAG),
    SUM(ETS_BALANCE_DIFF_FLAG),
    -- friendlier SQL syntax from DuckDB
    SUM(COLUMNS('any.*_w.*_flag'))
FROM FUNDING 
WHERE BALANCE_WY_DIFF_FLAG OR 
        ETS_BALANCE_DIFF_FLAG OR 
        ANY_WY_TRANSACTION_FLAG OR 
        ANY_WS_TRANSACTION_FLAG
GROUP BY ROLLUP(YEAR)
ORDER BY YEAR
; 


-- get top 15 most anomalous schools
SELECT 
    DBN, 
    SCHOOL_NAME_X, 
    -- average PTA financial values
    CAST(AVG(PTA_INCOME) AS DECIMAL(10, 1)) AS AVG_PTA_INCOME,
    CAST(AVG(PTA_EXPENDITURE) AS DECIMAL(10, 1)) AS AVG_PTA_EXPENDITURE,
    CAST(AVG(PTA_END_BALANCE) AS DECIMAL(10, 1)) AS AVG_PTA_END_BALANCE,
    -- sum of flags 
    SUM(BALANCE_WY_DIFF_FLAG) + SUM(ETS_BALANCE_DIFF_FLAG) + SUM(list_sum(list_value(*COLUMNS('pta.*flag')))) AS N_ANOMALIES,
    SUM(BALANCE_WY_DIFF_FLAG) AS N_BALANCE_WY_DIFF_FLAG, 
    SUM(ETS_BALANCE_DIFF_FLAG) AS N_ETS_BALANCE_DIFF_FLAG, 
    SUM(list_sum(list_value(*COLUMNS('pta.*_wy_transaction_flag')))) AS N_WY_TRANSACTION_FLAG,
    SUM(list_sum(list_value(*COLUMNS('pta.*_ws_transaction_flag')))) AS N_WS_TRANSACTION_FLAG
FROM FUNDING 
WHERE BALANCE_WY_DIFF_FLAG OR 
        ETS_BALANCE_DIFF_FLAG OR 
        ANY_WY_TRANSACTION_FLAG OR 
        ANY_WS_TRANSACTION_FLAG
GROUP BY DBN, SCHOOL_NAME_X
ORDER BY N_ANOMALIES DESC
LIMIT 15
; 


-- look at specific schools
SELECT 
    SCHOOL_NAME_X, 
    YEAR,
    PTA_START_BALANCE,
    PTA_INCOME,
    PTA_EXPENDITURE,
    PTA_END_BALANCE,
    COLUMNS('^.*flag')
FROM FUNDING 
WHERE SCHOOL_NAME_X IN (
    'P.S. 052 Sheepshead Bay', 
    'P.S. 029 John M. Harrigan', 
    'The Emily Warren Roebling School'
)
ORDER BY SCHOOL_NAME_X, YEAR
;


-- are well-funded PTAs more likely to have accounting errors / balance anomalies?


-- look at schools that were flagged as cross-year, within-school anomalies 
COPY (
    SELECT 
        SCHOOL_NAME_X, 
        YEAR, 
        PTA_START_BALANCE, 
        PTA_INCOME, 
        PTA_EXPENDITURE, 
        PTA_END_BALANCE
    FROM FUNDING
    WHERE ANY_WS_TRANSACTION_FLAG 
    ORDER BY SCHOOL_NAME_X, YEAR 
) TO "./data/processed/flagged_ws_transaction.csv" (HEADER, DELIMITER ',') 
;
