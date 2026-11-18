"""Which vehicle for utility exposure? BUI, UTF, DNP, GLU, XLU and IGF side by side, every number from one
source per field and dated 13 November 2026.

Prices and NAVs: Nasdaq (fund closes and X-ticker NAVs). Fees: fund reports and issuer pages. Yields: latest
regular distribution x 12 over the Nov 13 price for the CEFs; issuer trailing yields for the ETFs.
Rate beta: 2026 weekly Friday-to-Friday regression on the 10-year change, RSP, SMH and USO (same as
rate_beta_tests.py), HAC t-stats. Edge: constrained style alpha after fees from style_analysis.py.
Liquidity: median daily dollar volume, last 63 sessions.
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
fac = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
etf = pd.read_csv(os.path.join(DATA, "etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
veh = pd.read_csv(os.path.join(DATA, "vehicle_prices_volumes_daily.csv"), parse_dates=["date"]).set_index("date")
bo = pd.read_csv(os.path.join(DATA, "bui_ohlcv_daily.csv"), parse_dates=["date"]).set_index("date")
uo = pd.read_csv(os.path.join(DATA, "utf_ohlcv_daily.csv"), parse_dates=["date"]).set_index("date")
y = pd.read_csv(os.path.join(DATA, "dgs10.csv"))
y.columns = ["date", "y"]
y["date"] = pd.to_datetime(y.date)
y = y.set_index("date").y.replace(".", np.nan).astype(float)
bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
sty = pd.read_csv(os.path.join(RES, "style_analysis.csv"))

# BUI NAV total return index, as in rate_beta_tests.py
nav = bui.bui_nav
div = pd.Series(0.0, index=nav.index)
for dtt, a in bd.groupby("ex_date").amount.sum().items():
    i = nav.index.searchsorted(dtt)
    if 0 < i < len(nav):
        div.iloc[i] += a
bui_tr = ((nav + div) / nav.shift(1)).fillna(1).cumprod()

S = pd.DataFrame({"BUI": bui_tr, "UTF": fac.utf_nav, "DNP": fac.dnp_nav, "GLU": fac.glu_nav, "XLU": etf.xlu_close,
                  "IGF": etf.igf_close, "rsp": fac.rsp_close, "smh": fac.smh_close, "uso": fac.uso_close, "y10": y}).dropna()
S = S[S.index.weekday == 4]
Wk = S.pct_change()
Wk["dy"] = S.y10.diff()
Wk = Wk.dropna().loc["2026"]
beta = {}
for f in ["BUI", "UTF", "DNP", "GLU", "XLU", "IGF"]:
    r = sm.OLS(Wk[f], sm.add_constant(Wk[["dy", "rsp", "smh", "uso"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    beta[f] = (r.params["dy"] * 100, r.tvalues["dy"])

d = pd.Timestamp("2026-11-13")
price = {"BUI": bui.bui_close[d], "UTF": fac.utf_price[d], "DNP": veh.dnp_close[d], "GLU": fac.glu_price[d],
         "XLU": etf.xlu_close[d], "IGF": etf.igf_close[d]}
navs = {"BUI": bui.bui_nav[d], "UTF": fac.utf_nav[d], "DNP": fac.dnp_nav[d], "GLU": fac.glu_nav[d]}
# Costs on one basis, in two columns. Without leverage: management and operating costs. With leverage: plus interest
# on borrowings. GLU's leverage is preferred stock, whose dividends aren't an expense, so it has no second figure.
# BUI: H1 2026 N-CSRS. UTF: H1 2026 N-CSRS. DNP: FY to Oct 31 2025 N-CSR ("Operating expenses, without leverage"
# 0.95%, "Operating expenses" 2.53%). GLU: H1 2026 N-CSRS, annualised. ETFs: issuer pages, November 2026.
fee_ex = {"BUI": "1.06%", "UTF": "1.33%", "DNP": "0.95%", "GLU": "1.13%", "XLU": "0.08%", "IGF": "0.37%"}
fee_lev = {"BUI": "1.06% (no leverage)", "UTF": "3.03%", "DNP": "2.53%", "GLU": "n/a (preferred, not an expense)",
           "XLU": "0.08%", "IGF": "0.37%"}
yld = {"BUI": 0.154 * 12 / price["BUI"] * 100, "UTF": 0.165 * 12 / price["UTF"] * 100,
       "DNP": 0.065 * 12 / price["DNP"] * 100, "GLU": 0.11 * 12 / price["GLU"] * 100, "XLU": 2.77, "IGF": 2.93}
dv = lambda c, v: (c * v).iloc[-63:].median() / 1e6
liq = {"BUI": dv(bo.close, bo.volume), "UTF": dv(uo.close, uo.volume),
       "DNP": dv(veh.dnp_close, veh.dnp_volume), "GLU": dv(veh.glu_close, veh.glu_volume),
       "XLU": dv(etf.xlu_close, veh.xlu_volume.reindex(etf.index)), "IGF": dv(etf.igf_close, veh.igf_volume.reindex(etf.index))}
rows = []
for f in ["BUI", "UTF", "DNP", "GLU", "XLU", "IGF"]:
    if f in navs:
        e = sty[(sty.fund == f) & (sty.set == "book-like") & (sty.period == "last five years")].iloc[0]
        edge = "%+.1f%% (90%%: %+.1f to %+.1f)" % (e.alpha_after_fees, e.alpha_90_lo, e.alpha_90_hi)
        disc = "%+.2f%%" % ((price[f] / navs[f] - 1) * 100)
    else:
        edge, disc = "benchmark", "n/a (ETF)"
    rows.append({"vehicle": f, "cost_ex_leverage": fee_ex[f], "cost_with_leverage": fee_lev[f], "yield_on_price": "%.2f%%" % yld[f], "premium_discount": disc,
                 "rate_beta_2026": "%.1f (t %.1f)" % beta[f], "edge_vs_book_like_mix_5y": edge,
                 "median_daily_dollar_volume": "$%.1fm" % liq[f]})
t = pd.DataFrame(rows)
p(t.to_string(index=False))
t.to_csv(os.path.join(RES, "vehicle_table.csv"), index=False)
open(os.path.join(RES, "vehicle_table.txt"), "w").write("\n".join(out) + "\n")
