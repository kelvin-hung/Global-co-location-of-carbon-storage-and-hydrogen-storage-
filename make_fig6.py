"""Fig 6: Kaplan-Meier survival of power-sector CCS + time-to-termination of all 36 failures."""
import csv, json
import numpy as np
from ccus_style import plt, panel, despine, INK, MUT, BLUE, TEAL, ORANGE, VERM, GREY, GRID

rows = []
with open("/home/claude/ccus_uhs/data/survival.psv") as f:
    r = [x for x in csv.reader(f, delimiter="|") if x and any(c.strip() for c in x)]
h = r[0]
for x in r[1:]:
    rows.append(dict(zip(h, x)))

# --- Kaplan-Meier for the power cohort (n=56) ---
power = [x for x in rows if x["group"] == "power"]
data = []
for x in power:
    t = int(x["event_year"]) - int(x["announcement_year"])
    t = max(t, 0.5)  # same-year events -> 0.5 yr
    data.append((t, 1 if x["db_outcome"] == "death" else 0))
data.sort()
times = sorted({t for t, d in data if d == 1})
S, V = 1.0, 0.0
km_t, km_s, km_lo, km_hi = [0.0], [1.0], [1.0], [1.0]
for t in times:
    n_risk = sum(1 for tt, _ in data if tt >= t)
    d_t = sum(1 for tt, dd in data if tt == t and dd == 1)
    S *= (1 - d_t / n_risk)
    if n_risk > d_t:
        V += d_t / (n_risk * (n_risk - d_t))
    se = S * np.sqrt(V)
    km_t.append(t); km_s.append(S)
    km_lo.append(max(0, S - 1.96 * se)); km_hi.append(min(1, S + 1.96 * se))
n_deaths = sum(d for _, d in data)
print(f"power cohort n={len(power)}, deaths={n_deaths}")
for tt, ss in zip(km_t, km_s):
    if tt in (4, 5, 8, 10, 11): print(f"  S({tt}) = {ss:.2f}")
print("KM final S =", round(km_s[-1], 2), "at t =", km_t[-1])

cens = [(t, None) for t, d in data if d == 0]
death_times_power = [t for t, d in data if d == 1]
print("median time-to-death (power failures):", np.median(death_times_power))

nonp = [x for x in rows if x["group"] == "nonpower_failed"]
death_times_nonp = [max(int(x["event_year"]) - int(x["announcement_year"]), 0.5) for x in nonp]
print("median time-to-death (non-power failures):", np.median(death_times_nonp), "n =", len(nonp))

json.dump({"km_t": km_t, "km_s": km_s, "S5": km_s[min(range(len(km_t)), key=lambda i: abs(km_t[i]-5))],
           "power_deaths": death_times_power, "nonpower_deaths": death_times_nonp},
          open("/home/claude/ccus_uhs/km.json", "w"))

# --- figure ---
fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 2.7), dpi=400,
                               gridspec_kw={"wspace": 0.30, "left": 0.075, "right": 0.985,
                                            "top": 0.86, "bottom": 0.17})
# (a) KM curve
def stepify(t, s):
    xs, ys = [t[0]], [s[0]]
    for i in range(1, len(t)):
        xs += [t[i], t[i]]; ys += [s[i-1], s[i]]
    return xs, ys
xs, ys = stepify(km_t, km_s)
xlo, ylo = stepify(km_t, km_lo)
xhi, yhi = stepify(km_t, km_hi)
axa.fill_between(xlo, ylo, yhi, step=None, color=BLUE, alpha=0.14, lw=0)
axa.plot(xs, ys, color=BLUE, lw=1.6)
# censoring ticks
for t, d in data:
    if d == 0:
        s_at = next(km_s[i] for i in range(len(km_t)-1, -1, -1) if km_t[i] <= t)
        axa.plot([t], [s_at], marker="|", color=BLUE, ms=5, mew=1.0, alpha=0.6)
axa.set_xlim(0, 21); axa.set_ylim(0, 1.02)
axa.set_xlabel("Years since project announcement")
axa.set_ylabel("Survival probability")
i5 = max(i for i in range(len(km_t)) if km_t[i] <= 5)
i10 = max(i for i in range(len(km_t)) if km_t[i] <= 10)
axa.annotate(f"S(5 yr) = {km_s[i5]:.2f}", (5, km_s[i5]), textcoords="offset points",
             xytext=(8, 8), fontsize=6.2, color=INK,
             arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=0.6))
axa.annotate(f"S(10 yr) = {km_s[i10]:.2f}", (10, km_s[i10]), textcoords="offset points",
             xytext=(8, 8), fontsize=6.2, color=INK,
             arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=0.6))
axa.text(0.98, 0.06, f"Power-sector CCS cohort\nn = {len(power)}, events = {n_deaths}\nshaded: 95% CI (Greenwood)\nticks: censored",
         transform=axa.transAxes, fontsize=5.8, color=MUT, ha="right", va="bottom")
despine(axa)
axa.grid(axis="y", color=GRID, lw=0.5)
panel(axa, "a", "Kaplan–Meier survival, power-sector CCS")

# (b) time-to-termination strip plot
rng_offsets = {}
def jitter_y(vals, base):
    cnt = {}
    ys = []
    for v in vals:
        k = round(v)
        cnt[k] = cnt.get(k, 0) + 1
        ys.append(base + ((cnt[k] - 1) - (cnt[k] - 1) // 2 * 2) * 0.09 * (1 if cnt[k] % 2 else -1))
    return ys

groups = [("Power (n = 22)", death_times_power, VERM, 1.0),
          ("Non-power (n = 14)", death_times_nonp, "#8A8A8A", 0.0)]
for label, vals, col, base in groups:
    cnt = {}
    for v in sorted(vals):
        k = round(v * 2) / 2
        cnt[k] = cnt.get(k, 0) + 1
        off = (cnt[k] - 1) * 0.10 * (1 if cnt[k] % 2 == 0 else -1)
        axb.scatter([v], [base + off], s=26, color=col, alpha=0.85,
                    edgecolor="white", linewidths=0.6, zorder=3)
    med = float(np.median(vals))
    axb.plot([med, med], [base - 0.32, base + 0.32], color=INK, lw=1.2, zorder=4)
    axb.text(med, base + 0.40, f"median {med:g} yr", fontsize=6.2, color=INK, ha="center")
axb.set_yticks([0, 1]); axb.set_yticklabels(["Non-power\nfailures (n = 14)", "Power\nfailures (n = 22)"], fontsize=6.5)
axb.set_ylim(-0.7, 1.75)
axb.set_xlim(0, 12.5)
axb.set_xlabel("Years from announcement to cancellation or suspension")
despine(axb)
axb.tick_params(axis="y", length=0)
axb.grid(axis="x", color=GRID, lw=0.5)
panel(axb, "b", "Time to termination, all 36 failed projects")

fig.savefig("/home/claude/ccus_uhs/fig6_survival.png", bbox_inches="tight")
print("fig6 saved")
