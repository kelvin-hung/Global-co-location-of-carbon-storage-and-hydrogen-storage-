"""Quantitative coupling analyses: proximity, build-out timeline, attrition, basin ranking."""
import csv, math, json
from collections import Counter, defaultdict

D = "/home/claude/ccus_uhs/data"

def read_psv(path):
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f, delimiter="|") if r and any(x.strip() for x in r)]
    return rows[0], rows[1:]

# --- load geo + attributes ---
_, gc = read_psv(f"{D}/geo_ccus.psv")
geo_ccus = {r[0]: (float(r[2]), float(r[3]), r[4]) for r in gc}
with open(f"{D}/geo_uhs_blueh2.psv") as f:
    txt = f.read()
def parse_block(block):
    lines = [l for l in block.strip().splitlines() if l.strip()]
    return {l.split("|")[0]: l.split("|")[1:6] for l in lines[1:]}
geo_uhs = parse_block(txt.split("===UHS===")[1].split("===BLUEH2===")[0])   # country, lat, lon, basin, conf
geo_bh = parse_block(txt.split("===BLUEH2===")[1])

ccus = {}
countries_ccus = set()
for fn in ["ccus_americas.psv", "ccus_emea.psv", "ccus_apac.psv"]:
    h, d = read_psv(f"{D}/{fn}")
    for r in d:
        ccus[r[0]] = dict(zip(h, r))
        countries_ccus.add(r[1])
_, uhs_rows = read_psv(f"{D}/uhs.psv")
_, bh_rows = read_psv(f"{D}/blueh2.psv")
countries_uhs = {r[1] for r in uhs_rows}
countries_bh = {r[1] for r in bh_rows}
def canon(c): return "United Kingdom" if c == "UK" else c
all_countries = {canon(c) for c in countries_ccus | countries_uhs | countries_bh}
print(f"countries: CCUS={len({canon(c) for c in countries_ccus})}, UHS={len({canon(c) for c in countries_uhs})}, "
      f"BlueH2={len({canon(c) for c in countries_bh})}, union={len(all_countries)}")

def active(st):
    s = st.lower(); return not ("cancel" in s or "suspend" in s)
def operational(st):
    return "operational" in st.lower() and "pilot" not in st.lower()

# --- proximity analysis (haversine) ---
def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

act_ccus_pts = [(geo_ccus[n][0], geo_ccus[n][1]) for n, a in ccus.items() if active(a["status"]) and n in geo_ccus]
uhs_pts = {n: (float(v[1]), float(v[2])) for n, v in geo_uhs.items()}
bh_active = {}
for r in bh_rows:
    st = r[3].lower()
    if "cancel" not in st and "paused" not in st and r[0] in geo_bh:
        v = geo_bh[r[0]]
        bh_active[r[0]] = (float(v[1]), float(v[2]))

uhs_nearest = {n: min(hav(la, lo, cla, clo) for cla, clo in act_ccus_pts) for n, (la, lo) in uhs_pts.items()}
dists = sorted(uhs_nearest.values())
def share_within(ds, km): return 100 * sum(1 for x in ds if x <= km) / len(ds)
med = dists[len(dists)//2]
print(f"UHS→nearest active CCUS: median={med:.0f} km; within 50km={share_within(dists,50):.0f}%; "
      f"100km={share_within(dists,100):.0f}%; 200km={share_within(dists,200):.0f}%; n={len(dists)}")

uhs_active_pts = list(uhs_pts.values())
bh_nearest = {n: min(hav(la, lo, ula, ulo) for ula, ulo in uhs_active_pts) for n, (la, lo) in bh_active.items()}
bd = sorted(bh_nearest.values())
print(f"BlueH2→nearest UHS: median={bd[len(bd)//2]:.0f} km; within 100km={share_within(bd,100):.0f}%; "
      f"200km={share_within(bd,200):.0f}%; 500km={share_within(bd,500):.0f}%; n={len(bd)}")
far = sorted(uhs_nearest.items(), key=lambda x: -x[1])[:5]
print("farthest UHS from CCUS:", [(n, round(d)) for n, d in far])
near = sorted(uhs_nearest.items(), key=lambda x: x[1])[:8]
print("nearest UHS to CCUS:", [(n, round(d)) for n, d in near])

# --- build-out timeline ---
cap_by_year = defaultdict(float)
for n, a in ccus.items():
    if operational(a["status"]):
        try:
            y = int(a["start_year"]); c = float(a["capture_capacity_MtCO2_per_yr"])
        except ValueError:
            continue
        cap_by_year[y] += c
years = list(range(1970, 2027))
cum = []; tot = 0
for y in years:
    tot += cap_by_year.get(y, 0); cum.append(tot)
print("cumulative operational capture capacity 2026:", round(tot, 1), "Mt/yr")
print("capacity milestones:", {y: round(c,1) for y, c in zip(years, cum) if y in (1996, 2005, 2010, 2015, 2020, 2024, 2026)})

uhs_year = []
for r in uhs_rows:
    try: uhs_year.append(int(r[5]))
    except ValueError: pass
uhs_cum = [sum(1 for y in uhs_year if y <= yy) for yy in years]
print("UHS cumulative sites (with known year) 2026:", uhs_cum[-1], "of", len(uhs_rows))

# --- attrition by sector ---
def sector_group(s):
    s = s.lower()
    if "power" in s or "beccs" in s and "power" in s: return "Power"
    if "hydrogen" in s or "ammonia" in s or "methanol" in s or "refin" in s or "synfuel" in s or "coal chemical" in s or "gasification" in s: return "H2/fuels/chemicals"
    if "storage" in s or "transport" in s: return "Storage hubs & transport"
    if "gas processing" in s: return "Gas processing"
    if "ethanol" in s: return "Ethanol/bioenergy"
    if "cement" in s or "steel" in s or "waste" in s or "pulp" in s or "soda" in s or "fertilizer" in s: return "Industry (cement/steel/other)"
    if "dac" in s: return "DAC"
    return "Other/pilot"
tot_by, dead_by = Counter(), Counter()
for n, a in ccus.items():
    g = sector_group(a["sector"])
    tot_by[g] += 1
    if not active(a["status"]): dead_by[g] += 1
print("attrition by sector:")
attr = {}
for g in tot_by:
    attr[g] = (dead_by[g], tot_by[g], round(100*dead_by[g]/tot_by[g]))
    print(f"  {g}: {dead_by[g]}/{tot_by[g]} = {attr[g][2]}%")

# regional attrition
reg_tot, reg_dead = Counter(), Counter()
regmap = {"ccus_americas.psv": "Americas", "ccus_emea.psv": "EMEA", "ccus_apac.psv": "Asia-Pacific"}
for fn, rg in regmap.items():
    h, d = read_psv(f"{D}/{fn}")
    for r in d:
        reg_tot[rg] += 1
        if not active(r[3]): reg_dead[rg] += 1
print("attrition by region:", {rg: f"{reg_dead[rg]}/{reg_tot[rg]}={100*reg_dead[rg]//reg_tot[rg]}%" for rg in reg_tot})

json.dump({
    "years": years, "ccus_cum_cap": cum, "uhs_cum": uhs_cum,
    "uhs_dists": dists, "bh_dists": bd, "attrition": attr,
}, open("/home/claude/ccus_uhs/analysis.json", "w"))
print("saved analysis.json")
