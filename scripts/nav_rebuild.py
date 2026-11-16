"""Rebuild BUI's NAV day by day from the 30 June 2026 N-PORT book and compare it with the NAV BlackRock reports.

The US and Canada-listed names (plus National Grid through its NYSE ADR) are priced daily from their own closes.
Everything else (the European and Asian names, cash, other assets) is held flat, so the rebuilt series is a lower
bound on how much of the fund I can explain with public closing prices. Foreign stocks in this fund are Level 2 in
the N-PORT, which means they are fair-valued to the 4pm New York close rather than carried at their home-market close.

Second half: is BUI's weekly rate beta bigger than its daily one because of the NAV, or because the market itself
takes more than a day to price a rate move? XLU has no NAV, so if XLU shows the same gap the answer is the market.
"""
import os
import csv
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")

ns = {"n": "http://www.sec.gov/edgar/nport"}
root = ET.parse(os.path.join(DATA, "nport", "0001410368-26-085641.xml")).getroot()
net = float(root.find(".//n:netAssets", ns).text)
val = {}
lvl = {}
for s in root.findall(".//n:invstOrSec", ns):
    nm = s.find("n:name", ns).text
    val[nm] = float(s.find("n:valUSD", ns).text)
    fl = s.find("n:fairValLevel", ns)
    lvl[nm] = fl.text if fl is not None else ""

out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

lv = pd.Series(val)
p("30 Jun 2026 net assets $%.1fm; securities $%.1fm" % (net / 1e6, lv.sum() / 1e6))
for k in ["1", "2", "3"]:
    v = sum(val[n] for n in val if lvl[n] == k)
    p("  Level %s: $%.1fm, %.1f%% of net assets" % (k, v / 1e6, v / net * 100))

mapping = {r["ticker"]: r["nport_name"] for r in csv.DictReader(open(os.path.join(DATA, "listed_holdings_prices.csv")))}
px = pd.read_csv(os.path.join(DATA, "listed_holdings_daily_2026h2.csv"), parse_dates=["date"]).set_index("date")
px = px.loc["2026-06-30":].ffill()
w = pd.Series({t: val[mapping[t]] for t in mapping if t in px.columns})
covered = w.sum()
p("priced daily: %d names, $%.1fm, %.1f%% of net assets" % (len(w), covered / 1e6, covered / net * 100))

rel = px[w.index] / px[w.index].iloc[0]
sleeve = (rel * w).sum(axis=1)
rebuilt_nav = sleeve + (net - covered)          # everything else flat
rebuilt_ret = rebuilt_nav / rebuilt_nav.iloc[0] - 1

bui = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
nav = bui.bui_nav.loc["2026-06-30":]
dist = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
# add back distributions so the reported series is a NAV total return, like the rebuild
add = pd.Series(0.0, index=nav.index)
for _, r in dist.iterrows():
    if nav.index[0] < r.ex_date <= nav.index[-1]:
        add.loc[nav.index[nav.index.searchsorted(r.ex_date)]:] += r.amount
nav_tr = (nav + add) / nav.iloc[0] - 1

j = pd.DataFrame({"rebuilt": rebuilt_ret, "reported": nav_tr}).dropna()
p("\n30 Jun -> %s: reported NAV total return %.2f%%, rebuilt (foreign/cash flat) %.2f%%, gap %.2f pts" %
  (j.index[-1].date(), j.reported.iloc[-1] * 100, j.rebuilt.iloc[-1] * 100,
   (j.reported.iloc[-1] - j.rebuilt.iloc[-1]) * 100))

# daily return match. Ex-dates are already handled by adding the payout back.
dr = pd.DataFrame({"rebuilt": (1 + j.rebuilt).pct_change(), "reported": (1 + j.reported).pct_change()}).dropna()
X = np.column_stack([np.ones(len(dr)), dr.rebuilt])
b = np.linalg.lstsq(X, dr.reported, rcond=None)[0]
res = dr.reported - X @ b
r2 = 1 - res.var() / dr.reported.var()
p("daily: reported on rebuilt slope %.2f, R2 %.2f, residual sd %.2f%% a day (%d days)" %
  (b[1], r2, res.std() * 100, len(dr)))
p("  scaled to the whole fund the slope should be near %.2f if the unpriced sleeve moved with the priced one" %
  (net / covered))
big = res.abs().sort_values(ascending=False).head(5)
p("  largest unexplained days (reported minus fitted, pts):")
for d, _ in big.items():
    p("   ", d.date(), "%+.2f" % (res.loc[d] * 100))

# biggest contributors to the priced sleeve since 30 June, $ per BUI share
shares = 26_548_823  # shares outstanding used in the June book replay
contrib = ((rel.iloc[-1] - 1) * w / shares).sort_values()
p("\nlargest contributors 30 Jun -> last close, $ per BUI share:")
for t in list(contrib.index[:4]) + list(contrib.index[-4:]):
    p("   %-5s %+.3f" % (t, contrib[t]))

pd.DataFrame({"rebuilt_tr": j.rebuilt.round(5), "reported_tr": j.reported.round(5)}).to_csv(
    os.path.join(RES, "nav_rebuild_daily.csv"))

# daily vs weekly rate beta: BUI NAV, BUI price, XLU, and the rebuilt sleeve
p("\nDAILY VS WEEKLY RATE BETA, 2026 (pct per +100bp in the 10-year)")
y = pd.read_csv(os.path.join(DATA, "dgs10.csv"))
y.columns = ["date", "dgs10"]
y["date"] = pd.to_datetime(y.date)
y = y.set_index("date").dgs10.replace(".", np.nan).astype(float)
# NAV total return index for the whole year
navy = bui.bui_nav.loc["2025-12-31":]
addy = pd.Series(0.0, index=navy.index)
for _, r in dist.iterrows():
    if navy.index[0] < r.ex_date <= navy.index[-1]:
        addy.loc[navy.index[navy.index.searchsorted(r.ex_date)]:] += r.amount
series = {"BUI NAV": navy + addy, "XLU price": bui.xlu_close.loc["2025-12-31":], "SPY price": bui.spy_close.loc["2025-12-31":]}
brows = []
for lab, s in series.items():
    d = pd.DataFrame({"x": s, "y10": y}).dropna()
    for freq in ["D", "W-FRI"]:
        dd = d if freq == "D" else d.resample(freq).last().dropna()
        rr = dd.x.pct_change() * 100
        dy = dd.y10.diff()
        k = pd.concat([rr, dy], axis=1).dropna()
        Xk = np.column_stack([np.ones(len(k)), k.y10])
        bk = np.linalg.lstsq(Xk, k.x, rcond=None)[0]
        e = k.x - Xk @ bk
        se = np.sqrt(e.var() * len(k) / (len(k) - 2) / ((k.y10 - k.y10.mean()) ** 2).sum())
        p("  %-10s %-6s beta %+.1f (se %.1f), n %d" % (lab, "daily" if freq == "D" else "weekly", bk[1], se, len(k)))
        brows.append({"series": lab, "freq": freq, "beta": round(bk[1], 2), "se": round(se, 2), "n": len(k)})
pd.DataFrame(brows).to_csv(os.path.join(RES, "daily_vs_weekly_rate_beta.csv"), index=False)
open(os.path.join(RES, "nav_rebuild.txt"), "w").write("\n".join(out) + "\n")
