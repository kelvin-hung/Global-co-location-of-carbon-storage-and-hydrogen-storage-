"""Fleet-anatomy analyses for Joule Figures 4-6."""
import csv, json, re
import numpy as np
from collections import Counter, defaultdict

D = "/home/claude/ccus_uhs"

def read_psv(path):
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f, delimiter="|") if r and any(x.strip() for x in r)]
    return rows[0], rows[1:]

ccus = []
for fn in ["ccus_americas.psv", "ccus_emea.psv", "ccus_apac.psv"]:
    h, dd = read_psv(f"{D}/data/{fn}")
    for r in dd:
        ccus.append(dict(zip(h, r)))

def active(st):
    s = st.lower(); return not ("cancel" in s or "suspend" in s)
def cap(r):
    try: return float(r["capture_capacity_MtCO2_per_yr"])
    except ValueError: return None
def year(r):
    try: return int(r["start_year"])
    except ValueError: return None

def sector_group(s):
    s = s.lower()
    if "power" in s: return "Power"
    if "hydrogen" in s or "ammonia" in s or "methanol" in s or "refin" in s or "synfuel" in s or "coal chemical" in s or "gasification" in s: return "H2/fuels/chemicals"
    if "storage" in s or "transport" in s: return "Storage hubs"
    if "gas processing" in s: return "Gas processing"
    if "ethanol" in s: return "Ethanol/BECCS"
    if "beccs" in s or "biomass" in s: return "Ethanol/BECCS"
    if "cement" in s: return "Cement"
    if "steel" in s: return "Steel"
    if "waste" in s: return "Waste-to-energy"
    if "dac" in s: return "DAC"
    return "Other"

def fate_group(s):
    s = s.lower()
    if "eor" in s: return "EOR"
    if "saline" in s: return "Dedicated: saline aquifer"
    if "depleted" in s: return "Dedicated: depleted field"
    if "basalt" in s or "mineral" in s: return "Mineralization"
    if "utilization" in s: return "Utilization (no storage)"
    return "TBD/unspecified"

# ---- A: capacity by sector (active only, disclosed capacity) ----
cap_by_sector = defaultdict(float); n_by_sector = Counter(); nd = 0
for r in ccus:
    if active(r["status"]):
        g = sector_group(r["sector"]); n_by_sector[g] += 1
        c = cap(r)
        if c: cap_by_sector[g] += c
        else: nd += 1
print("A) active capacity by sector (Mt/yr):", {k: round(v,1) for k,v in sorted(cap_by_sector.items(), key=lambda x:-x[1])})
print("   active project counts:", dict(n_by_sector), "| active w/o disclosed capacity:", nd)

# ---- B: storage fate by 5-yr cohort (operational only, capacity-weighted + counts) ----
coh_bins = [(1972,1999),(2000,2009),(2010,2014),(2015,2019),(2020,2026)]
fate_coh_cap = {b: defaultdict(float) for b in coh_bins}
fate_coh_n = {b: Counter() for b in coh_bins}
for r in ccus:
    y = year(r)
    if y is None or not ("operational" in r["status"].lower()): continue
    for b in coh_bins:
        if b[0] <= y <= b[1]:
            f = fate_group(r["storage_type"])
            fate_coh_n[b][f] += 1
            c = cap(r)
            if c: fate_coh_cap[b][f] += c
print("B) operational fate shares by start cohort (capacity Mt/yr):")
for b in coh_bins:
    tot = sum(fate_coh_cap[b].values())
    if tot:
        shares = {k: round(100*v/tot) for k,v in fate_coh_cap[b].items()}
        print(f"   {b}: total {tot:.1f} Mt/yr; shares% {shares}")

# fate counts overall (all statuses, active)
fate_all = Counter(fate_group(r["storage_type"]) for r in ccus if active(r["status"]))
print("   active fate counts:", dict(fate_all))

# ---- C: project scale by start decade (operational, disclosed) ----
dec_caps = defaultdict(list)
for r in ccus:
    y = year(r); c = cap(r)
    if y and c and "operational" in r["status"].lower():
        dec = f"{(y//10)*10}s"
        dec_caps[dec].append(c)
print("C) median operational project capacity by decade:",
      {k: (round(float(np.median(v)),2), len(v)) for k,v in sorted(dec_caps.items())})

# planned/construction median
fut = [cap(r) for r in ccus if r["status"].lower() in ("under construction","advanced development","planned") and cap(r)]
print("   median capacity, under-construction/planned pipeline:", round(float(np.median(fut)),2), "n=", len(fut))

