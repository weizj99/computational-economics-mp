# Data

Three tables with one row per year, 1980–2023. They hold the series in De
Loecker, Eeckhout and Mongey (2026). Section, equation and figure numbers below
refer to the version of that paper dated September 4, 2026.

## Moments.csv

The three U.S. series that unit 03 matches (Section 4.1, equations 20–22).

| Column | Series | Source |
| --- | --- | --- |
| `rer_total` | Job reallocation rate, all employers | U.S. Census Bureau, Business Dynamics Statistics |
| `mu_w` | Markup α<sub>COGS</sub> · Sales / COGS, sales-weighted mean | Firms in Compustat |
| `mean_sga_tc_w` | SGA share SGA / (COGS + capital cost + SGA), sales-weighted mean | Firms in Compustat |

After a centred five-year moving average, these are the data lines in the
paper's Figure 2.

## boxes.csv

The search range used in unit 03 for each year: the lower limit (`_lo`) and
upper limit (`_hi`) of σ, N and ζ.

## Untargeted_Moment.csv

The data for unit 05. `markup_total` is the same sales-weighted markup as
`mu_w` above. The other three columns start from its 1980 value and add up,
year by year, one part of its change (equation 23): within firms
(`markup_within`), reallocation across firms (`markup_reallocation`) and net
entry (`markup_netentry`). After a centred five-year moving average, the four
columns are the lines in the paper's Figure 7A.

## How to cite

When you use these data, cite the paper and the underlying sources:

- De Loecker, Jan, Jan Eeckhout, and Simon Mongey. 2026. "Quantifying Market
  Power and Business Dynamism in the Macroeconomy." Federal Reserve Bank of
  Minneapolis Staff Report 688. https://doi.org/10.21034/sr.688
- U.S. Census Bureau. Business Dynamics Statistics.
- S&P Global Market Intelligence. Compustat North America.
