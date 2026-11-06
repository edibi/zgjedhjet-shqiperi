# Power BI Python visual: pie charts of the vote by unit, drawn over the Tirana boundaries.
# Fields: Njesia administrative, Longitude, Latitude, Grupimi i partive, Vota.
import json
import math

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon, Wedge

TOPOJSON = r"C:\zgjedhjet-shqiperi\data\gjeografi\tirana_njesite_administrative.topojson"
BG, LAND, CITY, EDGE, TEXT = "#1F1F1F", "#3A3A3A", "#4A4A4A", "#6E6D6B", "#F5F5F5"
COLORS = {
    "PS + PSD": "#5E3894", "PS": "#5E3894", "PSD": "#0C5D34", "PD-ASHM": "#00529C",
    "MUNDESIA": "#FFC04D", "NISMA-SHB": "#F48221", "BASHKE": "#E82D36", "Te tjeret": "#9E9E9E",
}
ORDER = ["PS + PSD", "PS", "PSD", "PD-ASHM", "MUNDESIA", "NISMA-SHB", "BASHKE", "Te tjeret"]
K = math.cos(math.radians(41.33))

UNIT, LON, LAT = "NjA", "Longitude", "Latitude"
vote_col = next(c for c in dataset.columns if c.startswith("Vota"))
group_col = next(c for c in dataset.columns if c not in (UNIT, LON, LAT, vote_col))

topo = json.load(open(TOPOJSON, encoding="utf-8"))
shapes = {g["id"]: topo["arcs"][g["arcs"][0][0]] for g in topo["objects"]["njesite"]["geometries"]}


def short(name):
    return name.replace("NjA ", "")


def is_city(name):
    return name.startswith("NjA")


units = []
for name, rows in dataset.groupby(UNIT):
    votes = rows.groupby(group_col)[vote_col].sum()
    votes = votes[votes > 0]
    if votes.sum() == 0:
        continue
    x, y = float(rows[LON].iloc[0]) * K, float(rows[LAT].iloc[0])
    units.append({"name": name, "votes": votes, "total": float(votes.sum()), "x0": x, "y0": y, "x": x, "y": y})


def label(u):
    return f"{short(u['name'])} · {u['votes'].max() / u['total']:.0%}"


def separate(items, gap, unit_per_pt, size):
    # Push overlapping pies and their labels apart; each pie keeps a leader line to its true position.
    lh = size * 1.5 * unit_per_pt
    for u in items:
        u["hw"] = max(u["r"], len(label(u)) * size * 0.3 * unit_per_pt)
    for _ in range(600):
        moved = False
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                ay, by = a["y"] - lh / 2, b["y"] - lh / 2
                ox = a["hw"] + b["hw"] + gap - abs(b["x"] - a["x"])
                oy = a["r"] + b["r"] + lh + gap - abs(by - ay)
                if ox > 0 and oy > 0:
                    moved = True
                    if ox < oy:
                        s = 1 if b["x"] >= a["x"] else -1
                        a["x"] -= s * ox / 2
                        b["x"] += s * ox / 2
                    else:
                        s = 1 if by >= ay else -1
                        a["y"] -= s * oy / 2
                        b["y"] += s * oy / 2
        if not moved:
            break


def draw_pie(ax, u, size):
    start = 90.0
    ordered = sorted(u["votes"].items(), key=lambda kv: ORDER.index(kv[0]) if kv[0] in ORDER else 99)
    for group, value in ordered:
        sweep = 360.0 * value / u["total"]
        ax.add_patch(Wedge((u["x"], u["y"]), u["r"], start - sweep, start,
                           facecolor=COLORS.get(group, "#9E9E9E"), edgecolor=BG, linewidth=0.5, zorder=4))
        start -= sweep
    if math.hypot(u["x"] - u["x0"], u["y"] - u["y0"]) > u["r"]:
        ax.add_line(Line2D([u["x0"], u["x"]], [u["y0"], u["y"]], color=TEXT, linewidth=0.6, alpha=0.7, zorder=3))
        ax.plot([u["x0"]], [u["y0"]], "o", color=TEXT, markersize=size * 0.2, zorder=3)
    ax.text(u["x"], u["y"] - u["r"] * 1.06, label(u), ha="center", va="top", color=TEXT, fontsize=size, zorder=5)


def draw_panel(ax, title, names_with_pies, r_max, gap, size, bounds=None):
    ax.set_facecolor(BG)
    for name, ring in shapes.items():
        pts = [(x * K, y) for x, y in ring]
        ax.add_patch(Polygon(pts, closed=True, facecolor=CITY if is_city(name) else LAND,
                             edgecolor=EDGE, linewidth=0.6, zorder=1))
    if bounds is None:
        xs = [p[0] * K for r in shapes.values() for p in r]
        ys = [p[1] for r in shapes.values() for p in r]
        bounds = (min(xs), max(xs), min(ys), max(ys))
    pad = 0.012
    ax.set_xlim(bounds[0] - pad, bounds[1] + pad)
    ax.set_ylim(bounds[2] - pad, bounds[3] + pad)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.apply_aspect()
    box = ax.get_window_extent()
    unit_per_pt = (ax.get_xlim()[1] - ax.get_xlim()[0]) / (box.width / ax.figure.dpi * 72)
    items = [u for u in units if u["name"] in names_with_pies]
    biggest = max((u["total"] for u in items), default=1)
    for u in items:
        u["x"], u["y"] = u["x0"], u["y0"]
        u["r"] = max(r_max * math.sqrt(u["total"] / biggest), r_max * 0.3)
    separate(items, gap, unit_per_pt, size)
    for u in items:
        draw_pie(ax, u, size)
    ax.set_title(title, color=TEXT, fontsize=size * 1.5, loc="left", pad=6)


fig = plt.gcf()
fig.set_facecolor(BG)
scale = fig.get_size_inches()[0] / 13.0
small = max(6.0, 7.5 * scale)
left = fig.add_axes([0.01, 0.09, 0.47, 0.84])
right = fig.add_axes([0.5, 0.09, 0.49, 0.84])

city_xy = [(x * K, y) for n, r in shapes.items() if is_city(n) for x, y in r]
city_bounds = (min(p[0] for p in city_xy), max(p[0] for p in city_xy), min(p[1] for p in city_xy), max(p[1] for p in city_xy))
names = [u["name"] for u in units]
draw_panel(left, "Njësitë rurale", [n for n in names if not is_city(n)], 0.026, 0.002, small)
draw_panel(right, "Qyteti i Tiranës (Nr. 1–11)", [n for n in names if is_city(n)], 0.0085, 0.0006, small, city_bounds)
fig.text(0.99, 0.965, "Përqindja = grupi i parë në njësi. Madhësia e rrethit tregon votat brenda secilës hartë.",
         ha="right", color=TEXT, fontsize=small)

present = [g for g in ORDER if g in set(dataset[group_col])] + [g for g in dataset[group_col].unique() if g not in ORDER]
fig.legend(handles=[Patch(facecolor=COLORS.get(g, "#9E9E9E"), label=g) for g in present], loc="lower center",
           ncol=len(present), frameon=False, labelcolor=TEXT, fontsize=small * 1.15)
plt.show()
