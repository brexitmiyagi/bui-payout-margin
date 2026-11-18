"""Where BUI's year since dropping covered calls came from.

The regression in style_analysis.py says BUI beat an ETF mix by 5 to 8 points in the 53 weeks after it stopped writing
calls (10 November 2025), but can't say why. Here I use the holdings instead. I split the year into four pieces:

  stub   14 Nov 2025 to 31 Dec 2025   December 31 book, start weights backed out of the end weights, US-listed names
  Q1     31 Dec 2025 to 31 Mar 2026   December 31 book, every position priced from the two N-PORTs
  Q2     31 Mar 2026 to 30 Jun 2026   March 31 book, same
  H2     30 Jun 2026 to 13 Nov 2026   June 30 book, US-listed names from Nasdaq (September's N-PORT isn't out yet)

For each piece:
  holdings   what the book earned, buy and hold from the start weights, price only
  sectors    the same bucket weights, but each bucket earns a plain ETF instead of BUI's names
  benchmark  the five-year book-like mix from style_analysis.py (19% XLU, 57% IGF, 23% XLI, 1% IEF), fixed, so it
             isn't fitted on the year it's judged on

  sector bets  = sectors - benchmark
  stock picks  = holdings - sectors, with the 2026 IPOs (SpaceX, Fervo, SOLV) shown on their own
A position I can't price in a piece (non-US names in the stub and H2, a few non-US names sold mid-quarter) is given
its bucket ETF's return, so it adds nothing to stock picking either way. Coverage is printed.

Bucket ETFs: US utilities and US power producers XLU, non-US utilities JXI, pipelines and LNG MLPX, rail, airports and
toll roads IGF, grid equipment GRID, renewables ICLN, gases and materials XLB, waste and space XLI, cash at the
3-month bill. All price only, like the holdings, so dividends are out of both sides.

Then a daily test on the US-listed part of the book over the whole year: holdings minus their bucket ETFs, day by day,
annualised, with a t-stat. That's the test with power: it compares each name with the ETF for its own bucket instead of
the whole fund with one mix.
"""
import os
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

NPORT = {"2025-12-31": "0001410368-26-016995", "2026-03-31": "0001410368-26-054529", "2026-06-30": "0001410368-26-085641"}
IPO = {"SPCX", "FRVO", "MWH"}
PROXY = {"US regulated utilities": "XLU", "US power producers": "XLU", "non-US utilities and grid operators": "JXI",
         "pipelines and LNG": "MLPX", "rail airports and toll roads": "IGF", "grid and electrification equipment": "GRID",
         "renewables and storage": "ICLN", "industrial gases and materials": "XLB", "waste": "XLI",
         "space and satellites": "XLI", "cash": "BILL"}
BENCH = {"XLU": 0.19, "IGF": 0.57, "XLI": 0.23, "IEF": 0.01}

