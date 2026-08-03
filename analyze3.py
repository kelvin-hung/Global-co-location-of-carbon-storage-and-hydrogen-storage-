"""Supplemental analyses: proximity sensitivity, survival robustness, country detail, LCA spread."""
import csv, json, math, re
import numpy as np
from collections import Counter, defaultdict

D = "/home/claude/ccus_uhs"

def read_psv(path):
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f, delimiter="|") if r and any(x.strip() for x in r)]
    return rows[0], rows[1:]

def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# ---------- load ----------
_, gc = read_psv(f"{D}/data/geo_ccus.psv")
geo_ccus = {r[0]: (float(r[2]), float(r[3])) for r in gc}
ccus = {}
for fn in ["ccus_americas.psv", "ccus_emea.psv", "ccus_apac.psv"]:
    h, dd = read_psv(f"{D}/data/{fn}")
    for r in dd:
        ccus[r[0]] = dict(zip(h, r))
with open(f"{D}/data/geo_uhs_blueh2.psv") as f:
    txt = f.read()
uhs_lines = [l.split("|") for l in txt.split("===UHS===")[1].split("===BLUEH2===")[0].strip().splitlines()[1:]]
uhs_pts = {r[0]: (float(r[2]), float(r[3])) for r in uhs_lines}

def active(st): s = st.lower(); return not ("cancel" in s or "suspend" in s)
def operational(st): return "operational" in st.lower()
def dedicated(a):
    t = a["storage_type"].lower()
    return ("saline" in t or "depleted" in t or "mineral" in t)

sets = {
    "active (baseline)": [(geo_ccus[n]) for n, a in ccus.items() if active(a["status"]) and n in geo_ccus],
    "operational only": [(geo_ccus[n]) for n, a in ccus.items() if operational(a["status"]) and n in geo_ccus],
    "active, dedicated storage only": [(geo_ccus[n]) for n, a in ccus.items()
                                       if active(a["status"]) and dedicated(a) and n in geo_ccus],
}
prox = {}
for label, pts in sets.items():
    ds = sorted(min(hav(la, lo, cla, clo) for cla, clo in pts) for la, lo in uhs_pts.values())
    med = ds[len(ds)//2]
    w100 = 100 * sum(1 for x in ds if x <= 100) / len(ds)
    w200 = 100 * sum(1 for x in ds if x <= 200) / len(ds)
    prox[label] = {"dists": ds, "median": round(med), "w100": round(w100), "w200": round(w200), "n_ref": len(pts)}
    print(f"S1 {label}: n_ref={len(pts)} median={med:.0f} km, <=100km {w100:.0f}%, <=200km {w200:.0f}%")

# ---------- survival sensitivity ----------
h, sv = read_psv(f"{D}/data/survival.psv")
sv = [dict(zip(h, r)) for r in sv]
power = [x for x in sv if x["group"] == "power"]

def km(data):
    data = sorted(data)
    times = sorted({t for t, d in data if d == 1})
    S = 1.0
    kt, ks = [0.0], [1.0]
    for t in times:
        n_risk = sum(1 for tt, _ in data if tt >= t)
        d_t = sum(1 for tt, dd in data if tt == t and dd == 1)
        S *= (1 - d_t / n_risk)
        kt.append(t); ks.append(S)
    return kt, ks

def build(events="all", min_conf=False):
    out = []
    for x in power:
        if min_conf and x["confidence"] == "low":
            continue
        t = max(int(x["event_year"]) - int(x["announcement_year"]), 0.5)
        if x["db_outcome"] == "death":
            is_cancel = True
            if events == "cancelled_only":
                nm = x["project_name"]
                # suspended projects (treated as censored under cancelled-only)
                susp = {"Project Tundra (Milton R. Young)", "Mendota BECCS (Clean Energy Systems)",
                        "Calpine Sutter Decarbonization Project", "Poza Rica CCUS pilot",
                        "GreenGen IGCC Capture Phase", "Drax BECCS"}
                is_cancel = nm not in susp
            out.append((t, 1 if is_cancel else 0))
        else:
            out.append((t, 0))
    return out

variants = {
    "baseline (n=56, events=22)": build(),
    "cancellations only as events (n=56, events=16)": build(events="cancelled_only"),
    "excluding low-confidence records": build(min_conf=True),
}
km_out = {}
for lab, data in variants.items():
    kt, ks = km(data)
    km_out[lab] = {"t": kt, "s": ks, "n": len(data), "events": sum(d for _, d in data)}
    def S_at(x): return next(ks[i] for i in range(len(kt)-1, -1, -1) if kt[i] <= x)
    print(f"S2 {lab}: n={len(data)} events={sum(d for _,d in data)} S(5)={S_at(5):.2f} S(10)={S_at(10):.2f}")

# termination calendar (all 36 failures)
term_years = [int(x["event_year"]) for x in sv if x["db_outcome"] == "death"]
cal = Counter(term_years)
print("S2 termination calendar:", dict(sorted(cal.items())))

# ---------- country detail ----------
def sg(s):
    s = s.lower()
    if "cancel" in s or "suspend" in s: return "Cancelled/suspended"
    if "pilot" in s or "injection completed" in s: return "Pilot"
    if "operational" in s: return "Operational"
    if "construction" in s: return "Under construction"
    if "advanced" in s: return "Advanced development"
    return "Planned"
cstat = defaultdict(Counter); ccap = defaultdict(float)
for a in ccus.values():
    cstat[a["country"]][sg(a["status"])] += 1
    if active(a["status"]):
        try: ccap[a["country"]] += float(a["capture_capacity_MtCO2_per_yr"])
        except ValueError: pass
top = sorted(cstat, key=lambda c: -sum(cstat[c].values()))[:15]
country_detail = {c: {"stat": dict(cstat[c]), "cap": round(ccap[c], 1)} for c in top}
print("S3 top-15 countries:", [(c, sum(cstat[c].values()), round(ccap[c],1)) for c in top])

# ---------- LCA per-study spread ----------
h, lca = read_psv(f"{D}/data/lca_h2.psv")
lca = [dict(zip(h, r)) for r in lca]
def fam(p):
    p = p.lower()
    if "grey" in p or "gray" in p: return "Grey"
    if "blue" in p: return "Blue"
    if "turquoise" in p: return "Turquoise"
    if "green" in p: return "Green"
    return "Other"
studies = []
for r in lca:
    if "kg CO2e/kg H2" not in r["gwp_unit"]:
        continue
    lo = hi = mid = None
    try: mid = float(r["gwp_central"])
    except ValueError: pass
    m = re.match(r"^\s*(-?[\d.]+)\s*[-–]\s*(-?[\d.]+)", r["gwp_range"])
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
    if mid is None and lo is None:
        continue
    if lo is None: lo = hi = mid
    if mid is None: mid = (lo + hi) / 2
    studies.append({"study": r["study"], "year": int(r["year"]), "fam": fam(r["pathway"]),
                    "lo": lo, "mid": mid, "hi": hi, "pathway": r["pathway"]})
print(f"S4 LCA study records plotted: {len(studies)}")

json.dump({"prox": prox, "km": km_out, "cal": dict(cal), "country": country_detail,
           "top_order": top, "lca_studies": studies},
          open(f"{D}/analysis3.json", "w"))
print("analysis3.json saved")
