# Lever: direct public employment

The government hires directly in public services with budget B (% of
GDP). The budget splits, data-derived, by the public-services sector's
own labour share (compensation / output):
- a **wage component** = labour_share x B creating direct jobs at the
  sector's internal compensation per worker (direct jobs = budget x the
  public-services employment coefficient); the wage bill is Type
  II-eligible (recycled through the household closure when the toggle is
  on);
- a **non-wage operating component** = (1 - labour_share) x B injected
  across the public-services input column (domestic A_d column).

Fiscal cost = the full budget (financing drag default on, so net < gross
when on -- tested). Like public works, results are JOB-YEARS.
