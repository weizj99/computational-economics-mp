# 05 Untargeted moment: the markup decomposition

**Given:** the annual estimates from unit 03
(`modules/03_estimation/assets/annual_parameters.csv`), the solver in
`07_python/qmp`, and the data in `data/Untargeted_Moment.csv`. **Find:** the
model's split of the change in the sales-weighted markup into within-firm
change, reallocation and net entry, cumulated from 1980. **Check:** each of the
six exercises below ends with a folded answer.

The finished code is `lessons/05_untargeted/decompose_markup.py`, with the
decomposition in `07_python/qmp/untargeted.py`. Write your own version first
and use these files to check it. The unit's download,
`computational-economics-05.zip`, contains all the files named here. The whole exercise takes about 18 core-minutes
of computing; a laptop with four cores needs about 5 minutes.

1. **The decomposition.** For each of the three parts, say in one sentence
   what kind of change in firms it measures. Then explain why the model passing
   or failing this comparison says something about the model, given that the
   estimation never used it.

   <details>
   <summary>Check your result</summary>

   Within firms: continuing firms change their own markups, weighted by their
   earlier sales shares. Reallocation: sales shares move among continuing firms,
   toward or away from firms whose markups are above the earlier average,
   including the term where shares and markups change together. Net entry:
   entrants with markups above the earlier average raise it, and exiting firms
   with markups above it lower it. The estimation chose the parameters to match
   the level of the markup, not how its change splits, so a match supports the
   model's mechanism and a miss shows where it falls short.

   </details>

2. **Solve each year again.** For every year, solve the economy at its unit 03
   estimate, with the same random numbers as the estimation: NumPy PCG64 with
   seed 100, drawn once for each M = floor(N). Keep the period-1 markups,
   shares, prices and quantities.

   <details>
   <summary>Check your result</summary>

   The three moments of every year match the saved ones in
   `annual_parameters.csv`, to the last digit if each process uses one
   linear-algebra thread (`OPENBLAS_NUM_THREADS=1`). `decompose_markup.py` prints
   "Largest difference from unit 03's saved moments: 0".

   </details>

3. **Connect firms across years.** Slot (i, j) is the same firm in two years
   only if both years draw the same random numbers. Find the pairs of adjacent
   years in which M changes.

   <details>
   <summary>Check your result</summary>

   27 of the 43 pairs: those ending in 1986–1996, 1998, 2000–2003, 2006,
   2008–2011, 2013–2016, 2020 and 2022.

   </details>

4. **Decompose and cumulate.** Split each pair of adjacent years into the three
   parts and check that they add up to the change in the sales-weighted markup.
   Starting from the 1980 markup, add up each part over the years. Smooth the
   levels with a centred five-year moving average whose window shrinks near the
   ends.

   <details>
   <summary>Check your result</summary>

   The largest adding-up error is below 10⁻¹⁵ (4.04 × 10⁻¹⁶ in the saved run). The
   model's markup is 1.3342 in 1980 and 1.5758 in 2023. From 1980 to 2023, before
   smoothing, the model's total rises by 0.242: −0.071 within firms, +0.254 from
   reallocation and +0.059 from net entry.

   </details>

5. **Compare with the data.** Draw three panels: the data, the model, and the
   model shifted so that its smoothed total starts at the data's smoothed 1980
   value, 1.21. Which parts does the model match? Why does reallocation give the
   largest part of the rise? How much of the model's rise falls in the pairs
   with new draws?

   <details>
   <summary>Check your result</summary>

   The model matches the main fact: reallocation gives the largest part of the
   rise, +0.327 in the data and +0.254 in the model, because sales move toward
   firms with above-average markups; net entry adds a little in both, +0.043 and
   +0.059. It misses in two ways: its within-firm part falls by 0.071 while the
   data's rises by 0.012, and its total rise, 0.242, is smaller than the data's,
   0.382. Of the model's rise, 0.20 falls in the pairs with new draws; in the 16
   pairs that keep the same firms, the total rises by 0.04 and reallocation alone
   by 0.06.

   </details>

6. **The markup floor.** A firm's markup cannot fall below η/(η − 1) with
   η = 4.36875. Compute this floor and compare it with the data's markup in
   1980. What does the floor do to the model's markup and to the estimated N in
   1980–84? Look up N in `annual_parameters.csv` and the upper limits in
   `data/boxes.csv`.

   <details>
   <summary>Check your result</summary>

   The floor is 4.36875 / 3.36875 = 1.297, and the data's markup in 1980 is 1.20,
   below it, so the model cannot reach the data. The estimation pushes the markup
   down with many firms per market: in 1980–84 the estimated N is between 59.4 and
   59.6, just under the upper limit of 60, and the model's markup stays at about
   1.33 (1.3342 in 1980).

   </details>

