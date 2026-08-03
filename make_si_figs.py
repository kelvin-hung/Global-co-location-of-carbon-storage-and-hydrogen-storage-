"""Supplemental figures S1-S4 (Cell Press SI style, capital panel letters)."""
import json
import numpy as np
from ccus_style import plt, panel, despine, INK, MUT, BLUE, TEAL, ORANGE, VERM, GREY, GRID

D = "/home/claude/ccus_uhs"
A = json.load(open(f"{D}/analysis3.json"))

def save(fig, name):
    fig.savefig(f"{D}/{name}.png", bbox_inches="tight")
    fig.savefig(f"{D}/{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"{name} saved")

# ============ FIGURE S1: proximity sensitivity ============
fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 3.1), dpi=400,
                               gridspec_kw=dict(wspace=0.34, left=0.075, right=0.985,
                                                top=0.86, bottom=0.16))
COLS = {"active (baseline)": TEAL,
        "operational only": BLUE,
        "active, dedicated storage only": ORANGE}
LABS = {"active (baseline)": "All active CCUS (baseline)",
        "operational only": "Operational CCUS only",
        "active, dedicated storage only": "Active, dedicated storage only"}
for key, col in COLS.items():
    ds = np.clip(np.array(A["prox"][key]["dists"]), 1, None)
    y = 100 * np.arange(1, len(ds) + 1) / len(ds)
    axa.step(ds, y, where="post", color=col, lw=1.6, label=LABS[key])
axa.set_xscale("log")
axa.set_xlim(1, 4000)
axa.set_ylim(0, 100)
axa.axvline(100, color="#CCCCCC", lw=0.7, ls=":")
axa.text(107, 3, "100 km", fontsize=7.3, color=MUT)
axa.set_xlabel("UHS site to nearest CCUS project (km, log)")
axa.set_ylabel("Share of UHS sites (%)")
despine(axa)
axa.grid(color=GRID, lw=0.5)
axa.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 1.04),
           handlelength=1.2, fontsize=7.3)
panel(axa, "A", "Distance distributions under three CCUS reference sets", y=1.06, x=-0.10)

keys = list(COLS)
x = np.arange(3)
w = 0.27
med = [A["prox"][k]["median"] for k in keys]
w100 = [A["prox"][k]["w100"] for k in keys]
w200 = [A["prox"][k]["w200"] for k in keys]
axb2 = axb.twinx()
b1 = axb.bar(x - w, med, w, color=[COLS[k] for k in keys], alpha=0.9)
b2 = axb2.bar(x, w100, w, color=[COLS[k] for k in keys], alpha=0.55)
b3 = axb2.bar(x + w, w200, w, color=[COLS[k] for k in keys], alpha=0.3)
for xi, v in zip(x - w, med):
    axb.text(xi, v + 6, f"{v}", ha="center", fontsize=7.3, color=INK)
for xi, v in zip(x, w100):
    axb2.text(xi, v + 1.2, f"{v}%", ha="center", fontsize=7.3, color=INK)
for xi, v in zip(x + w, w200):
    axb2.text(xi, v + 1.2, f"{v}%", ha="center", fontsize=7.3, color=INK)
axb.set_xticks(x)
axb.set_xticklabels(["All active\n(baseline)", "Operational\nonly", "Active, dedicated\nstorage only"], fontsize=7.6)
axb.set_ylabel("Median distance (km)")
axb2.set_ylabel("Share of UHS sites (%)", color=MUT)
axb2.tick_params(axis="y", colors=MUT)
axb.set_ylim(0, 420)
axb2.set_ylim(0, 78)
despine(axb, keep=("left", "bottom"))
axb2.spines["top"].set_visible(False)
axb2.spines["left"].set_visible(False)
axb.text(0.99, 0.97, "solid bar: median km\nmid bar: share ≤100 km\nlight bar: share ≤200 km",
         transform=axb.transAxes, ha="right", va="top", fontsize=7.0, color=MUT,
         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#DDDDDD", lw=0.5))
panel(axb, "B", "Summary statistics by reference set", y=1.06, x=-0.14, dx=0.075)
save(fig, "JouleFigS1_proximity_sensitivity")

# ============ FIGURE S2: survival robustness + termination calendar ============
fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 3.1), dpi=400,
                               gridspec_kw=dict(wspace=0.30, left=0.075, right=0.985,
                                                top=0.86, bottom=0.16))
