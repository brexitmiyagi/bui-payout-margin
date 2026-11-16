# BUI's own Section 19(a) notices, January to October 2026: what each payout was made of, and the gap between
# the fund's 5-year average NAV return and the distribution rate it is paying on NAV.
from common import rows
R = rows('section19_notices_2026.csv')
print('perf as of | 5y avg NAV TR | dist rate on NAV | margin | YTD NAV TR | month payout mix (NII / ST / LT / ROC)')
for r in R:
    m = float(r['five_year_avg_nav_tr_pct']) - float(r['annualized_dist_rate_on_nav_pct'])
    d = float(r['month_distribution'])
    mix = ' / '.join(f"{float(r[k])/d:.0%}" for k in ['month_net_income','month_st_gains','month_lt_gains','month_return_of_capital'])
    print(f"{r['performance_as_of']} | {r['five_year_avg_nav_tr_pct']}% | {r['annualized_dist_rate_on_nav_pct']}% | {m:+.2f} pts | {r['ytd_cum_nav_tr_pct']}% | {mix}")
last = R[-1]
y = float(last['ytd_distributions'])
print(f"fiscal YTD to {last['notice_pay_date']}: ${y:.3f} paid, net income {float(last['ytd_net_income'])/y:.0%}, short-term gains {float(last['ytd_st_gains'])/y:.0%}, long-term gains {float(last['ytd_lt_gains'])/y:.0%}, return of capital {float(last['ytd_return_of_capital'])/y:.0%}")

# Year-to-date short-term gains are cumulative, so a fall between notices means net short-term losses were booked.
rs = rows('section19_notices_2026.csv')
for a, b in zip(rs, rs[1:]):
    d = float(b['ytd_st_gains']) - float(a['ytd_st_gains'])
    if d < 0:
        print(f"YTD short-term gains fell {d:+.4f} a share between the {a['notice_pay_date']} and {b['notice_pay_date']} notices")
