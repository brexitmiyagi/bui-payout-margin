# Testing the explanation, not just asserting it. If utilities lost their equity beta because the AI-power premium
# came out of them, the names that rallied most in 2025 should show the biggest drop in equity beta in 2026.
# 34 US utilities and power producers. For each: 2025 price return, and the change in weekly equity beta (on the
# equal-weight S&P 500, with the 10-year change in the model) from 2025 to 2026. Then the rank correlation, with a
# permutation p-value.
import csv, os, datetime as dt, random
import numpy as np, statsmodels.api as sm
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
U = list(csv.DictReader(open(os.path.join(DATA, 'us_utilities_daily_2025_2026.csv'))))
F = {r['date']: r for r in csv.DictReader(open(os.path.join(DATA, 'factors_and_peer_navs_daily.csv')))}
y = {r['observation_date']: float(r['DGS10']) for r in csv.DictReader(open(os.path.join(DATA, 'dgs10.csv'))) if r['DGS10'] not in ('', '.')}
tickers = [k for k in U[0] if k != 'date']
fri = [r for r in U if dt.date.fromisoformat(r['date']).weekday() == 4 and r['date'] in F and r['date'] in y]
def beta(tk, yr):
    P = []
    for a, b in zip(fri, fri[1:]):
        if b['date'][:4] != str(yr) or not a[tk] or not b[tk]: continue
        P.append((float(b[tk])/float(a[tk])-1, y[b['date']]-y[a['date']], float(F[b['date']]['rsp_close'])/float(F[a['date']]['rsp_close'])-1))
    Y = np.array([p[0] for p in P]); X = sm.add_constant(np.array([[p[1], p[2]] for p in P]))
    return sm.OLS(Y, X).fit().params[2]
def px(tk, d):
    v = [r[tk] for r in U if r['date'] <= d and r[tk]]; return float(v[-1])
res = []
for tk in tickers:
    r25 = px(tk, '2025-12-31')/px(tk, '2024-12-31') - 1
    res.append((tk, r25, beta(tk, 2025), beta(tk, 2026)))
res.sort(key=lambda x: -x[1])
for tk, r25, b25, b26 in res:
    print(f"{tk:5} 2025 return {r25:+6.1%}  equity beta 2025 {b25:+.2f} -> 2026 {b26:+.2f}  change {b26-b25:+.2f}")
def rank(v): o = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v); [r.__setitem__(i, k) for k, i in enumerate(o)]; return r
a = rank([r[1] for r in res]); b = rank([r[3]-r[2] for r in res])
rho = float(np.corrcoef(a, b)[0, 1])
random.seed(1); bb = list(b); cnt = 0
for _ in range(10000):
    random.shuffle(bb)
    if float(np.corrcoef(a, bb)[0, 1]) <= rho: cnt += 1
print(f"Spearman correlation, 2025 return vs change in equity beta: {rho:+.2f} (one-sided permutation p = {cnt/10000:.3f}, n = {len(res)})")
top = res[:len(res)//3]; bot = res[-(len(res)//3):]
print(f"top third by 2025 return: average beta change {np.mean([r[3]-r[2] for r in top]):+.2f}; bottom third: {np.mean([r[3]-r[2] for r in bot]):+.2f}")
