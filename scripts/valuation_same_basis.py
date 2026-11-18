"""BUI's book against XLU on the same basis: consensus P/E and growth, built the same way for both.

XLU tracks the S&P 500 utilities. State Street's daily holdings file wouldn't download for me, so I rebuild XLU as the
31 S&P 500 utilities (list from Wikipedia's S&P 500 page, November 2026), weighted by market cap. That ignores XLU's
capping rules, so the tie-out against State Street's own P/E is printed.

BUI's side is every US-listed name in the June 30 N-PORT with a consensus, at its N-PORT weight. Non-US ordinary shares
(about a third of the book) have no Nasdaq consensus and are left out; coverage is printed.

P/E is the November 17 close over consensus EPS for the fiscal year ending nearest December 2027. Growth is the next
fiscal year's consensus over that one. Averages are weighted in earnings yield (the harmonic mean), so a loss-maker
like Fervo pulls the average the right way instead of breaking it.
"""
import os
import xml.etree.ElementTree as ET
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

c = pd.read_csv(os.path.join(DATA, "consensus_eps_2026_11_18.csv"))
c["fy"] = pd.to_datetime(c.fiscal_end, format="%b %Y")
lo, hi = pd.Timestamp("2027-06-30"), pd.Timestamp("2028-06-30")
rows = []
for t, g in c.groupby("ticker"):
    g = g.sort_values("fy")
    cur = g[(g.fy > lo) & (g.fy <= hi)]
    if cur.empty:
        continue
    cur = cur.iloc[0]
    nxt = g[g.fy > cur.fy]
    rows.append({"ticker": t, "price": cur.price_2026_11_17, "eps_fy27": cur.consensus_eps, "fiscal_end": cur.fiscal_end,
                 "n_est": cur.n_estimates, "eps_next": nxt.consensus_eps.iloc[0] if len(nxt) else float("nan"),
                 "mcap": cur.market_cap})
v = pd.DataFrame(rows).set_index("ticker")
v["ey"] = v.eps_fy27 / v.price
v["pe"] = v.price / v.eps_fy27
v["growth"] = v.eps_next / v.eps_fy27 - 1


def agg(w, label):
    w = w / w.sum()
    ey = (w * v.loc[w.index, "ey"]).sum()
    g = (w * v.loc[w.index, "growth"]).sum()
    p("%-42s P/E %.1f (earnings yield %.2f%%), next-year EPS growth %.1f%%, %d names" % (label, 1 / ey, ey * 100, g * 100, len(w)))
    return 1 / ey, g


u = pd.read_csv(os.path.join(DATA, "sp500_utilities_2026_11.csv")).ticker
xlu_pe, xlu_g = agg(v.loc[u, "mcap"], "XLU rebuilt (S&P 500 utilities, cap-weighted)")
p("  tie-out: State Street's own XLU P/E on FY1 earnings was 18.25 on November 13; different year and weights")

root = ET.parse(os.path.join(DATA, "nport", "0001410368-26-085641.xml")).getroot()
N = root.tag.split("}")[0][1:]
hmap = pd.read_csv(os.path.join(DATA, "holdings_map.csv")).set_index("isin")
w = {}
for s in root.iter("{%s}invstOrSec" % N):
    isin = [x.get("value") for x in s.find("{%s}identifiers" % N) if x.tag.endswith("isin")]
    tk = hmap.us_ticker.get(isin[0]) if isin else None
    if isinstance(tk, str) and tk in v.index:
        w[tk] = float(s.find("{%s}pctVal" % N).text)
w = pd.Series(w)
p("BUI names covered: %.1f%% of net assets" % w.sum())
bui_pe, bui_g = agg(w, "BUI, US-listed names (June 30 weights)")
bx_pe, bx_g = agg(w.drop(["SPCX", "FRVO", "MWH"], errors="ignore"), "BUI, US-listed, without the 2026 IPOs")
ut = w[[t for t in w.index if t in set(u)]]
agg(ut, "BUI's US utilities only")
agg(v.loc[ut.index, "mcap"], "the same utilities at XLU-style cap weights")
nonut = w.drop(ut.index).drop(["SPCX", "FRVO", "MWH"], errors="ignore")
agg(nonut, "BUI's US-listed non-utilities (ex IPOs)")
p("\nSpaceX's consensus more than doubles from 2027 to 2028, so the growth figure with the IPOs is mostly SpaceX; use the ex-IPO line")
p("P/E over growth in points: XLU %.2f, BUI US-listed ex IPOs %.2f" % (xlu_pe / (xlu_g * 100), bx_pe / (bx_g * 100)))
p("tie-out: FactSet's 3-5 year EPS growth for XLU via State Street was 9.42%%; my rebuilt next-year figure is %.1f%%" % (xlu_g * 100))
v.round(4).to_csv(os.path.join(RES, "valuation_same_basis.csv"))
open(os.path.join(RES, "valuation_same_basis.txt"), "w").write("\n".join(out) + "\n")
