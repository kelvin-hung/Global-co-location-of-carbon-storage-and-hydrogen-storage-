"""Shared Nature-style figure system for the CCUS-UHS paper."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

_avail = {f.name for f in font_manager.fontManager.ttflist}
for _f in ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]:
    if _f in _avail:
        FAMILY = _f
        break

plt.rcParams.update({
    "font.family": FAMILY,
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5,
    "axes.edgecolor": "#9A9A9A", "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.dpi": 400,
})

INK, MUT = "#1A1A1A", "#666666"
BLUE = "#0072B2"    # CCUS / CO2 chain
TEAL = "#009E73"    # UHS / H2 storage
ORANGE = "#E69F00"  # H2/NH3 production with CCS
VERM = "#D55E00"    # emphasis / failure
GREY = "#BDB9B1"    # inactive / cancelled
GRID = "#ECEAE6"

def panel(ax, letter, descriptor="", x=-0.02, y=1.06, fs_letter=11, fs_desc=8.5, dx=0.055):
    """Nature-style bold panel letter + regular-weight short descriptor."""
    ax.text(x, y, letter, transform=ax.transAxes, fontweight="bold",
            fontsize=fs_letter, va="bottom", ha="left", color=INK)
    if descriptor:
        ax.text(x + dx, y + 0.004, descriptor, transform=ax.transAxes,
                fontsize=fs_desc, va="bottom", ha="left", color=INK)

def despine(ax, keep=("left", "bottom")):
    for s in ["top", "right", "left", "bottom"]:
        ax.spines[s].set_visible(s in keep)
