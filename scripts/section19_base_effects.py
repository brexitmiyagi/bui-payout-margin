# The Section 19 margin is a 5-year number, so it moves when old months drop out of the window, not just when the fund
# earns or loses. This runs the margin forward at month-ends to Dec 2027 with NAV total return held at 0%, 5% and 8.28%
# a year, finds what NAV has to do between Nov 13 and Dec 31, 2026 for the Dec 31 figure (the late-January notice) to
# go negative, and how often BUI's NAV has fallen that much over a similar 32-trading-day stretch.
import datetime as dt
from common import daily, dists, nav_tr_index, at
D = daily(); idx = nav_tr_index(D, dists())
me = {}
for k, x in enumerate(D): me[(x['d'].year, x['d'].month)] = idx[k]
lv0 = [me[k] for k in sorted(me) if k <= (2026, 10)]
pay = 0.154
labels = [(2026, 11), (2026, 12)] + [(2027, m) for m in range(1, 13)]
print("month-end: " + "  ".join(f"{y}-{m:02d}" for y, m in labels))
for annual in (0.0, 0.05, 0.0828):
    r = (1+annual)**(1/12) - 1; lv = list(lv0); nav = D[-1]['nav']; out = []
    for _ in labels:
        lv.append(lv[-1]*(1+r)); nav = nav*(1+r) - pay
        out.append(f"{((lv[-1]/lv[-61])**0.2 - 1 - pay*12/nav)*100:+5.2f}")
    print(f"NAV {annual:.2%}/yr: " + "    ".join(out))
print("months leaving the 5-year window, monthly NAV total return:")
ks = sorted(me)
print("  " + ", ".join(f"{k[0]}-{k[1]:02d} {me[k]/me[ks[ks.index(k)-1]]-1:+.1%}" for k in ks if (2021, 11) <= k <= (2022, 12)))
now = idx[-1]; nav0 = D[-1]['nav']; s = idx[D.index(at(D, dt.date(2021, 12, 31)))]
for special in (0.0, 0.5):
    lo, hi = -0.2, 0.2
    for _ in range(60):
        g = (lo+hi)/2
        m = (now*(1+g)/s)**0.2 - 1 - pay*12/(nav0*(1+g) - pay - special)
        lo, hi = (lo, g) if m > 0 else (g, hi)
    print(f"Dec 31, 2026 margin goes negative below a NAV total return of {g:+.2%} from Nov 13 (special of ${special:.2f})")
h = 32
r = [idx[i+h]/idx[i]-1 for i in range(len(idx)-h)]
r2 = [idx[i+h]/idx[i]-1 for i in range(len(idx)-h) if D[i]['d'].year in (2022, 2023, 2026)]
for th in (-0.03, -0.025):
    print(f"share of {h}-trading-day windows since 2016 with NAV total return below {th:.1%}: {sum(v < th for v in r)/len(r):.1%}; in 2022, 2023 and 2026: {sum(v < th for v in r2)/len(r2):.1%}")
