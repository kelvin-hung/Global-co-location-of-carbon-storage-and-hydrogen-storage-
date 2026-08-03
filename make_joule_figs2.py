"""Joule Figures 4-6: CCUS anatomy, UHS anatomy, resources & readiness."""
import json
import numpy as np
from ccus_style import plt, panel, despine, INK, MUT, BLUE, TEAL, ORANGE, VERM, GREY, GRID

A2 = json.load(open("/home/claude/ccus_uhs/analysis2.json"))

# ================= FIGURE 4: anatomy of the CCUS fleet =================
fig = plt.figure(figsize=(7.2, 6.2), dpi=400)
gs = fig.add_gridspec(2, 2, hspace=0.55, wspace=0.42, left=0.14, right=0.97, top=0.94, bottom=0.09)

# (A) capacity by sector
axa = fig.add_subplot(gs[0, 0])
cs = A2["cap_by_sector"]; ns = A2["n_by_sector"]
order = sorted(cs, key=lambda k: cs[k])
vals = [cs[k] for k in order]
cols = [VERM if k == "Power" else ("#08519C" if k == "Storage hubs" else "#9DBFD8") for k in order]
y = np.arange(len(order))
axa.barh(y, vals, color=cols, height=0.62, edgecolor="white", lw=0.7)
for yi, v, k in zip(y, vals, order):
    axa.text(v + 3, yi, f"{v:.0f}  (n={ns[k]})", va="center", fontsize=7, color=INK)
axa.set_yticks(y); axa.set_yticklabels(order, fontsize=7.5)
axa.set_xlabel("Active capture/injection capacity (Mt CO$_2$/yr)")
axa.set_xlim(0, 235)
despine(axa, keep=("bottom",)); axa.tick_params(axis="y", length=0)
axa.grid(axis="x", color=GRID, lw=0.5)
panel(axa, "A", "Where the megatons are", x=-0.38)

# (B) fate transition by cohort (capacity-weighted, operational)
axb = fig.add_subplot(gs[0, 1])
cohorts = ["1972-1999", "2000-2009", "2010-2014", "2015-2019", "2020-2026"]
FATES = [("EOR", "#B0784A"), ("Dedicated: saline aquifer", BLUE), ("Dedicated: depleted field", "#6BAED6"),
         ("Mineralization", TEAL), ("Utilization (no storage)", "#CFCBC4"), ("TBD/unspecified", "#E8E5DF")]
x = np.arange(len(cohorts))
bottom = np.zeros(len(cohorts))
for f, col in FATES:
    shares = []
    for c in cohorts:
        d = A2["fate_coh_cap"][c]; tot = sum(d.values())
        shares.append(100 * d.get(f, 0) / tot if tot else 0)
    axb.bar(x, shares, bottom=bottom, color=col, width=0.66, edgecolor="white", lw=0.7,
            label=f.replace("Dedicated: ", "Ded. "))
    for xi, s, b in zip(x, shares, bottom):
        if s >= 12:
            axb.text(xi, b + s / 2, f"{s:.0f}", ha="center", va="center", fontsize=6.8,
                     color="white" if f != "Utilization (no storage)" else INK)
    bottom += np.array(shares)
axb.set_xticks(x); axb.set_xticklabels([c.replace("-", "–\n") for c in cohorts], fontsize=7)
axb.set_ylabel("Share of cohort capacity (%)")
axb.set_ylim(0, 100)
despine(axb); axb.grid(axis="y", color=GRID, lw=0.5)
axb.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.42, -0.20), ncol=3,
           fontsize=6.4, handlelength=0.9, columnspacing=0.6, handletextpad=0.4)
panel(axb, "B", "Storage fate by start cohort (operational)", x=-0.20)

# (C) project scale by decade + pipeline
axc = fig.add_subplot(gs[1, 0])
decs = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
rng = np.random.default_rng(7)
for i, d in enumerate(decs):
    vals = A2["dec_caps"].get(d, [])
    if not vals: continue
    xs = i + (rng.random(len(vals)) - 0.5) * 0.4
    axc.scatter(xs, vals, s=14, color=BLUE, alpha=0.55, edgecolor="white", lw=0.4, zorder=3)
    med = float(np.median(vals))
    axc.plot([i - 0.26, i + 0.26], [med, med], color=INK, lw=1.2, zorder=4)
