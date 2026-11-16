# Maps BUI's June 30, 2026 US utility holdings (N-PORT weights) to the states where the November 2026 midterms or 2026
# legislation raised regulatory pressure, per S&P Global's Nov 6 factbox (Georgia PSC majority change, Arizona
# commissioners, New York data-center pause, Ohio data-center measures) and Gabelli's June 26 note (Pennsylvania House
# bill capping ROEs at the 10-year + 2 points). A holding counts if its latest 10-K/20-F names a regulated operating
# utility in one of those states (subsidiary named below). This overstates exposure, since each company also operates
# elsewhere; it is the share of NAV with some exposure, not the share of earnings.
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
book = {  # ticker: (June 30, 2026 % of net assets from N-PORT, states, operating subsidiary named in the 10-K/20-F)
    'SO':  (3.94, 'GA', 'Georgia Power Company'),
    'DUK': (3.96, 'OH', 'Duke Energy Ohio'),
    'AEP': (3.46, 'OH', 'Ohio Power Company (AEP Ohio)'),
    'NGG': (3.92, 'NY', 'Niagara Mohawk (National Grid)'),
    'EXC': (2.41, 'PA', 'PECO Energy Company'),
    'FE':  (1.74, 'OH, PA', 'Ohio Edison; FE PA'),
    'NI':  (1.67, 'OH, PA', 'Columbia Gas of Ohio; Columbia Gas of Pennsylvania'),
}
not_counted = {'NEE': 'Florida', 'D': 'Virginia/Carolinas (East Ohio gas sold to Enbridge, March 2024)', 'SRE': 'California/Texas',
               'ETR': 'Gulf South', 'CMS': 'Michigan', 'XEL': 'Upper Midwest/Colorado/Texas', 'PCG': 'California',
               'CNP': 'Texas/Indiana/Minnesota (Ohio unit listed as former subsidiary in 10-K; excluded)'}
tot = 0
for t, (w, st, sub) in book.items():
    tot += w; print(f"{t:4} {w:4.2f}%  {st:7} {sub}")
print(f"share of June 30 net assets in holdings with a regulated utility in GA, PA, OH, NY or AZ: {tot:.1f}%")
print("not counted: " + "; ".join(f"{k} ({v})" for k, v in not_counted.items()))
print("Georgia: S&P Global says the new 3-2 Democratic PSC will oversee Georgia Power's first rate case since 2022. Southern Co was 3.39% of BUI at Oct 30.")