# ---- D: transport mode by era (active, by start year known or status-era) ----
def mode_group(m):
    m = m.lower()
    if "ship" in m and "pipeline" in m: return "Pipeline + ship"
    if "ship" in m: return "Ship"
    if "pipeline" in m: return "Pipeline"
    if "onsite" in m: return "On-site"
    if "truck" in m or "rail" in m: return "Truck/rail"
    return "NA"
mode_pre2020 = Counter(); mode_2020s = Counter()
for r in ccus:
    if not active(r["status"]): continue
    y = year(r)
    m = mode_group(r["co2_transport"])
    if m == "NA": continue
    if y and y < 2020: mode_pre2020[m] += 1
    elif y and y >= 2020: mode_2020s[m] += 1
print("D) transport modes pre-2020 starts:", dict(mode_pre2020))
print("   transport modes 2020s starts:", dict(mode_2020s))

# ---- UHS anatomy ----
h, uhs = read_psv(f"{D}/data/uhs.psv")
uhs = [dict(zip(h, r)) for r in uhs]
def medium(r):
    m = r["storage_medium"].lower()
    if "salt" in m: return "Salt cavern"
    if "depleted" in m: return "Depleted field"
    if "aquifer" in m: return "Aquifer"
    if "rock" in m: return "Lined rock cavern"
    return "Other"
def ustatus(r):
    s = r["status"].lower()
    if "historical" in s: return "Historical (town gas)"
    if "operational" in s or ("demonstration" in s and "under" not in s): return "Operating/demonstration"
    if "completed" in s: return "Completed pilot"
    if "construction" in s: return "Under construction"
    if "pilot" in s: return "Operating/demonstration"
    if "study" in s or "research" in s or "feasibility" in s: return "Study/feasibility"
    if "planned" in s or "proposed" in s: return "Planned/proposed"
    return "Other"
mm = Counter((medium(r), ustatus(r)) for r in uhs)
print("UHS medium x status:", dict(mm))

# depth vs year vs medium (for scatter)
pts = []
for r in uhs:
    try: d_ = float(r["depth_m"])
    except ValueError: d_ = None
    try: y_ = int(r["start_year"])
    except ValueError: y_ = None
    # h2 share
    hs = r["h2_share_percent"]
    try: hsv = float(hs.split("-")[-1])
    except (ValueError, AttributeError): hsv = None
    pts.append((r["project_name"], medium(r), y_, d_, hsv))
with_both = [p for p in pts if p[2] and p[3]]
print("UHS with year+depth:", len(with_both), "| with year+share:", len([p for p in pts if p[2] and p[4] is not None]))

# operating pure-H2 energy capacity (GWh), from capacity strings
def gwh(r):
    c = r["capacity"]; name = r["project_name"]
    m = re.search(r"([\d.]+)\s*GWh", c)
    if m: return float(m.group(1))
    m = re.search(r"([\d.]+)\s*TWh", c)
    if m: return float(m.group(1)) * 1000
    m = re.search(r"([\d.]+)\s*kt H2", c)
    if m: return float(m.group(1)) * 33.3
    m = re.search(r"([\d.]+)\s*t H2", c)
    if m: return float(m.group(1)) * 0.0333
    return None
op_energy = []
for r in uhs:
    if ustatus(r) in ("Operating/demonstration",) and medium(r) != "Aquifer":
        g = gwh(r)
        if g: op_energy.append((r["project_name"], g))
print("operating UHS energy (GWh):", [(n, round(g,1)) for n, g in op_energy], "| total:", round(sum(g for _, g in op_energy), 1))

json.dump({
    "cap_by_sector": {k: round(v, 2) for k, v in cap_by_sector.items()},
    "n_by_sector": dict(n_by_sector),
    "fate_coh_cap": {f"{b[0]}-{b[1]}": {k: round(v,2) for k,v in fate_coh_cap[b].items()} for b in coh_bins},
    "fate_all": dict(fate_all),
    "dec_caps": {k: v for k, v in dec_caps.items()},
    "fut_caps": fut,
    "mode_pre2020": dict(mode_pre2020), "mode_2020s": dict(mode_2020s),
    "uhs_mm": {f"{a}|{b}": c for (a, b), c in mm.items()},
    "uhs_pts": pts,
    "op_energy": op_energy,
}, open(f"{D}/analysis2.json", "w"))
print("saved analysis2.json")