futv = A2["fut_caps"]
PX = 6.45
xs = PX + (rng.random(len(futv)) - 0.5) * 0.4
axc.scatter(xs, futv, s=14, color=ORANGE, alpha=0.6, edgecolor="white", lw=0.4, zorder=3)
medf = float(np.median(futv))
axc.plot([PX - 0.26, PX + 0.26], [medf, medf], color=INK, lw=1.2, zorder=4)
axc.text(PX + 0.42, medf, f"median\n{medf:g}", fontsize=7.2, color="#B25000",
         va="center", ha="left", linespacing=1.1)
axc.text(0.02, 0.05, "operating median 0.1–0.2\n(2010s–2020s)", transform=axc.transAxes,
         fontsize=7.2, color=MUT, ha="left", va="bottom")
axc.set_yscale("log"); axc.set_ylim(0.0007, 30)
axc.set_xlim(-0.55, 7.6)
axc.set_xticks(list(range(len(decs))) + [6.45]); axc.set_xticklabels(decs + ["Pipeline\n(constr.+planned)"], fontsize=7.3)
axc.set_ylabel("Capture capacity (Mt CO$_2$/yr, log)")
despine(axc); axc.grid(axis="y", color=GRID, lw=0.5)
panel(axc, "C", "Project scale: operating fleet vs. pipeline", x=-0.22)

# (D) transport modes, pre-2020 vs 2020s starts
axd = fig.add_subplot(gs[1, 1])
MODES = [("Pipeline", "#08519C"), ("On-site", "#9DBFD8"), ("Ship", ORANGE), ("Pipeline + ship", "#E8B85B"), ("Truck/rail", "#CFCBC4")]
groups = [("Starts before 2020\n(n = 64)", A2["mode_pre2020"]), ("Starts 2020–2031\n(n = 87)", A2["mode_2020s"])]
x = np.arange(len(groups))
bottom = np.zeros(len(groups))
for m, col in MODES:
    shares = []
    for _, d in groups:
        tot = sum(d.values())
        shares.append(100 * d.get(m, 0) / tot if tot else 0)
    axd.bar(x, shares, bottom=bottom, color=col, width=0.5, edgecolor="white", lw=0.8, label=m)
    for xi, s, b in zip(x, shares, bottom):
        if s >= 6:
            axd.text(xi, b + s / 2, f"{s:.0f}", ha="center", va="center", fontsize=7,
                     color="white" if col in ("#08519C",) else INK)
    bottom += np.array(shares)
axd.set_xticks(x); axd.set_xticklabels([g for g, _ in groups], fontsize=7.8)
axd.set_ylabel("Share of active projects (%)")
axd.set_ylim(0, 100)
despine(axd); axd.grid(axis="y", color=GRID, lw=0.5)
axd.legend(frameon=False, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7.3, handlelength=1.0)
panel(axd, "D", "CO$_2$ transport by project vintage", x=-0.20)

fig.savefig("/home/claude/ccus_uhs/JouleFig4_ccus_anatomy.png", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig4_ccus_anatomy.pdf", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig4_ccus_anatomy.svg", bbox_inches="tight")
plt.close(fig)
print("Fig 4 saved")

# ================= FIGURE 5: anatomy of the UHS fleet =================
fig = plt.figure(figsize=(7.2, 6.0), dpi=400)
gs = fig.add_gridspec(2, 2, hspace=0.52, wspace=0.38, left=0.11, right=0.97, top=0.94, bottom=0.09)

MEDIA = [("Salt cavern", TEAL), ("Depleted field", "#0072B2"), ("Aquifer", "#9DBFD8"), ("Lined rock cavern", ORANGE)]
STATS = ["Historical (town gas)", "Completed pilot", "Operating/demonstration", "Under construction", "Planned/proposed", "Study/feasibility"]

# (A) medium x status stacked bars
axa = fig.add_subplot(gs[0, 0])
mm = A2["uhs_mm"]
x = np.arange(len(STATS))
bottom = np.zeros(len(STATS))
for med, col in MEDIA:
    vals = [mm.get(f"{med}|{st}", 0) for st in STATS]
    axa.bar(x, vals, bottom=bottom, color=col, width=0.6, edgecolor="white", lw=0.8, label=med)
    for xi, v, b in zip(x, vals, bottom):
        if v >= 2:
            axa.text(xi, b + v / 2, int(v), ha="center", va="center", fontsize=7, color="white")
    bottom += np.array(vals)
