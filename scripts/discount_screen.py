"""What discount should a fund trade at, given what it pays, what it earned, its leverage, size and costs?

Cross-section of 108 US-listed equity CEFs from CEF Connect on 13 November 2026 (commodity trusts left out).
The residual is the part of the discount the fundamentals do not explain. Positive means the fund trades richer
than its fundamentals say, negative means cheaper. Then the utility and infrastructure funds are ranked, with
their own one-year discount z-score and three-month discount change next to them, so the screen can be rerun
every month on a fresh pull.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")

u = pd.read_csv(os.path.join(DATA, "equity_cef_universe_2026_11_13.csv"))
u["leverage_pct"] = u.leverage_pct.fillna(0)
u["log_assets"] = np.log(u.total_assets_musd)
X = sm.add_constant(u[["dist_rate_nav_pct", "nav_return_1y_pct", "leverage_pct", "log_assets", "expense_ratio_pct"]])
m = sm.OLS(u.discount_pct, X).fit(cov_type="HC1")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
p("n = %d funds, R2 %.2f" % (int(m.nobs), m.rsquared))
for k in m.params.index:
    p("  %-20s %+.3f  (t %.1f)" % (k, m.params[k], m.tvalues[k]))

u["fitted"] = m.fittedvalues
u["residual"] = u.discount_pct - u.fitted
z = pd.read_csv(os.path.join(DATA, "cef_discount_zscores_1y_2026_11.csv"))
group = ["BUI", "UTF", "UTG", "GLU", "DPG", "DNP", "MEGI", "RFI", "HTD", "ECF", "GUT", "TYG", "KYN", "NML", "EMO"]
g = u[u.ticker.isin(group)].merge(z[["ticker", "z_1y", "change_63d"]], on="ticker", how="left")
g = g.sort_values("residual")
cols = ["ticker", "discount_pct", "fitted", "residual", "dist_rate_nav_pct", "nav_return_1y_pct",
        "leverage_pct", "expense_ratio_pct", "z_1y", "change_63d"]
p("\nutility, infrastructure and energy-infrastructure funds, cheapest residual first:")
p(g[cols].round(2).to_string(index=False))
missing = [t for t in group if t not in set(u.ticker)]
p("not in the cross-section (missing a field or an outlier): %s" % ", ".join(missing))
g[cols].round(2).to_csv(os.path.join(RES, "utility_cef_screen.csv"), index=False)
open(os.path.join(RES, "discount_screen.txt"), "w").write("\n".join(out) + "\n")