hmap = pd.read_csv(os.path.join(DATA, "holdings_map.csv")).set_index("isin")
lp = pd.read_csv(os.path.join(DATA, "listed_holdings_daily_2025_2026.csv"), parse_dates=["date"]).set_index("date")
etf = pd.read_csv(os.path.join(DATA, "etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
etf = etf.rename(columns=lambda c: c.replace("_close", "").upper())[["XLU", "IGF", "XLI", "IEF", "GRID", "AMLP"]]
px = pd.read_csv(os.path.join(DATA, "proxy_etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
etf = etf.join(px, how="inner")
ust = pd.read_csv(os.path.join(DATA, "treasury_par_curve_2026.csv"), parse_dates=["Date"]).set_index("Date").sort_index()
bill = ust["3 Mo"].mean()   # 2026 average 3-month bill, used for the cash sleeve
nav = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date").bui_nav
dist = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])


def book(date):
    root = ET.parse(os.path.join(DATA, "nport", NPORT[date] + ".xml")).getroot()
    N = root.tag.split("}")[0][1:]
    rows = []
    for s in root.iter("{%s}invstOrSec" % N):
        isin = ""
        ids = s.find("{%s}identifiers" % N)
        for c in (ids if ids is not None else []):
            if c.tag.endswith("isin"):
                isin = c.get("value")
        bal, val = float(s.find("{%s}balance" % N).text), float(s.find("{%s}valUSD" % N).text)
        rows.append({"isin": isin, "w": float(s.find("{%s}pctVal" % N).text) / 100, "px": val / bal if bal else np.nan})
    b = pd.DataFrame(rows).set_index("isin")
    b = b.join(hmap)
    assert b.bucket.notna().all(), b[b.bucket.isna()]
    return b


def lr(t, a, z):
    """price return of a listed ticker between two dates (last close on or before each)"""
    if t not in lp or pd.isna(t):
        return np.nan
    s = lp[t].dropna()
    s0, s1 = s.loc[:a], s.loc[:z]
    if s0.empty or s1.empty or s0.index[-1] < pd.Timestamp(a) - pd.Timedelta(days=5):
        return np.nan
    return s1.iloc[-1] / s0.iloc[-1] - 1


def er(t, a, z):
    if t == "BILL":
        return bill / 100 * (pd.Timestamp(z) - pd.Timestamp(a)).days / 365
    s = etf[t]
    return s.loc[:z].iloc[-1] / s.loc[:a].iloc[-1] - 1


def piece(label, b, a, z, source, back_out=False):
    b = b.copy()
    b["proxy"] = b.bucket.map(PROXY)
    b["pr"] = [er(t, a, z) for t in b.proxy]
    if source == "nport":
        nxt = book(z)
        b["r"] = nxt.px.reindex(b.index) / b.px - 1   # N-PORT price per share, start and end
        miss = b.r.isna() & b.us_ticker.notna()
        b.loc[miss, "r"] = [lr(t, a, z) for t in b.loc[miss, "us_ticker"]]
    else:
        b["r"] = [lr(t, a, z) for t in b.us_ticker]
    b.loc[b.bucket == "cash", "r"] = b.loc[b.bucket == "cash", "pr"]
    if back_out:   # end weights -> start weights, assuming no trading in the stub
        g = 1 + b.r.fillna(b.pr)
        b["w"] = (b.w / g) / (b.w / g).sum() * b.w.sum()
    w = b.w / b.w.sum()
    cov = w[b.r.notna()].sum()
    r_used = b.r.fillna(b.pr)
    H = (w * r_used).sum()
    S = (w * b.pr).sum()
    B = sum(v * er(k, a, z) for k, v in BENCH.items())
    ipo = (w * (r_used - b.pr))[b.us_ticker.isin(IPO)].sum()
    # NAV total return over the piece, for the reconciliation
    n0, n1 = nav.loc[:a].iloc[-1], nav.loc[:z].iloc[-1]
    d = dist[(dist.ex_date > pd.Timestamp(a)) & (dist.ex_date <= pd.Timestamp(z))].amount.sum()
    navtr = (n1 + d) / n0 - 1
    by_bucket = (w * (r_used - b.pr)).groupby(b.bucket).sum()
    global SECT
    SECT.append((w * (b.pr - B)).groupby(b.bucket).sum().rename(label))
    names = (w * (r_used - b.pr)).rename(lambda i: hmap.loc[i, "name"] if i in hmap.index else i)
    return {"piece": label, "start": a, "end": z, "priced_weight": cov, "holdings": H, "sectors": S, "benchmark": B,
            "sector_bets": S - B, "stock_picks_ex_ipo": H - S - ipo, "ipos": ipo, "nav_tr": navtr}, by_bucket, names


SECT = []
pieces = [("stub", book("2025-12-31"), "2025-11-14", "2025-12-31", "listed", True),
          ("Q1 2026", book("2025-12-31"), "2025-12-31", "2026-03-31", "nport", False),
          ("Q2 2026", book("2026-03-31"), "2026-03-31", "2026-06-30", "nport", False),
          ("H2 to Nov 13", book("2026-06-30"), "2026-06-30", "2026-11-13", "listed", False)]
rows, bb, nm = [], [], []
for lab, b, a, z, src, bo in pieces:
    r, by, names = piece(lab, b, a, z, src, bo)
    rows.append(r); bb.append(by.rename(lab)); nm.append(names.rename(lab))
t = pd.DataFrame(rows)
tot = {"piece": "year", "start": t.start.iloc[0], "end": t.end.iloc[-1], "priced_weight": np.nan}
for c in ["holdings", "sectors", "benchmark", "nav_tr"]:
    tot[c] = (1 + t[c]).prod() - 1
for c in ["sector_bets", "stock_picks_ex_ipo", "ipos"]:
    tot[c] = t[c].sum()
t = pd.concat([t, pd.DataFrame([tot])], ignore_index=True)
show = t.copy()
for c in ["priced_weight", "holdings", "sectors", "benchmark", "sector_bets", "stock_picks_ex_ipo", "ipos", "nav_tr"]:
    show[c] = (show[c] * 100).round(2)
p("price-only, % (priced_weight is the share of the book with its own price in that piece):")
p(show.to_string(index=False))
yr = t.iloc[-1]
excess = yr.holdings - yr.benchmark
p("\nyear: holdings %+.1f%%, benchmark mix %+.1f%%, gap %+.1f points" % (yr.holdings * 100, yr.benchmark * 100, excess * 100))
p("  sector bets %+.1f, stock picks %+.1f, IPOs %+.1f, compounding cross-terms %+.1f" %
  (yr.sector_bets * 100, yr.stock_picks_ex_ipo * 100, yr.ipos * 100,
   (excess - yr.sector_bets - yr.stock_picks_ex_ipo - yr.ipos) * 100))
B = pd.concat(bb, axis=1).fillna(0)
B["year"] = B.sum(axis=1)
p("\nstock picks plus IPOs by bucket (points of fund return):")
p((B * 100).round(2).sort_values("year").to_string())
Sx = pd.concat(SECT, axis=1).fillna(0)
Sx["year"] = Sx.sum(axis=1)
p("\nsector bets by bucket: weight x (bucket ETF - benchmark mix), points:")
p((Sx * 100).round(2).sort_values("year").to_string())
Nm = pd.concat(nm, axis=1).fillna(0)
Nm["year"] = Nm.sum(axis=1)
p("\nlargest single-name contributions vs their bucket ETF over the year (points):")
s = (Nm.year * 100).sort_values()
p(pd.concat([s.head(5), s.tail(5)]).round(2).to_string())

# reconciliation: holdings are price only and before fees; NAV is total return after fees
p("\nreconciliation, year: NAV total return %+.1f%% vs holdings price return %+.1f%%; the difference (%+.1f) is"
  " income (about 2.8%% a year), less 1.06%% of fees, plus trading within quarters and the parts I can't price" %
  (yr.nav_tr * 100, yr.holdings * 100, (yr.nav_tr - yr.holdings) * 100))

t["unexplained"] = t.nav_tr - t.holdings - (2.8 - 1.06) / 100 * (pd.to_datetime(t.end) - pd.to_datetime(t.start)).dt.days / 365
p("NAV return not explained by priced holdings plus income less fees, by piece (points): " +
  ", ".join("%s %+.1f" % (r.piece, r.unexplained * 100) for r in t.itertuples() if r.piece != "year"))
p("  the April 2026 rights offering sold about 2.4m shares near $26.9 against a NAV near $27.7, about -0.25 of NAV,"
  " so it doesn't explain the gap; in the two fully priced quarters the rest is trading inside the quarter")

# daily test on the US-listed sleeve
segs = [(book("2025-12-31"), "2025-11-14", "2026-03-31"), (book("2026-03-31"), "2026-03-31", "2026-06-30"),
        (book("2026-06-30"), "2026-06-30", "2026-11-13")]
act = []
for b, a, z in segs:
    b = b[b.us_ticker.notna() & (b.bucket != "cash")]
    b = b[[tk in lp for tk in b.us_ticker]]
    b = b[[lp[tk].loc[:a].dropna().size > 0 and lp[tk].loc[:a].dropna().index[-1] >= pd.Timestamp(a) - pd.Timedelta(days=5)
           for tk in b.us_ticker]]
    w = b.w / b.w.sum()
    pr = lp[b.us_ticker.tolist()].loc[a:z].ffill()
    ep = etf[[PROXY[x] for x in b.bucket]].loc[a:z]
    ep.columns = b.us_ticker.tolist()
    hv = (pr / pr.iloc[0]).mul(w.values, axis=1).sum(axis=1)       # buy and hold within the segment
    sv = (ep / ep.iloc[0]).mul(w.values, axis=1).sum(axis=1)
    act.append((hv.pct_change() - sv.pct_change()).dropna())
a = pd.concat(act)
a = a[~a.index.duplicated()]
mu, sd = a.mean() * 252 * 100, a.std() * np.sqrt(252) * 100
tstat = a.mean() / (a.std() / np.sqrt(len(a)))
p("\ndaily test, US-listed sleeve, %s to %s (%d days): stock picks vs bucket ETFs %+.1f%% a year, tracking error %.1f%%,"
  " t = %.1f" % (a.index[0].date(), a.index[-1].date(), len(a), mu, sd, tstat))
p("  years to reach t = 2 at this edge and tracking error: %.1f" % ((2 * sd / abs(mu)) ** 2))
t.to_csv(os.path.join(RES, "attribution.csv"), index=False)
B.to_csv(os.path.join(RES, "attribution_by_bucket.csv"))
open(os.path.join(RES, "attribution.txt"), "w").write("\n".join(out) + "\n")