axa.set_xticks(x)
axa.set_xticklabels(["Town gas", "Pilot", "Op. /\ndemo", "Constr.", "Planned", "Study"], fontsize=8)
axa.set_ylabel("UHS sites (n = 39)")
despine(axa); axa.grid(axis="y", color=GRID, lw=0.5)
axa.legend(frameon=False, loc="upper right", fontsize=7.3, handlelength=1.0)
panel(axa, "A", "Storage media across maturity", x=-0.16)

# (B) depth vs start year
axb = fig.add_subplot(gs[0, 1])
medcol = dict(MEDIA)
for name, med, y_, d_, hs in A2["uhs_pts"]:
    if y_ and d_:
        axb.scatter([y_], [d_], s=26, color=medcol.get(med, GREY), edgecolor="white", lw=0.6, zorder=3)
axb.annotate("Teesside (1972)", (1972, 365), textcoords="offset points", xytext=(6, -10), fontsize=7, color=MUT)
axb.annotate("Spindletop (2016)", (2016, 1340), textcoords="offset points", xytext=(-70, -4), fontsize=7, color=MUT)
axb.annotate("Aldbrough (2030)", (2030, 1800), textcoords="offset points", xytext=(-72, -4), fontsize=7, color=MUT)
axb.set_ylim(2900, 0)
axb.set_xlim(1950, 2033)
axb.set_xlabel("Start year"); axb.set_ylabel("Depth (m)")
despine(axb); axb.grid(color=GRID, lw=0.5)
panel(axb, "B", "Deeper with time", x=-0.20)

# (C) purity transition
axc = fig.add_subplot(gs[1, 0])
for name, med, y_, d_, hs in A2["uhs_pts"]:
    if y_ and hs is not None:
        axc.scatter([y_], [hs], s=26, color=medcol.get(med, GREY), edgecolor="white", lw=0.6, zorder=3)
axc.axhspan(45, 65, color="#F4EFE6", zorder=0)
axc.axhspan(0, 30, color="#EFF4F0", zorder=0)
axc.text(1991, 48.5, "town-gas era (50–62% H$_2$)", fontsize=7.5, color="#7A6420")
axc.text(1957, 13, "blend trials (5–25%)", fontsize=7.5, color="#3E6B52")
axc.text(1993, 88, "pure H$_2$ (95–100%)", fontsize=7, color="#00795A")
axc.set_xlim(1950, 2033); axc.set_ylim(0, 105)
axc.set_xlabel("Start year"); axc.set_ylabel("H$_2$ share of stored gas (%)")
despine(axc); axc.grid(color=GRID, lw=0.5)
panel(axc, "C", "The purity transition", x=-0.16)

# (D) operating working energy by site
axd = fig.add_subplot(gs[1, 1])
ops = sorted([(n, round(g, 1)) for n, g in A2["op_energy"]], key=lambda x: x[1])
names = [o[0].replace(" (Advanced Clean Energy Storage)", "").replace(" H2 caverns", "") for o in ops]
vals = [o[1] for o in ops]
colmap = {"Teesside": TEAL, "Clemens Dome": TEAL, "Moss Bluff": TEAL, "Spindletop": TEAL,
          "ACES Delta": TEAL, "H2CAST Etzel": "#7FCBB2", "HyPSTER": "#7FCBB2", "HPC Krummhörn": "#7FCBB2", "HyGeo": "#7FCBB2"}
cols = [colmap.get(n, TEAL) for n in names]
y = np.arange(len(names))
axd.barh(y, vals, color=cols, height=0.6, edgecolor="white", lw=0.6)
for yi, v in zip(y, vals):
    axd.text(v * 1.15, yi, f"{v:g}", va="center", fontsize=6.8, color=MUT)
