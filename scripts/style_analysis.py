"""Constrained style analysis: does BUI beat a mix of ETFs that looks like its actual book?

Sharpe-style regression of weekly NAV total returns on ETF returns, weights forced to be zero or positive and to
sum to one, intercept free. Two ETF sets:

  book-like: XLU (utilities), IGF (global infrastructure), AMLP (pipelines), XLI (industrials), IEF (Treasuries).
    Nasdaq has no dividend history for XLU, AMLP and XLI, so they enter as price returns and the alpha is then
    reduced by weight x each ETF's trailing distribution yield from its issuer page (XLU 2.77%, AMLP 8.10%,
    XLI 1.11%, November 2026). That's an approximation: yields moved over the decade.
  total-return clean: IGF, PUI (US utilities), GRID (grid equipment), IEF, all with Nasdaq distributions.

Run for BUI and for the NAVs of UTF, DNP and GLU, by period. Then a power check: with this tracking error, how many
years would it take for an alpha of this size to reach t = 2?
"""
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
fac = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
etf = pd.read_csv(os.path.join(DATA, "etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
ed = pd.read_csv(os.path.join(DATA, "etf_distributions.csv"), parse_dates=["ex_date"])
bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
pdist = pd.read_csv(os.path.join(DATA, "peer_distributions.csv"), parse_dates=["ex_date"])
YIELD = {"xlu": 2.77, "amlp": 8.10, "xli": 1.11}


def tr(price, dists=None):
    price = price.dropna()
    div = pd.Series(0.0, index=price.index)
    if dists is not None:
        for dt, a in dists.groupby("ex_date").amount.sum().items():
            i = price.index.searchsorted(dt)
            if 0 < i < len(price):
                div.iloc[i] += a
    return (((price + div) / price.shift(1)).fillna(1)).cumprod()


L = pd.DataFrame({
    "BUI": tr(bui.bui_nav, bd),
    "UTF": tr(fac.utf_nav, pdist[pdist.ticker == "UTF"]),
    "DNP": tr(fac.dnp_nav, pdist[pdist.ticker == "DNP"]),
    "GLU": tr(fac.glu_nav, pdist[pdist.ticker == "GLU"]),
    "xlu": tr(etf.xlu_close), "amlp": tr(etf.amlp_close), "xli": tr(etf.xli_close),
    "igf": tr(etf.igf_close, ed[ed.ticker == "IGF"]), "ief": tr(etf.ief_close, ed[ed.ticker == "IEF"]),
    "pui": tr(etf.pui_close, ed[ed.ticker == "PUI"]), "grid": tr(etf.grid_close, ed[ed.ticker == "GRID"]),
}).dropna()
W = L.resample("W-FRI").last().pct_change().dropna() * 100

SETS = {"book-like": ["xlu", "igf", "amlp", "xli", "ief"], "total-return clean": ["igf", "pui", "grid", "ief"]}


def style(y, X):
    n = X.shape[1]
    def sse(w):
        r = y - X @ w
        return ((r - r.mean()) ** 2).sum()
    cons = ({"type": "eq", "fun": lambda w: w.sum() - 1},)
    res = minimize(sse, np.full(n, 1 / n), bounds=[(0, 1)] * n, constraints=cons, method="SLSQP")
    w = res.x
    resid = y - X @ w
    return w, resid.mean(), resid


rng = np.random.default_rng(11)
periods = [("last five years", "2021-11-19", "2026-11-13"), ("since BUI dropped calls", "2025-11-14", "2026-11-13"),
           ("covered-call era", "2016-11-18", "2025-11-07"), ("whole sample", "2016-11-18", "2026-11-13")]
rows = []
for fund in ["BUI", "UTF", "DNP", "GLU"]:
    for sname, cols in SETS.items():
        for plab, a, z in periods:
            if fund != "BUI" and plab in ("since BUI dropped calls", "covered-call era"):
                continue
            x = W.loc[a:z]
            y, X = x[fund].values, x[cols].values
            w, a_w, resid = style(y, X)
            alpha = a_w * 52
            adj = sum(w[i] * YIELD[c] for i, c in enumerate(cols) if c in YIELD)
            alpha_tr = alpha - adj
            te = resid.std(ddof=1) * np.sqrt(52)
            r2 = 1 - resid.var() / y.var()
            # block bootstrap (8-week blocks) for a 90% band on alpha, weights held fixed
            n = len(resid)
            boots = []
            for _ in range(2000):
                idx = np.concatenate([np.arange(s, min(s + 8, n)) for s in rng.integers(0, n, n // 8 + 1)])[:n]
                boots.append(resid[idx].mean() * 52 - adj)
            lo, hi = np.percentile(boots, [5, 95])
            yrs_needed = (2 * te / abs(alpha_tr)) ** 2 if alpha_tr != 0 else np.inf
            rows.append({"fund": fund, "set": sname, "period": plab, "weeks": n,
                         **{f"w_{c}": round(w[i], 2) for i, c in enumerate(cols)},
                         "r2": round(r2, 2), "tracking_error": round(te, 1),
                         "alpha_after_fees": round(alpha_tr, 2), "alpha_90_lo": round(lo, 2), "alpha_90_hi": round(hi, 2),
                         "years_for_t2": round(yrs_needed, 0)})
t = pd.DataFrame(rows)
t.to_csv(os.path.join(RES, "style_analysis.csv"), index=False)
show = ["fund", "set", "period", "weeks", "r2", "tracking_error", "alpha_after_fees", "alpha_90_lo", "alpha_90_hi", "years_for_t2"]
p(t[show].to_string(index=False))
p("\nweights, BUI, book-like set:")
p(t[(t.fund == "BUI") & (t.set == "book-like")][["period", "w_xlu", "w_igf", "w_amlp", "w_xli", "w_ief"]].to_string(index=False))
p("\nweights, BUI, total-return clean set:")
p(t[(t.fund == "BUI") & (t.set == "total-return clean")][["period", "w_igf", "w_pui", "w_grid", "w_ief"]].to_string(index=False))
p("\npower: to detect a 1-point annual edge at t = 2 with 5% tracking error takes (2 x 5 / 1)^2 = 100 years of weekly data")
open(os.path.join(RES, "style_analysis.txt"), "w").write("\n".join(out) + "\n")
