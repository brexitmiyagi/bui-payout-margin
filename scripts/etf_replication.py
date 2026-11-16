"""Why not just buy the ETF?

Replicates BUI's weekly NAV total return with the iShares Global Infrastructure ETF (IGF) and the iShares 7-10
Year Treasury ETF (IEF), both with distributions reinvested (Nasdaq dividend histories). The intercept, annualised,
is what BUI's manager added or lost after BUI's own 1.06% expenses, against an ETF mix you can buy for 0.15% to
0.37%. XLU is added in a second model to see how much more of BUI it explains. XLU's dividend history isn't on
Nasdaq, so XLU enters as a price return only and that model is used for fit, not for alpha.

Periods: the covered-call era (to 7 Nov 2025, BUI dropped call writing on 10 Nov 2025), the period since, the
last five years, and the whole sample.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
etf = pd.read_csv(os.path.join(DATA, "etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
ed = pd.read_csv(os.path.join(DATA, "etf_distributions.csv"), parse_dates=["ex_date"])
bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])


def tr_index(price, dists):
    price = price.dropna()
    div = pd.Series(0.0, index=price.index)
    for dt, a in dists.groupby("ex_date").amount.sum().items():
        i = price.index.searchsorted(dt)
        if 0 < i < len(price):
            div.iloc[i] += a
    r = (price + div) / price.shift(1) - 1
    return (1 + r.fillna(0)).cumprod()


idx = pd.DataFrame({
    "bui_nav": tr_index(bui.bui_nav, bd),
    "bui_px": tr_index(bui.bui_close, bd),
    "igf": tr_index(etf.igf_close, ed[ed.ticker == "IGF"]),
    "ief": tr_index(etf.ief_close, ed[ed.ticker == "IEF"]),
    "xlu_px": etf.xlu_close / etf.xlu_close.iloc[0],
}).dropna()
w = idx.resample("W-FRI").last().pct_change().dropna() * 100

periods = [("covered-call era, Nov 2016 to Nov 7 2025", "2016-11-18", "2025-11-07"),
           ("since dropping calls, Nov 14 2025 to Nov 13 2026", "2025-11-14", "2026-11-13"),
           ("last five years", "2021-11-19", "2026-11-13"),
           ("whole sample", "2016-11-18", "2026-11-13")]
rows = []
for lab, a, z in periods:
    x = w.loc[a:z]
    mA = sm.OLS(x.bui_nav, sm.add_constant(x[["igf", "ief"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    mB = sm.OLS(x.bui_nav, sm.add_constant(x[["igf", "ief", "xlu_px"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    alpha = mA.params["const"] * 52
    te = mA.resid.std() * np.sqrt(52)
    p("\n%s (%d weeks)" % (lab, len(x)))
    p("  BUI NAV = %.2f x IGF + %.2f x IEF; R2 %.2f; tracking error %.1f%% a year" %
      (mA.params["igf"], mA.params["ief"], mA.rsquared, te))
    p("  alpha after BUI's fees: %+.2f%% a year (t %.1f)" % (alpha, mA.tvalues["const"]))
    p("  adding XLU (price only): R2 %.2f, XLU weight %.2f" % (mB.rsquared, mB.params["xlu_px"]))
    yrs = len(x) / 52
    cum = lambda s: ((1 + x[s] / 100).prod() ** (1 / yrs) - 1) * 100
    p("  annualised: BUI NAV TR %.2f%%, BUI price TR %.2f%%, IGF TR %.2f%%, IEF TR %.2f%%" %
      (cum("bui_nav"), cum("bui_px"), cum("igf"), cum("ief")))
    rows.append({"period": lab, "weeks": len(x), "w_igf": round(mA.params["igf"], 2), "w_ief": round(mA.params["ief"], 2),
                 "r2": round(mA.rsquared, 2), "tracking_error_pct": round(te, 1), "alpha_after_fees_pct": round(alpha, 2),
                 "alpha_t": round(mA.tvalues["const"], 1), "r2_with_xlu": round(mB.rsquared, 2),
                 "bui_nav_tr_ann": round(cum("bui_nav"), 2), "igf_tr_ann": round(cum("igf"), 2)})
pd.DataFrame(rows).to_csv(os.path.join(RES, "etf_replication.csv"), index=False)
p("\nfees: BUI 1.06% (H1 2026 expense ratio), IGF 0.37%, IEF 0.15% (issuer pages, Nov 2026)."
  " Alpha above is after BUI's fees and before the ETFs' fees, which their total returns already carry.")
# tie-out: my IGF total return against iShares' published market-price returns to 30 Sep 2026
e = idx.igf.loc[:"2026-09-30"].iloc[-1]
for yrs, start, pub in [(5, "2021-09-30", 9.26), (1, "2025-09-30", 3.80)]:
    mine = ((e / idx.igf.loc[:start].iloc[-1]) ** (1 / yrs) - 1) * 100
    p("tie-out IGF %dy to 30 Sep 2026: mine %.2f%%, iShares market price %.2f%%" % (yrs, mine, pub))
    assert abs(mine - pub) < 0.15, "IGF total return rebuild is off"
open(os.path.join(RES, "etf_replication.txt"), "w").write("\n".join(out) + "\n")