KCOLS = {"baseline (n=56, events=22)": VERM,
         "cancellations only as events (n=56, events=16)": BLUE,
         "excluding low-confidence records": TEAL}
KLABS = {"baseline (n=56, events=22)": "Baseline (56 projects, 22 events)",
         "cancellations only as events (n=56, events=16)": "Cancellations only (16 events)",
         "excluding low-confidence records": "Excluding low-confidence (47 projects)"}
for key, col in KCOLS.items():
    kt, ks = A["km"][key]["t"], A["km"][key]["s"]
    axa.step(kt + [17], ks + [ks[-1]], where="post", color=col, lw=1.6, label=KLABS[key])
axa.set_xlim(0, 17)
axa.set_ylim(0, 1.02)
axa.set_xlabel("Years since project announcement")
axa.set_ylabel("Survival probability S(t)")
despine(axa)
axa.grid(color=GRID, lw=0.5)
axa.legend(frameon=False, loc="lower left", fontsize=7.2, handlelength=1.2)
panel(axa, "A", "Kaplan–Meier sensitivity, power-sector CCS", y=1.06, x=-0.10)

cal = {int(k): v for k, v in A["cal"].items()}
years = list(range(2010, 2026))
counts = [cal.get(y, 0) for y in years]
cols = [VERM if y >= 2024 else GREY for y in years]
axb.bar(years, counts, color=cols, width=0.75)
for y, c in zip(years, counts):
    if c:
        axb.text(y, c + 0.12, str(c), ha="center", fontsize=7.3, color=INK)
axb.set_xlabel("Year of cancellation or suspension")
axb.set_ylabel("Terminated projects")
axb.set_xticks(range(2010, 2026, 3))
axb.set_ylim(0, 8.2)
despine(axb)
axb.grid(axis="y", color=GRID, lw=0.5)
axb.text(0.02, 0.95, "13 of 36 terminations occurred\nin 2024–2025 (red bars)",
         transform=axb.transAxes, ha="left", va="top", fontsize=7.4, color="#B03A00")
panel(axb, "B", "Calendar of the 36 recorded terminations", y=1.06, x=-0.12, dx=0.075)
save(fig, "JouleFigS2_survival_robustness")

# ============ FIGURE S3: top-15 country detail ============
fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 3.8), dpi=400,
                               gridspec_kw=dict(width_ratios=[1.5, 1], wspace=0.10,
                                                left=0.14, right=0.985, top=0.90, bottom=0.13))
order = A["top_order"]
SCOLS = [("Operational", TEAL), ("Under construction", BLUE), ("Advanced development", "#7FB8D8"),
         ("Planned", GREY), ("Pilot", ORANGE), ("Cancelled/suspended", VERM)]
ypos = np.arange(len(order))[::-1]
left = np.zeros(len(order))
for lab, col in SCOLS:
    vals = np.array([A["country"][c]["stat"].get(lab, 0) for c in order], dtype=float)
    axa.barh(ypos, vals, left=left, color=col, height=0.68, label=lab)
    left += vals
axa.set_yticks(ypos)
axa.set_yticklabels(order, fontsize=7.8)
axa.set_xlabel("CCUS projects in database")
axa.set_xlim(0, 58)
for yi, tot in zip(ypos, left):
    axa.text(tot + 0.7, yi, f"{int(tot)}", va="center", fontsize=7.2, color=MUT)
despine(axa)
axa.grid(axis="x", color=GRID, lw=0.5)
axa.legend(frameon=False, fontsize=7.0, loc="lower right", handlelength=1.0,
           bbox_to_anchor=(1.0, 0.02))
panel(axa, "A", "Project count by status, top 15 countries", y=1.02, x=-0.26)

caps = [A["country"][c]["cap"] for c in order]
axb.barh(ypos, caps, color=BLUE, height=0.68)
axb.set_yticks(ypos)
axb.set_yticklabels([])
axb.set_xlabel("Active capture capacity (Mt CO$_2$ yr$^{-1}$)")
axb.set_xlim(0, 92)
for yi, v in zip(ypos, caps):
    axb.text(v + 1.4, yi, f"{v:g}", va="center", fontsize=7.2, color=MUT)
