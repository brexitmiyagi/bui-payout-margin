# BlackRock said dropping call writing (10 Nov 2025) "could also potentially lead to ... improved trading and lower
# discounts." Average weekly discount before the Sep 10, 2025 announcement, just after the change, and now, for the
# seven funds that dropped the calls, the four BlackRock funds that kept them, and every other equity CEF on CEF Connect.
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'discount_event_study_fund_windows.csv'))))
cols = ['avg_discount_jul11_sep05_2025', 'avg_discount_nov14_2025_jan09_2026', 'avg_discount_sep18_nov13_2026']
for r in R:
    v = [float(r[c]) for c in cols]
    print(f"{r['ticker']:32} {v[0]:+6.2f} -> {v[1]:+6.2f} -> {v[2]:+6.2f}  change {v[2]-v[0]:+.2f}")
def grp(g):
    rows = [r for r in R if r['group'] == g]
    return [sum(float(r[c]) for r in rows)/len(rows) for c in cols]
t, c, o = grp('dropped calls 10 Nov 2025'), grp('BlackRock kept options'), grp('other equity CEFs on CEF Connect')
for name, v in (('seven that dropped calls', t), ('four BlackRock funds that kept options', c), ('other equity CEFs (mean)', o)):
    print(f"{name:40} {v[0]:+.2f} -> {v[2]:+.2f} ({v[2]-v[0]:+.2f})")
print(f"difference-in-differences vs BlackRock option funds: {(t[2]-t[0])-(c[2]-c[0]):+.2f} pts; vs other equity CEFs: {(t[2]-t[0])-(o[2]-o[0]):+.2f} pts")
M = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'discount_monthly_blackrock_vs_others.csv'))))
for r in M:
    if r['month'] in ('2024-06', '2025-06', '2025-10', '2026-02', '2026-09', '2026-10'):
        print(f"{r['month']}: BlackRock 11 {float(r['blackrock_11_mean_discount']):+.2f}, other equity CEFs {float(r['other_equity_cefs_mean_discount']):+.2f}, BUI {r['bui_discount']}")
