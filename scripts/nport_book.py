# What BUI's quarterly N-PORT filings show: the call-writing book disappearing after November 2025, monthly NAV
# returns, and realised gains month by month (the fuel for the payout).
import os, glob, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'n': 'http://www.sec.gov/edgar/nport'}
total_by_q = {}
for f in sorted(glob.glob(os.path.join(HERE, '..', 'data', 'nport', '*.xml')), key=lambda f: ET.parse(f).getroot().find('.//n:repPdDate', ns).text):
    r = ET.parse(f).getroot()
    q = r.find('.//n:repPdDate', ns).text
    secs = r.findall('.//n:invstOrSec', ns)
    der = [s for s in secs if s.find('.//n:derivativeInfo', ns) is not None]
    net = float(r.find('.//n:netAssets', ns).text)
    rt = r.find('.//n:monthlyTotReturn', ns).attrib
    real = []
    for k in ('1', '2', '3'):
        a = r.find(f'.//n:instrMon{k}', ns); b = r.find(f'.//n:othMon{k}', ns)
        real.append(float(a.attrib['netRealizedGain']) + float(b.attrib['netRealizedGain']))
    opt = [float(r.find(f'.//n:instrMon{k}', ns).attrib['netRealizedGain']) for k in ('1', '2', '3')]
    print(f"quarter to {q}: net assets ${net/1e6:,.1f}m, {len(secs)} positions of which {len(der)} derivatives (written calls), "
          f"monthly NAV returns {float(rt['rtn1']):.2f}% / {float(rt['rtn2']):.2f}% / {float(rt['rtn3']):.2f}%, realised gains ${sum(real)/1e6:,.1f}m "
          f"(options ${sum(opt)/1e6:,.1f}m)")
    total_by_q[q] = sum(real)
h1 = total_by_q.get('2026-03-31', 0) + total_by_q.get('2026-06-30', 0)
print(f"realised gains first half 2026 from N-PORT: ${h1/1e6:,.1f}m (statement of operations: $43.1m)")