despine(axb)
axb.grid(axis="x", color=GRID, lw=0.5)
panel(axb, "B", "Active capture capacity", y=1.02, x=-0.02, dx=0.09)
save(fig, "JouleFigS3_country_detail")

# ============ FIGURE S4: study-level LCA spread ============
fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 3.4), dpi=400,
                               gridspec_kw=dict(width_ratios=[1.75, 1], wspace=0.26,
                                                left=0.07, right=0.985, top=0.88, bottom=0.15))
FCOL = {"Grey": "#8A8A8A", "Blue": BLUE, "Turquoise": TEAL, "Green": "#4DAF4A"}
FOFF = {"Grey": -0.27, "Blue": -0.09, "Turquoise": 0.09, "Green": 0.27}
rng_state = 0
YCAP = 21.0
for s in A["lca_studies"]:
    x = s["year"] + FOFF[s["fam"]]
    col = FCOL[s["fam"]]
    if s["lo"] is not None and s["hi"] is not None and s["hi"] > s["lo"]:
        hi_draw = min(s["hi"], YCAP)
        axa.plot([x, x], [s["lo"], hi_draw], color=col, lw=1.4, alpha=0.65,
                 solid_capstyle="round")
        if s["hi"] > YCAP:
            axa.annotate("", (x, YCAP + 0.8), (x, YCAP), arrowprops=dict(
                arrowstyle="-|>", color=col, lw=1.1))
            axa.text(x + 0.25, YCAP + 0.1, f"extends to {s['hi']:g}",
                     fontsize=6.8, color=MUT, va="center")
    axa.scatter([x], [s["mid"]], s=16, color=col, edgecolor="white", lw=0.5, zorder=5)
for fam, col in FCOL.items():
    axa.scatter([], [], s=16, color=col, label=fam)
axa.set_xlabel("Publication year")
axa.set_ylabel("kg CO$_2$e per kg H$_2$ (GWP100)")
axa.set_xlim(2011.3, 2025.7)
axa.set_ylim(-0.5, 22.6)
axa.axhspan(1, 4, color=TEAL, alpha=0.07, lw=0)
axa.text(2011.6, 4.4, "harmonized blue-H$_2$\nrange in main text (1–4)",
         fontsize=7.0, color="#00795A", va="bottom")
despine(axa)
axa.grid(color=GRID, lw=0.5)
axa.legend(frameon=False, fontsize=7.2, loc="upper right", ncol=4,
           handletextpad=0.1, columnspacing=0.8, bbox_to_anchor=(1.0, 1.05))
panel(axa, "A", "Study-level GWP estimates by publication year", y=1.05, x=-0.075)

fams = ["Grey", "Blue", "Turquoise", "Green"]
for i, fam in enumerate(fams):
    mids = [s["mid"] for s in A["lca_studies"] if s["fam"] == fam]
    los = [s["lo"] for s in A["lca_studies"] if s["fam"] == fam]
    his = [s["hi"] for s in A["lca_studies"] if s["fam"] == fam]
    lo, hi = min(los), max(his)
    hi_draw = min(hi, YCAP)
    med = float(np.median(mids))
    axb.plot([i, i], [lo, hi_draw], color=FCOL[fam], lw=5, alpha=0.25, solid_capstyle="round")
    axb.scatter([i], [med], s=42, color=FCOL[fam], edgecolor="white", lw=0.8, zorder=5)
    if hi > YCAP:
        axb.annotate("", (i, YCAP + 0.8), (i, YCAP), arrowprops=dict(
            arrowstyle="-|>", color=FCOL[fam], lw=1.1, alpha=0.6))
        axb.text(i - 0.16, YCAP - 0.15, f"to {hi:g}\nn={len(mids)}", ha="right",
                 va="top", fontsize=6.9, color=MUT)
    else:
        axb.text(i, hi_draw + 0.55, f"n={len(mids)}", ha="center", fontsize=7.2, color=MUT)
axb.set_xticks(range(4))
axb.set_xticklabels(fams, fontsize=7.8)
axb.set_xlim(-0.6, 3.6)
axb.set_ylim(-0.5, 22.6)
axb.set_ylabel("kg CO$_2$e per kg H$_2$")
despine(axb)
axb.grid(axis="y", color=GRID, lw=0.5)
panel(axb, "B", "Full range and median by pathway family", y=1.05, x=-0.17, dx=0.10)
save(fig, "JouleFigS4_lca_spread")
