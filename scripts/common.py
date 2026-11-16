# Shared loaders. Prices: Nasdaq daily closes (BUI, XLU, SPY). NAV: Nasdaq's XBUIX, the fund's daily NAV.
# Distributions: BlackRock's BUI distribution table (ex-dates and amounts).
import csv, os, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))

def daily():
    out = []
    for r in rows('bui_price_nav_daily.csv'):
        out.append(dict(d=dt.date.fromisoformat(r['date']), px=float(r['bui_close']), nav=float(r['bui_nav']),
                        xlu=float(r['xlu_close']) if r['xlu_close'] else None, spy=float(r['spy_close']) if r['spy_close'] else None))
    return out

def dists():
    return {dt.date.fromisoformat(r['ex_date']): float(r['amount']) for r in rows('bui_distributions.csv')}

def nav_tr_index(D, dist):
    # NAV total return: reinvest each distribution at NAV on its ex-date. The XBUIX NAV on the ex-date is ex-distribution.
    idx = [1.0]
    for a, b in zip(D, D[1:]):
        div = sum(v for k, v in dist.items() if a['d'] < k <= b['d'])
        idx.append(idx[-1] * (b['nav'] + div) / a['nav'])
    return idx

def at(D, day):
    k = [x for x in D if x['d'] <= day]
    return k[-1]
