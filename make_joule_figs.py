"""Three Joule composite figures with capital panel letters (Cell Press style)."""
import numpy as np
from ccus_style import plt, panel, INK, MUT
from matplotlib.patches import Rectangle
import plots as P

geo_ccus, geo_uhs, geo_bh, ccus_attr = P.load_all()

# ============ FIGURE 1: state of play (A world, B-E zooms, F bars, G scatter) ============
fig = plt.figure(figsize=(7.2, 7.6), dpi=400)
gs = fig.add_gridspec(3, 4, height_ratios=[2.1, 1.05, 1.25], hspace=0.30, wspace=0.09,
                      left=0.015, right=0.985, top=0.965, bottom=0.075)
axw = fig.add_subplot(gs[0, :])
P.basemap(axw, (-170, 180), (-58, 78))
P.map_layers(axw, geo_ccus, geo_uhs, geo_bh, ccus_attr, smin=5, smax=90, alpha=0.7, lw=0.3)
axw.set_anchor("S")
panel(axw, "A", "Global co-location of CCUS projects, underground hydrogen storage, and hydrogen-with-CCS production", y=1.012, x=0.0)
letters = ["B", "C", "D", "E"]
for i, (name, xl, yl) in enumerate(P.ZOOMS):
    ax = fig.add_subplot(gs[1, i])
    P.basemap(ax, xl, yl)
    P.map_layers(ax, geo_ccus, geo_uhs, geo_bh, ccus_attr, smin=11, smax=180, alpha=0.8, lw=0.5)
    ax.set_anchor("N")
    panel(ax, letters[i], name, y=1.035, x=0.0, fs_letter=8, fs_desc=8.3)
    axw.add_patch(Rectangle((xl[0], yl[0]), xl[1]-xl[0], yl[1]-yl[0],
                            fill=False, edgecolor="#8A8A8A", linewidth=0.8, zorder=6))
    axw.text(xl[0] + 1, yl[1] + 1.5, letters[i], fontsize=8.5, color="#5A5A5A", fontweight="bold")
    for text, x, y, ha in P.ZOOM_NOTES[i]:
        ax.text(x, y, text, fontsize=6.4, color=INK, ha=ha, va="bottom",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#CCCCCC", lw=0.4, alpha=0.9))
gsb = gs[2, :].subgridspec(1, 2, width_ratios=[1.12, 1], wspace=0.24)
axf = fig.add_subplot(gsb[0])
P.draw_region_status(axf, ccus_attr)
panel(axf, "F", "CCUS pipeline by region and status", y=1.05)
axg = fig.add_subplot(gsb[1])
P.draw_country_scatter(axg)
panel(axg, "G", "Country-level co-occurrence", y=1.05)
fig.legend(handles=P.map_legend_handles(), loc="lower center", ncol=4, frameon=False,
           fontsize=7.5, bbox_to_anchor=(0.5, 0.002), columnspacing=1.0, handletextpad=0.4)
fig.savefig("/home/claude/ccus_uhs/JouleFig1_state_of_play.png", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig1_state_of_play.pdf", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig1_state_of_play.svg", bbox_inches="tight")
plt.close(fig)
print("Joule Fig 1 saved")

# ============ FIGURE 2: concept + LCA (A schematic, B ladder) ============
fig = plt.figure(figsize=(7.2, 6.2), dpi=400)
gs = fig.add_gridspec(2, 1, height_ratios=[1.12, 1], hspace=0.30,
                      left=0.055, right=0.985, top=0.955, bottom=0.075)
axa = fig.add_subplot(gs[0])
P.draw_schematic(axa)
panel(axa, "A", "Coupling CCUS and UHS through the blue-hydrogen value chain", y=1.02, x=0.0)
axb = fig.add_subplot(gs[1])
P.draw_ladder(axb)
panel(axb, "B", "Harmonized life-cycle emissions of hydrogen pathways", y=1.05, x=-0.16)
fig.savefig("/home/claude/ccus_uhs/JouleFig2_concept_lca.png", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig2_concept_lca.pdf", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig2_concept_lca.svg", bbox_inches="tight")
plt.close(fig)
print("Joule Fig 2 saved")

# ============ FIGURE 3: quantitative + survival (A-F) ============
fig = plt.figure(figsize=(7.2, 7.8), dpi=400)
gs = fig.add_gridspec(3, 2, hspace=0.50, wspace=0.32,
                      left=0.095, right=0.985, top=0.955, bottom=0.06)
gsa = gs[0, 0].subgridspec(2, 1, hspace=0.14)
ax1 = fig.add_subplot(gsa[0]); ax2 = fig.add_subplot(gsa[1], sharex=ax1)
P.draw_scurves(ax1, ax2)
panel(ax1, "A", "Cumulative build-out", y=1.16)
axb = fig.add_subplot(gs[0, 1])
P.draw_cdf(axb)
panel(axb, "B", "Nearest-neighbour distances")
axc = fig.add_subplot(gs[1, 0])
P.draw_attrition(axc)
panel(axc, "C", "Termination rate by sector", x=-0.30)
axd = fig.add_subplot(gs[1, 1])
P.draw_basins(axd)
panel(axd, "D", "Active projects by basin", x=-0.22)
axe = fig.add_subplot(gs[2, 0])
P.draw_km(axe)
panel(axe, "E", "Kaplan–Meier survival, power-sector CCS")
axf = fig.add_subplot(gs[2, 1])
P.draw_strip(axf)
panel(axf, "F", "Time to termination, all 36 failures", x=-0.16)
fig.savefig("/home/claude/ccus_uhs/JouleFig3_analysis_survival.png", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig3_analysis_survival.pdf", bbox_inches="tight")
fig.savefig("/home/claude/ccus_uhs/JouleFig3_analysis_survival.svg", bbox_inches="tight")
plt.close(fig)
print("Joule Fig 3 saved")
