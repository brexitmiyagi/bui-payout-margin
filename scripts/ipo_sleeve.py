# The 2026 IPO names in BUI's June 30 book: SpaceX (the fund says it "participated in the company's initial public
# offering"), Fervo and SOLV Energy (both new since December 31 and both 2026 IPOs). June 30 value from N-PORT,
# November 13 value at the Nasdaq close if the shares were still held. Whether BUI bought Fervo and SOLV in the IPO
# itself isn't disclosed.
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
px = {r['ticker']: r for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'listed_holdings_prices.csv')))}
book = [('SPCX', 'SpaceX', 131_270, 135.00, '12 Jun 2026'), ('FRVO', 'Fervo Energy', 105_378, 27.00, '12 May 2026'),
        ('MWH', 'SOLV Energy', 107_962, 25.00, '10 Feb 2026')]
shares = 26_548_823
t0 = t1 = 0
for tk, name, n, ipo, when in book:
    a, b = float(px[tk]['close_2026_06_30']), float(px[tk]['close_2026_11_13'])
    t0 += n*a; t1 += n*b
    print(f"{name}: {n:,} shares, IPO ${ipo:.2f} ({when}), 30 Jun ${a:.2f} (${n*a/1e6:.2f}m), 13 Nov ${b:.2f} (${n*b/1e6:.2f}m), "
          f"{b/ipo-1:+.1%} vs IPO")
print(f"together: ${t0/1e6:.1f}m on 30 Jun, ${t1/1e6:.1f}m on 13 Nov if held, {(t1-t0)/shares:+.2f} a BUI share")
# Against the IPO prices: did the three add to the year since BUI dropped its calls? Valued at IPO price (whether
# BUI paid exactly that isn't disclosed), the three together, as a share of the June 30 net assets ($741.7m).
c0 = sum(n*ipo for _, _, n, ipo, _ in book)
print(f"at IPO prices ${c0/1e6:.1f}m, 13 Nov ${t1/1e6:.1f}m: {(t1-c0)/1e6:+.1f}m, {(t1-c0)/741.66e6:+.2%} of June 30 net assets")
