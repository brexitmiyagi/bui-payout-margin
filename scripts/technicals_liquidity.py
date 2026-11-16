"""CEF-desk technicals and a liquidity check for BUI and UTF.

Discount z-score and momentum come from switch_backtest.py's daily file. Volume is from the exchange tape
(Nasdaq historical). The spread estimate is Abdi and Ranaldo (2017), which backs a bid-ask spread out of daily
close, high and low. It is an estimate; the live quoted spread during US hours is the thing to check before trading.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

disc = pd.read_csv(os.path.join(RES, "switch_backtest_daily.csv"), parse_dates=["date"]).set_index("date")
bd = pd.read_csv(os.path.join(DATA, "bui_distributions.csv"), parse_dates=["ex_date"])
pdists = pd.read_csv(os.path.join(DATA, "peer_distributions.csv"), parse_dates=["ex_date"])
exd = {"bui": bd.ex_date, "utf": pdists[pdists.ticker == "UTF"].ex_date}


def rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def abdi_ranaldo(df):
    c = np.log(df.close)
    eta = (np.log(df.high) + np.log(df.low)) / 2
    s2 = 4 * (c - eta) * (c - eta.shift(-1))
    return s2


for t in ["bui", "utf"]:
    df = pd.read_csv(os.path.join(DATA, f"{t}_ohlcv_daily.csv"), parse_dates=["date"]).set_index("date")
    p("\n== %s, last close %s ==" % (t.upper(), df.index[-1].date()))
    dcol = f"{t}_disc"
    x = disc[dcol]
    last = x.iloc[-1]
    for w, lab in [(252, "1y"), (756, "3y")]:
        z = (last - x.iloc[-w:].mean()) / x.iloc[-w:].std()
        p("  discount %.2f%%, %s mean %.2f, z-score %.2f" % (last, lab, x.iloc[-w:].mean(), z))
    p("  discount change: 1 month %+.2f, 3 months %+.2f pts" % (last - x.iloc[-22], last - x.iloc[-64]))
    c = df.close
    p("  price %.2f vs 50-day avg %.2f, 200-day avg %.2f; RSI(14) %.0f" %
      (c.iloc[-1], c.iloc[-50:].mean(), c.iloc[-200:].mean(), rsi(c).iloc[-1]))
    # liquidity
    dv = df.volume * df.close
    for n, lab in [(21, "1 month"), (63, "3 months"), (252, "1 year")]:
        p("  average daily volume, %s: %s shares, $%.2fm (median $%.2fm)" %
          (lab, f"{df.volume.iloc[-n:].mean():,.0f}", dv.iloc[-n:].mean() / 1e6, dv.iloc[-n:].median() / 1e6))
    adv = dv.iloc[-63:].median()
    p("  at 15%% of median daily dollar volume an institution can do about $%.2fm a day; a $5m position takes %.0f days"
      % (adv * 0.15 / 1e6, 5e6 / (adv * 0.15)))
    s2 = abdi_ranaldo(df).iloc[-252:]
    spread = np.sqrt(s2.clip(lower=0).mean()) * 100
    p("  estimated effective spread (Abdi-Ranaldo, last year): %.2f%% of price" % spread)
    # volume around ex-dates: ratio of volume to the median of the prior 20 days
    rel = df.volume / df.volume.rolling(20).median().shift(1)
    ev = []
    for e in exd[t]:
        if e < df.index[25] or e > df.index[-3]:
            continue
        i = df.index.searchsorted(e)
        ev.append([rel.iloc[i + k] for k in range(-2, 3)])
    ev = np.array(ev)
    p("  volume vs prior 20-day median around ex-dates (days -2..+2, median of %d events): %s" %
      (len(ev), " ".join("%.2f" % v for v in np.nanmedian(ev, axis=0))))
    # 2026 big-volume days
    top = rel.loc["2026"].sort_values(ascending=False).head(5)
    p("  heaviest 2026 volume days (x prior 20-day median): " +
      ", ".join("%s %.1fx" % (d.date(), v) for d, v in top.items()))
    if t == "bui":
        win = rel.loc["2026-03-01":"2026-04-15"]
        p("  rights offering window Mar 1-Apr 15 2026: median %.2fx, max %.1fx on %s" %
          (win.median(), win.max(), win.idxmax().date()))
open(os.path.join(RES, "technicals_liquidity.txt"), "w").write("\n".join(out) + "\n")
