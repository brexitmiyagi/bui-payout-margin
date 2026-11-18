"""What BUI actually owns.

Full book from the June 30, 2026 N-PORT (the latest with every position; September's is due around November 29),
grouped into buckets I assigned by hand in data/holding_buckets.csv. Top ten from BlackRock's site as of October 30.
The buckets are my judgement: Exelon is a wires-only utility, NextEra also owns a big renewables developer, and so on.
"""
import os
import xml.etree.ElementTree as ET
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
out = []
p = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))

root = ET.parse(os.path.join(DATA, "nport", "0001410368-26-085641.xml")).getroot()
N = root.tag.split("}")[0][1:]
rows = []
for s in root.iter("{%s}invstOrSec" % N):
    rows.append({"name": s.find("{%s}name" % N).text, "pct": float(s.find("{%s}pctVal" % N).text),
                 "country": s.find("{%s}invCountry" % N).text})
h = pd.DataFrame(rows).sort_values("pct", ascending=False)
b = pd.read_csv(os.path.join(DATA, "holding_buckets.csv")).set_index("name_in_nport").bucket
h["bucket"] = h.name.map(b)
assert h.bucket.notna().all(), "unbucketed holding: %s" % h[h.bucket.isna()].name.tolist()
p("June 30, 2026: %d positions, top ten %.1f%% of net assets, top twenty %.1f%%" % (len(h), h.pct.head(10).sum(), h.pct.head(20).sum()))
g = h.groupby("bucket").pct.agg(["sum", "count"]).sort_values("sum", ascending=False)
p("\nby bucket (% of net assets, positions):")
p(g.round(1).to_string())
p("\nUS-listed or US-domiciled: %.1f%%; outside the US: %.1f%%" % (h[h.country == "US"].pct.sum(), h[h.country != "US"].pct.sum()))
t10 = pd.read_csv(os.path.join(DATA, "bui_top10_2026_10_30.csv"))
p("\nOctober 30 top ten (BlackRock): %.1f%% of net assets" % t10.weight_pct.sum())
p(t10[["name", "weight_pct"]].to_string(index=False))
nonutil = g.drop(["US regulated utilities", "non-US utilities and grid operators", "cash"], errors="ignore")["sum"].sum()
p("\noutside utilities (pipelines, rail, airports, gases, equipment, renewables, space): %.1f%% of net assets" % nonutil)
p("not held on June 30: the US independent power producers (Vistra, Constellation, Talen, NRG) and GE Vernova")
g.to_csv(os.path.join(RES, "holdings_lookthrough.csv"))
open(os.path.join(RES, "holdings_lookthrough.txt"), "w").write("\n".join(out) + "\n")
