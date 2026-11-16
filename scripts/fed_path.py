"""What the Treasury curve says about the Fed path behind my 10-year scenarios.

Par yields from Treasury's daily curve for 13 November 2026. Forward short rates are approximated from par yields
(f(a,b) ~ (b*y_b - a*y_a)/(b - a)), which is close enough at these maturities to read the direction and size.
FedWatch odds for the 8-9 December meeting are quoted in the post from press reports of CME data; CME's own page
isn't fetchable without a browser session.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
c = pd.read_csv(os.path.join(DATA, "treasury_par_curve_2026.csv"))
r = c[c.Date == "11/13/2026"].iloc[0]
m1, m3, m6, y1, y2, y10 = (float(r[k]) for k in ["1 Mo", "3 Mo", "6 Mo", "1 Yr", "2 Yr", "10 Yr"])
p("13 Nov 2026 par curve: 1m %.2f, 3m %.2f, 6m %.2f, 1y %.2f, 2y %.2f, 10y %.2f" % (m1, m3, m6, y1, y2, y10))
f6_6 = (1 * y1 - 0.5 * m6) / 0.5
f1_1 = (2 * y2 - 1 * y1) / 1
p("approximate forwards: 6m rate in 6m %.2f%%, 1y rate in 1y %.2f%%" % (f6_6, f1_1))
p("so bills price about %.0f bp of tightening from the 1-month rate to the 1y1y forward" % ((f1_1 - m1) * 100))
open(os.path.join(RES, "fed_path.txt"), "w").write("\n".join(out) + "\n")
