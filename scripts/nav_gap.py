"""The NAV return the quarter-end books can't explain, and what's behind it.

attribution.py finds BUI's NAV total return ran ahead of its priced holdings plus income less fees by about 0.4 points
in Q1 2026, 1.2 in Q2 and 0.8 from July to November 13. The candidates: trading inside the quarter, marking foreign
stocks to the New York close (fair value), currency, securities lending, and share issuance. Four checks:

1. The filed numbers. The N-CSRS for the half to June 30 reports realised plus unrealised gains per share. If BUI
   had held its December book untouched, the gains would be the December NAV times the buy-and-hold holdings return.
   The difference is gains the books can't see.
2. The cheap candidates, from the same statement of operations: securities lending income, withholding tax reclaims,
   and the rights offering (booked separately as dilution per share).
3. Fair value. About 25% of the book was Level 2 on June 30, which for BUI means foreign stocks marked to the New
   York close. If BUI used home-market closes instead, its NAV would pick up part of each US day's move a day late.
   Test: regress the daily NAV residual (after the priced US names and a foreign ETF) on today's and yesterday's
   S&P 500 return. A late mark shows up as a positive coefficient on yesterday.
4. Shape. Trading and one-off marks arrive in lumps; currency and income drift. So: what share of the residual comes
   from its ten biggest days, and how much of it lines up with the dollar?
"""
import os
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

# 1. filed numbers, half to June 30
fh = pd.read_csv(os.path.join(DATA, "financial_highlights.csv")).set_index("period").loc["H1 2026"]
att = pd.read_csv(os.path.join(RES, "attribution.csv")).set_index("piece")
h1 = (1 + att.loc["Q1 2026", "holdings"]) * (1 + att.loc["Q2 2026", "holdings"]) - 1
implied = fh.nav_begin * h1
p("1. half to June 30, per share: filed realised + unrealised gains $%.2f; buy-and-hold from the December book would"
  " give $%.2f (%.2f x %.1f%%); unexplained $%.2f, %.1f%% of the starting NAV" %
  (fh.realized_unrealized, implied, fh.nav_begin, h1 * 100, fh.realized_unrealized - implied,
   (fh.realized_unrealized - implied) / fh.nav_begin * 100))
p("   portfolio turnover in the half: %d%% (2025: 76%%), so a quarter of the book changed hands inside those six months"
  % fh.turnover_pct)

# 1b. the same check in dollars, because the per-share gains line in the financial highlights is a balancing figure
# and BUI issued about 2.4m shares in April. Statement of operations, six months to June 30, 2026: realised plus
# unrealised gains in dollars. Buy-and-hold in dollars: each quarter's starting net assets (N-PORT) times that quarter's
# buy-and-hold holdings return, plus the rights money ($64.7m in, April 2) earning the book's return from April 2 to
# June 30. For that piece I take Q2's holdings return net of the NAV's move from March 31 to April 2, which assumes the
# book moved with the NAV over those two days. Distributions paid out of the fund ($20.7m in the half) would lower the
# invested base a little; at most they're worth the half's return on half of that amount, shown as a bound.
so = pd.read_csv(os.path.join(DATA, "statement_totals.csv")).set_index("period").loc["H1 2026"]
gains = so.net_realized_gain + so.net_change_unrealized
na_dec, na_mar = 587822907.84, 662894158.16          # N-PORT net assets, Dec 31 2025 and Mar 31 2026
q1, q2 = att.loc["Q1 2026", "holdings"], att.loc["Q2 2026", "holdings"]
navs = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date").bui_nav
r_lead = navs.loc["2026-04-02"] / navs.loc["2026-03-31"] - 1
r_new = (1 + q2) / (1 + r_lead) - 1
bh = na_dec * q1 + na_mar * q2 + so.rights_offering_proceeds * r_new
dist_bound = so.distributions_total / 2 * h1
gap_usd = gains - bh
p("1b. in dollars: filed realised + unrealised $%.1fm; buy-and-hold $%.1fm (Q1 $%.1fm, Q2 $%.1fm, rights money $%.1fm"
  " at %.2f%%); gap $%.1fm, %.1f%% of average net assets, or $%.1fm after the most the payouts could account for" %
  (gains / 1e6, bh / 1e6, na_dec * q1 / 1e6, na_mar * q2 / 1e6, so.rights_offering_proceeds * r_new / 1e6, r_new * 100,
   gap_usd / 1e6, gap_usd / ((591048563 + 741864850) / 2) * 100, (gap_usd - dist_bound) / 1e6))
sh_dec, sh_jun = na_dec / fh.nav_begin, 26548823                  # Dec 31 from net assets / NAV; Jun 30 from the N-CSRS
sh_avg = (sh_dec * 3 + sh_jun * 3) / 6                               # new shares arrived on April 2, half-way through
p("   per share that's about $%.2f on %.1fm average shares, against the $%.2f from the financial highlights, so the"
  " balancing-figure problem doesn't make the gap go away" % (gap_usd / sh_avg, sh_avg / 1e6, fh.realized_unrealized - implied))

# 2. cheap candidates (N-CSRS statement of operations, six months to June 30, 2026; BUI column)
st = {"securities lending income, net": 1406, "foreign withholding tax claims": 328712,
      "IRS fee on those claims": -87340, "total investment income": 9374768}
