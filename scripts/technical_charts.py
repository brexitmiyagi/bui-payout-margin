"""Data for the three technical charts in the post. Writes CSVs to results/ that go straight into Datawrapper.

rolling_rate_beta_weekly.csv  BUI's and XLU's rate beta (% move per +100bp in the 10-year), rolling 52 weeks, controlling
                              for the equal-weight S&P 500, semiconductors and oil (model M3 in rate_beta_tests.py),
                              with a 95% band from Newey-West standard errors for BUI
premium_zscore_daily.csv      BUI's premium against its own 60-day average, in standard deviations, since the calls went
                              away, with the -1.5 buy line used in premium_patterns.py
payout_nav_fan_monthly.csv    BUI NAV paths to December 2027 after paying $0.154 a month, 12-month blocks of its own
                              monthly NAV returns since November 2016 resampled (same draws as payout_cut_probability.py),
                              percentiles, with the 7.5% and 8.1% cut triggers
"""
import os, csv, random, datetime as dt
import numpy as np, pandas as pd, statsmodels.api as sm
from common import daily, dists, nav_tr_index

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data"); RES = os.path.join(HERE, "..", "results")
D = daily(); idx = nav_tr_index(D, dists())

# 1. rolling 52-week rate beta, model M3
y = {dt.date.fromisoformat(r['observation_date']): float(r['DGS10'])
     for r in csv.DictReader(open(os.path.join(DATA, 'dgs10.csv'))) if r['DGS10'] not in ('', '.')}
F = {dt.date.fromisoformat(r['date']): r for r in csv.DictReader(open(os.path.join(DATA, 'factors_and_peer_navs_daily.csv')))}
rows = []
for k, x in enumerate(D):
    d = x['d']; f = F.get(d)
    if d.weekday() != 4 or d not in y or not f or not x['xlu'] or '' in (f['rsp_close'], f['smh_close'], f['uso_close']):
        continue
    rows.append(dict(d=d, bui=idx[k], xlu=x['xlu'], rsp=float(f['rsp_close']), smh=float(f['smh_close']), uso=float(f['uso_close']), y10=y[d]))
W = []
for a, b in zip(rows, rows[1:]):
    c = {'d': b['d'], 'dy': b['y10'] - a['y10']}
    for s in ('bui', 'xlu', 'rsp', 'smh', 'uso'): c[s] = b[s] / a[s] - 1
    W.append(c)
out = []
for j in range(51, len(W)):
    P = W[j-51:j+1]
    X = sm.add_constant(np.array([[p['dy'], p['rsp'], p['smh'], p['uso']] for p in P]))
    rb = sm.OLS(np.array([p['bui'] for p in P]), X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
    rx = sm.OLS(np.array([p['xlu'] for p in P]), X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
    b, se = rb.params[1] * 100, rb.bse[1] * 100
    out.append({'Week': W[j]['d'], 'BUI rate beta': round(b, 2), 'BUI 95% low': round(b - 1.96 * se, 2),
                'BUI 95% high': round(b + 1.96 * se, 2), 'XLU rate beta': round(rx.params[1] * 100, 2)})
rb = pd.DataFrame(out).set_index('Week')
rb.to_csv(os.path.join(RES, 'rolling_rate_beta_weekly.csv'))
print("rolling 52w rate beta, latest %s: BUI %+.1f (95%% %+.1f to %+.1f), XLU %+.1f; min BUI %+.1f on %s"
      % (rb.index[-1], *rb.iloc[-1][['BUI rate beta', 'BUI 95% low', 'BUI 95% high', 'XLU rate beta']], rb['BUI rate beta'].min(), rb['BUI rate beta'].idxmin()))

# 2. premium z-score against its 60-day average
s = pd.Series({x['d']: (x['px'] / x['nav'] - 1) * 100 for x in D})
s.index = pd.to_datetime(s.index)
z = (s - s.rolling(60).mean()) / s.rolling(60).std()
zz = pd.DataFrame({'Premium z-score (60-day)': z.round(2), 'Buy line (-1.5)': -1.5, 'Rich line (+1.5)': 1.5}).loc['2025-11-01':].dropna()
zz.rename_axis('Date').to_csv(os.path.join(RES, 'premium_zscore_daily.csv'), date_format='%Y-%m-%d')
print("premium z-score %s: %+.2f; days under -1.5 since Nov 2025: %d" % (zz.index[-1].date(), zz.iloc[-1, 0], (zz.iloc[:, 0] < -1.5).sum()))

# 3. NAV fan, same draws as payout_cut_probability.py (seed 11, first pool)
random.seed(11)
me = {}
for k, x in enumerate(D):
    me[(x['d'].year, x['d'].month)] = idx[k]
keys = sorted(k for k in me if k <= (2026, 10))
pool = [me[keys[i]] / me[keys[i-1]] - 1 for i in range(1, len(keys))]
PAY, nav0, N = 0.154, D[-1]['nav'], 20000
months = [(2026, 12)] + [(2027, m) for m in range(1, 13)]
blocks = [pool[i:i+12] for i in range(0, len(pool) - 11)]
paths = []
for _ in range(N):
    rs = []
    while len(rs) < len(months):
        rs += random.choice(blocks)
    nav, path = nav0, []
    for r in rs[:len(months)]:
        nav = nav * (1 + r) - PAY
        path.append(nav)
    paths.append(path)
A = np.array(paths)
fan = pd.DataFrame({'Month': ['2026-11'] + ['%d-%02d' % m for m in months]})
for q, name in ((10, '10th percentile'), (25, '25th percentile'), (50, 'Median'), (75, '75th percentile'), (90, '90th percentile')):
    fan[name] = [round(nav0, 2)] + list(np.percentile(A, q, axis=0).round(2))
fan['Cut line at 8.1% of NAV ($22.81)'] = round(PAY * 12 / 0.081, 2)
fan['Cut line at 7.5% of NAV ($24.64)'] = round(PAY * 12 / 0.075, 2)
fan.to_csv(os.path.join(RES, 'payout_nav_fan_monthly.csv'), index=False)
print("NAV fan Dec 2027: 10th $%.2f, median $%.2f, 90th $%.2f" % tuple(fan.iloc[-1][['10th percentile', 'Median', '90th percentile']]))
