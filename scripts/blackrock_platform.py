# BUI next to the rest of BlackRock's closed-end fund platform: the rights offerings since mid-2025, the SpaceX IPO
# allocation across four BlackRock CEFs, and what the seven funds that dropped call writing did with their payouts.
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
def rows(n): return list(csv.DictReader(open(os.path.join(HERE, '..', 'data', n))))
R = rows('blackrock_rights_offerings_2025_2026.csv')
print(f"BlackRock CEF rights offering results found on EDGAR since June 2025: {len(R)}, about ${sum(float(r['approx_proceeds_m']) for r in R):,.0f}m raised")
for r in R: print(f"  {r['result_date']} {r['ticker']:5} {r['result_as_announced']:16} ~{r['approx_new_shares_m']}m shares, ~${r['approx_proceeds_m']}m")
print("SpaceX at 30 Jun 2026 across BlackRock CEFs:")
for r in rows('spacex_across_blackrock_cefs_2026_06_30.csv'):
    print(f"  {r['ticker']:5} {int(r['spacex_shares']):>8,} shares, ${int(r['value_usd'])/1e6:5.1f}m, {r['pct_of_net_assets']}% of net assets, filed under {r['industry_label_in_schedule']}")
print("The seven funds that dropped call writing on 10 Nov 2025, regular monthly payout since:")
for r in rows('sibling_regular_payouts.csv'):
    print(f"  {r['ticker']:5} now ${r['regular_monthly_now']}: {r['change_since_2025_11_10']}; specials: {r['specials_2025_2026']}")
fee = 64.6e6 * 0.01; cost = 294_540
print(f"BUI rights offering: BlackRock paid ${cost:,} of costs; 1.00% fee on ~$64.6m is ${fee:,.0f} a year, so ~{cost/fee*12:.1f} months to earn it back")
