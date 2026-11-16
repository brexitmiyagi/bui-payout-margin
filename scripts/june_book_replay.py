# Replays the 30 June 2026 book (N-PORT) for the US/Canada-listed names: what each would have added or cost per BUI
# share from 30 June to 13 November 2026 if held unchanged. Price only, no dividends, and the fund has traded since,
# so this is a map of where the pressure came from, not the fund's actual P&L.
import csv, os, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'n': 'http://www.sec.gov/edgar/nport'}
r = ET.parse(os.path.join(HERE, '..', 'data', 'nport', '0001410368-26-085641.xml')).getroot()
val = {s.find('n:name', ns).text: float(s.find('n:valUSD', ns).text) for s in r.findall('.//n:invstOrSec', ns)}
net = float(r.find('.//n:netAssets', ns).text); shares = 26_548_823
growth = {'SPCX', 'FRVO', 'NXT', 'FSLR', 'ARRY', 'PRIM', 'VMI', 'HUBB', 'TT', 'MWH'}
pipes_rails = {'LNG', 'TRGP', 'WMB', 'TRP', 'UNP', 'CP'}
rows = []
for p in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'listed_holdings_prices.csv'))):
    v = val[p['nport_name']]; ch = float(p['close_2026_11_13'])/float(p['close_2026_06_30']) - 1
    rows.append((v*ch/shares, p['ticker'], v, ch))
rows.sort()
for c, t, v, ch in rows:
    print(f"{t:5} ${v/1e6:5.1f}m held  {ch:+6.1%}  {c:+.3f} a BUI share")
cov = sum(x[2] for x in rows)
print(f"covered: ${cov/1e6:,.0f}m, {cov/net:.0%} of 30 Jun net assets; total {sum(x[0] for x in rows):+.2f} a share")
for name, grp in (('growth and equipment (SpaceX, Fervo, solar, grid gear)', growth), ('pipelines and railroads', pipes_rails)):
    g = [x for x in rows if x[1] in grp]
    print(f"{name}: ${sum(x[2] for x in g)/1e6:,.0f}m held, {sum(x[0] for x in g):+.2f} a share")
u = [x for x in rows if x[1] not in growth | pipes_rails]
print(f"utilities and other: ${sum(x[2] for x in u)/1e6:,.0f}m held, {sum(x[0] for x in u):+.2f} a share")