axd.set_yticks(y); axd.set_yticklabels(names, fontsize=7.3)
axd.set_xscale("log"); axd.set_xlim(0.05, 4000)
axd.set_xlabel("Working H$_2$ energy (GWh, log)")
axd.axvline(818, color=VERM, lw=0.9, ls=(0, (4, 3)))
axd.text(950, 8.45, "global operating\ntotal ≈ 0.8 TWh", fontsize=7.2, color=VERM, va="top", ha="left")
despine(axd, keep=("bottom",)); axd.tick_params(axis="y", length=0)
axd.grid(axis="x", color=GRID, lw=0.5)
panel(axd, "D", "Operating pure-H$_2$ stores (commercial + demo)", x=-0.26)

fig.savefig("/home/claude/ccus_uhs/JouleFig5_uhs_anatomy.png", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig5_uhs_anatomy.pdf", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig5_uhs_anatomy.svg", bbox_inches="tight")
plt.close(fig)
print("Fig 5 saved")

# ================= FIGURE 6: resources & readiness =================
fig = plt.figure(figsize=(7.2, 6.4), dpi=400)
gs = fig.add_gridspec(2, 2, hspace=0.52, wspace=0.42, left=0.15, right=0.97, top=0.94, bottom=0.07)

# (A) CO2 storage resource by country (log)
axa = fig.add_subplot(gs[0, 0])
co2res = [("USA", 3000, "USGS 2013, technically accessible"), ("Brazil", 2035, "CARBMAP, theoretical"),
          ("China", 1888, "Fan 2025, effective (median)"), ("Australia", 501, "OGCI SRMS"),
          ("South Korea", 203, "OGCI, undiscovered"), ("Poland", 200, "CO2StoP, theoretical"),
          ("Japan", 152, "OGCI SRMS"), ("Malaysia", 150, "OGCI, undiscovered"),
          ("Canada", 148, "OGCI SRMS"), ("UK", 78, "BGS CO2Stored, P50"),
          ("Norway", 75, "Offshore Directorate atlases"), ("UAE", 16.7, "OGCI SRMS")]
co2res = co2res[::-1]
y = np.arange(len(co2res))
axa.barh(y, [v for _, v, _ in co2res], color=BLUE, height=0.62, edgecolor="white", lw=0.6)
for yi, (c, v, b) in zip(y, co2res):
    axa.text(v * 1.15, yi, f"{v:g}", va="center", fontsize=6.8, color=MUT)
axa.set_yticks(y); axa.set_yticklabels([c for c, _, _ in co2res], fontsize=7.5)
axa.set_xscale("log"); axa.set_xlim(8, 9000)
axa.set_xlabel("Assessed CO$_2$ storage resource (Gt, log)")
despine(axa, keep=("bottom",)); axa.tick_params(axis="y", length=0)
axa.grid(axis="x", color=GRID, lw=0.5)
panel(axa, "A", "National CO$_2$ storage resources", x=-0.30)

# (B) H2 cavern potential (log TWh)
axb = fig.add_subplot(gs[0, 1])
h2res = [("Europe (total)", 84800, "Caglayan 2020"), ("Germany", 35700, "Caglayan 2020"),
         ("Netherlands", 10400, "Caglayan 2020"), ("UK (salt, national)", 9000, "Caglayan 2020"),
         ("Norway (offshore)", 7500, "Caglayan 2020"), ("UK bedded halite", 2151, "Williams 2022"),
         ("USA (UGS repurpose)", 327, "Lackey 2023"), ("Poland (7 domes)", 126, "Lankof 2022")]
h2res = h2res[::-1]
y = np.arange(len(h2res))
axb.barh(y, [v for _, v, _ in h2res], color=TEAL, height=0.62, edgecolor="white", lw=0.6)
for yi, (c, v, s) in zip(y, h2res):
    axb.text(v * 1.15, yi, f"{v:,}", va="center", fontsize=6.8, color=MUT)
axb.set_yticks(y); axb.set_yticklabels([c for c, _, _ in h2res], fontsize=7.5)
axb.set_xscale("log"); axb.set_xlim(50, 700000)
axb.set_xlabel("Technical H$_2$ storage potential (TWh, log)")
despine(axb, keep=("bottom",)); axb.tick_params(axis="y", length=0)
axb.grid(axis="x", color=GRID, lw=0.5)
panel(axb, "B", "Hydrogen cavern potential", x=-0.34)