na_avg = (591048563 + 741864850) / 2
p("2. securities lending $%s, %.3f%% of average net assets; tax reclaims net of fee $%s, %.3f%%; total investment"
  " income %.2f%% for the half" % (f"{st['securities lending income, net']:,}", st["securities lending income, net"] / na_avg * 100,
  f"{st['foreign withholding tax claims'] + st['IRS fee on those claims']:,}",
  (st["foreign withholding tax claims"] + st["IRS fee on those claims"]) / na_avg * 100, st["total investment income"] / na_avg * 100))
p("   rights offering: booked as -$%.2f a share of dilution, so it pushes the gap the other way" % -fh.rights_dilution)

# 3 and 4. daily residual
NPORT = {"2025-12-31": "0001410368-26-016995", "2026-03-31": "0001410368-26-054529", "2026-06-30": "0001410368-26-085641"}
hmap = pd.read_csv(os.path.join(DATA, "holdings_map.csv")).set_index("isin")
lp = pd.read_csv(os.path.join(DATA, "listed_holdings_daily_2025_2026.csv"), parse_dates=["date"]).set_index("date")
bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
etf = pd.read_csv(os.path.join(DATA, "etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
dist = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"]).groupby("ex_date").amount.sum()


def weights(date):
    root = ET.parse(os.path.join(DATA, "nport", NPORT[date] + ".xml")).getroot()
    N = root.tag.split("}")[0][1:]
    w = {}
    for s in root.iter("{%s}invstOrSec" % N):
        isin = [x.get("value") for x in s.find("{%s}identifiers" % N) if x.tag.endswith("isin")]
        tk = hmap.us_ticker.get(isin[0]) if isin else None
        if isinstance(tk, str) and tk in lp:
            w[tk] = w.get(tk, 0) + float(s.find("{%s}pctVal" % N).text) / 100
    return pd.Series(w)


segs = [("2025-12-31", "2026-03-31"), ("2026-03-31", "2026-06-30"), ("2026-06-30", "2026-11-13")]
parts = []
for a, z in segs:
    w = weights(a)
    px = lp[w.index].loc[a:z].ffill()
    ok = px.iloc[0].notna()
    w, px = w[ok], px.loc[:, ok]
    v = (px / px.iloc[0]).mul(w.values, axis=1).sum(axis=1) / w.sum()
    parts.append(pd.DataFrame({"listed": v.pct_change(), "listed_w": w.sum()}).iloc[1:])
L = pd.concat(parts)
nav = bui.bui_nav
navr = (nav + dist.reindex(nav.index).fillna(0)) / nav.shift(1) - 1
d = pd.DataFrame({"nav": navr, "listed": L.listed, "igf": etf.igf_close.pct_change(),
                  "spy": bui.spy_close.pct_change()}).dropna()
d["spy_lag"] = d.spy.shift(1)
d = d.dropna()
m = sm.OLS(d.nav, sm.add_constant(d[["listed", "igf"]])).fit()
d["resid"] = m.resid
t = sm.OLS(d.resid, sm.add_constant(d[["spy", "spy_lag"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
p("3. daily, %s to %s (%d days): NAV on priced US names and IGF, R2 %.2f. Residual on the S&P 500: today %.3f (t %.1f),"
  " yesterday %.3f (t %.1f)" % (d.index[0].date(), d.index[-1].date(), len(d), m.rsquared, t.params.spy, t.tvalues.spy,
  t.params.spy_lag, t.tvalues.spy_lag))
p("   a late mark on the foreign third would show up as a positive yesterday coefficient; it isn't there, which fits"
  " BUI fair-valuing foreign stocks to the New York close")
# for the shape, use fixed weights instead of fitted ones (a fitted residual sums to zero by construction):
# priced US names at their N-PORT weight, the rest of the book at IGF, less income net of fees accruing daily
lw = L.listed_w.reindex(d.index).ffill()
g = d.nav - (lw * d.listed + (1 - lw) * d.igf) - (2.8 - 1.06) / 100 / 252
cum = g.sum() * 100
top = g.abs().sort_values(ascending=False).head(10)
p("4. fixed-weight residual, cumulative %+.1f points; the ten biggest days sum to %+.1f, the other %d days to %+.1f" %
  (cum, g[top.index].sum() * 100, len(g) - 10, (g.sum() - g[top.index].sum()) * 100))
p("   biggest days: " + ", ".join("%s %+.2f" % (i.date(), g[i] * 100) for i in top.index[:6]))
q = g.groupby(pd.PeriodIndex(g.index, freq="Q")).sum() * 100
p("   by quarter: " + ", ".join("%s %+.1f" % (k, v) for k, v in q.items()))
p("\nreading: the half to June 30 has about 2 points of gains that a buy-and-hold book can't produce, a quarter of the"
  " book turned over, securities lending and tax reclaims are each under 0.05%, the rights offering cut NAV, and"
  " there's no sign of late foreign marks. What's left is consistent with gains from trading inside the quarter; the filings can't prove it was skill rather than timing. Currency can't be"
  " separated from stock moves for the unpriced foreign names until September's N-PORT is out.")
d["fixed_resid"] = g
d["fixed_resid_cum_pts"] = g.cumsum() * 100
d.to_csv(os.path.join(RES, "nav_gap_daily.csv"))
open(os.path.join(RES, "nav_gap.txt"), "w").write("\n".join(out) + "\n")
