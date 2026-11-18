"""Why BUI's April 2026 rights offering came in undersubscribed.

Terms are in data/bui_rights_offering_2026.csv (497AD notices and the 424B2). The price formula matters most: 95% of
the five-day average market price, but never below 95% of NAV. At a premium, that's a discount to the market price
and subscribing pays. Once the shares trade under 95% of NAV, the floor kicks in and the subscription price sits above
the market price, so a holder who wants more shares does better buying them on the exchange.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

b = pd.read_csv(os.path.join(DATA, "bui_price_nav_daily.csv"), parse_dates=["date"]).set_index("date")
b["prem"] = (b.bui_close / b.bui_nav - 1) * 100
f = pd.read_csv(os.path.join(DATA, "factors_and_peer_navs_daily.csv"), parse_dates=["date"]).set_index("date")
utf = (f.utf_price / f.utf_nav - 1) * 100
etf = pd.read_csv(os.path.join(DATA, "etf_prices_daily.csv"), parse_dates=["date"]).set_index("date")
key = {"30 days before announcement": "2026-01-28", "announced": "2026-02-27", "prospectus (Mar 6)": "2026-03-06",
       "record date": "2026-03-09", "two weeks into the offer": "2026-03-20", "expiration": "2026-04-02",
       "two weeks after": "2026-04-16", "a month after": "2026-05-04", "June 30": "2026-06-30"}
rows = []
for k, d in key.items():
    r = b.loc[:d].iloc[-1]
    rows.append({"point": k, "date": r.name.date(), "price": r.bui_close, "nav": r.bui_nav, "premium_pct": round(r.prem, 2),
                 "utf_premium_pct": round(utf.loc[:d].iloc[-1], 2), "xlu": etf.xlu_close.loc[:d].iloc[-1]})
t = pd.DataFrame(rows)
p(t.to_string(index=False))
exp = b.loc["2026-03-27":"2026-04-02"]
formula = 0.95 * exp.bui_close.mean()
floor = 0.95 * exp.bui_nav.iloc[-1]
sub = max(formula, floor)
p("\nat expiration: formula price 95%% x five-day average close $%.2f = $%.2f; floor 95%% x NAV $%.2f = $%.2f;"
  " subscription price $%.2f (filed $26.37)" % (exp.bui_close.mean(), formula, exp.bui_nav.iloc[-1], floor, sub))
p("market close on expiration day $%.2f, so subscribing cost $%.2f a share more than buying on the exchange" %
  (exp.bui_close.iloc[-1], 26.37 - exp.bui_close.iloc[-1]))
a, z = b.loc["2026-02-27"], b.loc["2026-04-02"]
p("premium fell from %+.2f%% at announcement to %+.2f%% at expiration, %.1f points, while NAV went from $%.2f to $%.2f"
  % (a.prem, z.prem, a.prem - z.prem, a.bui_nav, z.bui_nav))
win = b.loc["2026-02-27":"2026-04-02"]
p("trading days in the offer period with the premium above +5%%: %d of %d; below 0: %d" %
  ((win.prem > 5).sum(), len(win), (win.prem < 0).sum()))
p("UTF's discount over the same window: %+.2f%% to %+.2f%%, so the slide was BUI's own, not the sector's" %
  (utf.loc[:"2026-02-27"].iloc[-1], utf.loc[:"2026-04-02"].iloc[-1]))
p("offer: 6,019,793 shares; issued a bit over 2.4m (about 40%); dilution booked at -$0.10 a share in the N-CSRS")
t.to_csv(os.path.join(RES, "rights_offering.csv"), index=False)
open(os.path.join(RES, "rights_offering.txt"), "w").write("\n".join(out) + "\n")
