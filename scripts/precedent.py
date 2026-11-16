# 2021-2024 is the closest thing to a test: four years where BUI's NAV return ran below its payout rate.
from common import rows
R = [r for r in rows('financial_highlights.csv') if r['period'] in ('2021','2022','2023','2024')]
g = 1.0
for r in R:
    g *= 1 + float(r['nav_tr_pct'])/100
    print(f"{r['period']}: NAV TR {r['nav_tr_pct']}%, paid ${r['dist_total']} = {float(r['dist_total'])/float(r['nav_begin']):.2%} of starting NAV, return of capital ${r['dist_roc']}")
ann = g**(1/4) - 1
print(f"2021-2024 NAV total return {ann:.2%} a year; NAV {R[0]['nav_begin']} -> {R[-1]['nav_end']} ({float(R[-1]['nav_end'])/float(R[0]['nav_begin'])-1:+.1%})")
nav = 26.38; pay = 1.848
for y in range(1, 5):
    nav = nav * (1 + ann) - pay
print(f"same four years from today's ${26.38:.2f} NAV with the ${pay:.3f} payout: NAV ${nav:.2f} ({nav/26.38-1:+.1%})")
