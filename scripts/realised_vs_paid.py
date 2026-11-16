# Realised gains against what BUI paid out, from the statements in the June 2026 semi-annual report.
import os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'statement_totals.csv'))):
    nii, rg, paid = float(r['net_investment_income']), float(r['net_realized_gain']), float(r['distributions_total'])
    print(f"{r['period']}: income ${nii/1e6:.1f}m + realised gains ${rg/1e6:.1f}m = ${(nii+rg)/1e6:.1f}m against ${paid/1e6:.1f}m paid "
          f"({(nii+rg)/paid:.2f}x); income alone {nii/paid:.0%}; new capital ${(float(r['rights_offering_proceeds'])+float(r['shelf_proceeds']))/1e6:.1f}m")
shares_jun, shares_nov = 26_548_823, 27_045_043
print(f"shares outstanding 30 Jun 2026 {shares_jun:,} -> 13 Nov 2026 {shares_nov:,} (BlackRock site): +{shares_nov-shares_jun:,}")
print(f"advisory fee is 1.00% of net assets: the rights offering's $64.7m adds about ${64.7447*0.01:.2f}m a year")