# (C) the deployment gap
axc = fig.add_subplot(gs[1, 0])
tiers = [("Operating pure-H$_2$ stores\n(this database, 2026)", 0.82, TEAL),
         ("Under construction + consented\n(HyStock, Bad Lauchstädt, Aldbrough,\nHyNet, GHH Denmark)", 2.2, "#7FCBB2"),
         ("US gas-storage repurposing\npotential (Lackey 2023)", 327, "#5FA8D3"),
         ("Europe salt-cavern technical\npotential (Caglayan 2020)", 84800, BLUE)]
y = np.arange(len(tiers))[::-1]
axc.barh(y, [t[1] for t in tiers], color=[t[2] for t in tiers], height=0.6, edgecolor="white", lw=0.6)
for yi, (lab, v, _) in zip(y, tiers):
    axc.text(v * 1.2, yi, (f"{v:,.0f} TWh" if v >= 10 else f"{v:g} TWh"), va="center", fontsize=7.3, color=INK)
axc.set_yticks(y); axc.set_yticklabels([t[0] for t in tiers], fontsize=7)
axc.set_xscale("log"); axc.set_xlim(0.3, 3e6)
axc.set_xlabel("Working H$_2$ energy (TWh, log)")
axc.text(0.975, 0.82, "five orders of magnitude between\noperating stores and technical potential",
         transform=axc.transAxes, fontsize=7.2, color=VERM, ha="right", va="center")
despine(axc, keep=("bottom",)); axc.tick_params(axis="y", length=0)
axc.grid(axis="x", color=GRID, lw=0.5)
panel(axc, "C", "The deployment gap", x=-0.52)

# (D) basin readiness matrix
axd = fig.add_subplot(gs[1, 1])
basins = ["US Gulf Coast", "Alberta–Williston", "NW Europe", "Eastern China", "Arabian Platform", "SE Australia", "NW Australia", "Sarawak–Malay"]
crits = ["Operating CO$_2$\nstorage", "Operating /\nproven UHS", "H$_2$+CCS\nanchor", "CO$_2$ resource\nassessed", "H$_2$ potential\nassessed", "Single\njurisdiction"]
#         scores: 2 = in place, 1 = partial/proposed, 0 = absent
M = np.array([
    [2, 2, 2, 2, 1, 2],   # Gulf Coast
    [2, 1, 2, 2, 1, 1],   # Alberta-Williston (salt proven, cavern proposed; 2 jurisdictions)
    [2, 2, 2, 2, 2, 0],   # NW Europe (5 jurisdictions)
    [1, 1, 1, 2, 1, 2],   # E China (EOR-dominant; demos)
    [2, 0, 2, 1, 0, 2],   # Arabian Platform
    [1, 1, 0, 2, 0, 2],   # SE Australia
    [1, 0, 0, 2, 0, 2],   # NW Australia
    [1, 0, 0, 1, 0, 1],   # Sarawak-Malay
])
from matplotlib.colors import ListedColormap
cmap = ListedColormap(["#F1EFEA", "#A8D2C4", "#00795A"])
axd.imshow(M, cmap=cmap, aspect="auto", vmin=0, vmax=2)
axd.set_xticks(range(len(crits))); axd.set_xticklabels([c.replace("\n", " ") for c in crits], fontsize=6.5, rotation=28, ha="right")
axd.set_yticks(range(len(basins))); axd.set_yticklabels(basins, fontsize=7.5)
for i in range(len(basins)):
    for j in range(len(crits)):
        axd.text(j, i, ["–", "◐", "●"][M[i, j]], ha="center", va="center",
                 fontsize=8.5, color="white" if M[i, j] == 2 else ("#3E6B52" if M[i, j] == 1 else "#B0ACA4"))
axd.set_xticks(np.arange(-0.5, len(crits)), minor=True)
axd.set_yticks(np.arange(-0.5, len(basins)), minor=True)
axd.grid(which="minor", color="white", lw=1.4)
axd.tick_params(length=0, which="both")
for s in axd.spines.values(): s.set_visible(False)
axd.text(0.0, -0.40, "● in place   ◐ partial/proposed   – absent", transform=axd.transAxes,
         fontsize=7.3, color=MUT)
panel(axd, "D", "Basin readiness matrix", x=-0.34)

fig.savefig("/home/claude/ccus_uhs/JouleFig6_resources_readiness.png", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig6_resources_readiness.pdf", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig6_resources_readiness.svg", bbox_inches="tight")
plt.close(fig)
print("Fig 6 saved")
