# NYC Public Schools Funding Analysis

In this project, I analyzed Parent Teacher Association (PTA) fundraising and expenditure data
across New York City Public Schools (NYCPS), which were made available by the transparency
mandates of Local Law 171 of 2018. While public schools are primarily funded through the 
city’s equity- and needs-based Fair Student Funding (FSF) formula, private PTA contributions remain 
largely opaque and in some cases, incredibly unequal. These stark inequities
create funding gaps that closely mirror socioeconomic and racial segregation.

## Key results

### Severe financial inequities

* As expected, PTA funding is hyper-concentrated in wealthiest schools. For example, in 2024-25,
  the median PTA per-pupil expenditure was $19. However, the 95th percentile school spent $471 per-pupil,
  the 99th spent $1,293, and the highest spending school spent $2,738 for each enrolled student.
* In the wealthiest schools, this expenditure acted almost as a "shadow budget" - schools like
  P.S. 029 John M. Harrigan and P.S. 158 Bayard Taylor spent private PTA funds worth 25% and 23% of their
  entire public FSF allocation, respectively.

## Socioeconomic and demographic stratification

* There is a clear negative linear relationship (OLS slope = -6.81) between students' economic need (measured by the
  NYCPS-created Economic Need Index, or ENI).
* Schools in the highest PTA expenditure quantile have a drastically higher share of White and Asian students
  compared to the lowest quantile, which is predominantly composed of Hispanic and Black students.

### Data anomalies

* The publicly available PTA fundraising data had a substantial number of accounting anomalies, like
    * cross-year discrepancies between ending balances in Y0 and starting balances in Y1
    * within-year discrepancies between the implied ending balance (`starting balance + income - expenditures`), and the reported ending balance
    * accounting errors like values expressed in cents rather than dollars
* In particular, the cross-year balance discrepancies - where the previous year's ending balance differed from the starting balance by over $50,000 - were highly concentrated in the schools with the wealthiest PTAs.


## Cross-sectional 2024-25 profile 
<img src="output/figures/fig7_top_schools_annotated.png" width="600">

<img src="output/figures/fig4_expenditure_percentiles.png" width="600">

<img src="output/figures/fig6_eni_vs_expenditure.png" width="600">

<img src="output/figures/fig5_racial_comp_by_pta.png" width="600">

## Trends between 2018-19 and 2024-25 

<img src="output/figures/fig3_quintile_trends.png" width="600">

## Anomaly analysis

<img src="output/figures/fig1c_balance_flag_vs_expenditure_hist.png" width="600">
<img src="output/figures/fig2c_transaction_flag_vs_expenditure_hist.png" width="600">



