"""What a taxable holder actually received: the tax character of BUI's distributions.

Final character for 2023-2025 from BlackRock's annual reports (dollars for the whole fund). 2026 is the October 30
Section 19 estimate for the year to date, which is not final; short-term gains are taxed as ordinary income.
Not tax advice; the 1099 decides.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
t = pd.read_csv(os.path.join(DATA, "blackrock_tax_character_2023_2025.csv"))
b = t[t.ticker == "BUI"].copy()
b["total"] = b.ordinary_income + b.lt_gains + b.return_of_capital
for r in b.itertuples():
    p("%d final: ordinary income %.0f%%, long-term gains %.0f%%, return of capital %.0f%%" %
      (r.year, r.ordinary_income / r.total * 100, r.lt_gains / r.total * 100, r.return_of_capital / r.total * 100))
s = pd.read_csv(os.path.join(DATA, "section19_notices_2026.csv")).iloc[-1]
tot = s.ytd_distributions
p("2026 to Oct 30 (estimate): net income %.0f%%, short-term gains %.0f%%, long-term gains %.0f%%, return of capital %.0f%%" %
  (s.ytd_net_income / tot * 100, s.ytd_st_gains / tot * 100, s.ytd_lt_gains / tot * 100, s.ytd_return_of_capital / tot * 100))
p("note: 'ordinary income' here includes qualified dividends. In 2025, $10,784,769 of BUI's $12,635,567 of ordinary"
  " dividends (85%) was designated qualified, so 97% of 2025's payout was taxed at preferential rates.")
p("2026 so far: short-term gains alone are %.0f%% of the payout and are taxed at ordinary rates; if net income is 85%%"
  " qualified again, about %.0f%% of the payout is taxed at ordinary rates (after_tax_yield.py)" %
  (s.ytd_st_gains / tot * 100, (s.ytd_st_gains + 0.15 * s.ytd_net_income) / tot * 100))
open(os.path.join(RES, "tax_character.txt"), "w").write("\n".join(out) + "\n")
