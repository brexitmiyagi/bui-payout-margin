# Net investment income against the distribution, from the audited financial highlights.
from common import rows
R = rows('financial_highlights.csv')
for r in R:
    print(f"{r['period']}: NII ${float(r['nii']):.2f}, distributions ${float(r['dist_total']):.2f} (return of capital ${float(r['dist_roc']):.2f}), NAV {r['nav_begin']} -> {r['nav_end']}, NAV TR {r['nav_tr_pct']}%")
h1 = [r for r in R if r['period'] == 'H1 2026'][0]
nii_run = float(h1['nii']) * 2
print(f"H1 2026 NII annualised ${nii_run:.2f} vs ${0.154*12:.3f} regular payout = {nii_run/(0.154*12):.0%} covered by income")
roc = sum(float(r['dist_roc']) for r in R if r['period'] in ('2021','2022','2023','2024'))
print(f"return of capital paid 2021-2024: ${roc:.2f} a share")
