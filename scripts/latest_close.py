"""The price-dependent numbers in the post, at the November 18, 2026 close.

Prices and NAVs: Nasdaq (fund closes and X-ticker NAVs). Distributions: latest regular monthly amount for each fund.
The UTF-BUI spread median is the trailing 252-day median from switch_backtest.py, with Nov 16 to 18 added.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
c = pd.read_csv(os.path.join(DATA, "close_2026_11_18.csv")).set_index("ticker")
c["prem_pct"] = (c.close / c.nav - 1) * 100
c["yield_on_price_pct"] = c.monthly_distribution * 12 / c.close * 100
print(c[["close", "nav", "prem_pct", "yield_on_price_pct"]].round(2).to_string())
nav, px = c.loc["BUI", "nav"], c.loc["BUI", "close"]
print("\nBUI target (100%% of NAV) $%.2f, trim above +1%% $%.2f, accumulate below 95%% $%.2f, formal Buy below 87%% $%.2f"
      % (nav, nav * 1.01, nav * 0.95, nav * 0.87))
print("payout $0.154 a month = %.2f%% of NAV" % (0.154 * 12 / nav * 100))
d = pd.read_csv(os.path.join(RES, "switch_backtest_daily.csv"), index_col=0, parse_dates=True).spread
u = lambda p, n: (p / n - 1) * 100
add = pd.Series({pd.Timestamp("2026-11-16"): u(25.44, 27.42) - u(26.12, 26.25),
                 pd.Timestamp("2026-11-17"): u(25.10, 27.04) - u(25.99, 25.87),
                 pd.Timestamp("2026-11-18"): c.loc["UTF", "prem_pct"] - c.loc["BUI", "prem_pct"]})
s = pd.concat([d, add])
med = s.rolling(252, min_periods=200).median()
print("UTF-BUI spread Nov 18 %.2f, trailing one-year median %.2f, switch trigger %.2f" % (s.iloc[-1], med.iloc[-1], med.iloc[-1] - 5))
