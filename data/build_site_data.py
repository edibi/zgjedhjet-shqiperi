"""Builds docs/data/site.json, the only data file the website loads.

Run from anywhere:  python data/build_site_data.py
"""
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "data", "site.json")

SHORT = {"PS": "PS", "PD-ASHM": "PD-ASHM", "NISMA-SHB": "Shqipëria Bëhet", "PSD": "PSD",
         "MUNDESIA": "Mundësia", "BASHKE": "L. Bashkë"}
MAIN = ["PS", "PD-ASHM", "PSD", "NISMA-SHB", "MUNDESIA", "BASHKE"]


def rows(*path):
    with open(os.path.join(DATA, *path), encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)


# ---- Parliament 2025: national and districts
national, regions = [], {}
for r in rows("kuvend-2025", "normalized", "party_results.csv"):
    if r["level"] == "national":
        national.append({"code": r["party_code"], "label": SHORT.get(r["party_code"], r["party_code"]),
                         "name": r["party_name"], "votes": int(r["votes_total"]), "abroad": int(r["votes_abroad"]),
                         "seats": int(r["seats"] or 0)})
    elif r["level"] == "region":
        q = regions.setdefault(r["region"], {"name": r["region"], "votes": {c: 0 for c in MAIN + ["TJERET"]},
                                             "seats": {c: 0 for c in MAIN + ["TJERET"]}})
        c = r["party_code"] if r["party_code"] in MAIN else "TJERET"
        q["votes"][c] += int(r["votes_total"])
        q["seats"][c] += int(r["seats"] or 0)
national.sort(key=lambda p: -p["votes"])
regions = sorted(regions.values(), key=lambda q: q["name"])
assert len(regions) == 12 and sum(p["seats"] for p in national) == 140
assert sum(p["votes"] for p in national) == 1606057
assert sum(sum(q["votes"].values()) for q in regions) == 1606057
assert sum(sum(q["seats"].values()) for q in regions) == 140

# ---- Tirana by unit
GROUPS = ["PS", "PSD", "PD-ASHM", "NISMA-SHB", "MUNDESIA", "BASHKE", "Te tjeret"]
units = {}
for r in rows("krahasime", "krahasimi_tirane_2023_2025.csv"):
    u = units.setdefault(r["Njesia administrative"], {"name": r["Njesia administrative"], "v23": [0] * 7, "v25": [0] * 7})
    u["v" + r["Viti"][2:]][GROUPS.index(r["Grupi i detajuar"])] += int(r["Vota"])
for r in rows("krahasime", "pjesemarrja_tirane_2023_2025.csv"):
    u = units[r["Njesia administrative"]]
    y = r["Viti"][2:]
    u["voters" + y], u["reg" + y] = int(r["Votues"]), int(r["Zgjedhes"])
units = sorted(units.values(), key=lambda u: (not u["name"].startswith("NjA"), len(u["name"]) if u["name"].startswith("NjA") else 0, u["name"]))
t25 = [sum(u["v25"][i] for u in units) for i in range(7)]
assert len(units) == 24 and sum(t25) == 340301 and t25[0] == 166571 and t25[2] == 109859
assert t25[3] + t25[4] + t25[5] == 41678

# ---- Map: project, simplify, write as SVG paths
with open(os.path.join(DATA, "gjeografi", "tirana_njesite_administrative.topojson"), encoding="utf-8") as f:
    topo = json.load(f)
K = math.cos(math.radians(41.33))
shapes = {g["id"]: topo["arcs"][g["arcs"][0][0]] for g in topo["objects"]["njesite"]["geometries"]}
assert set(shapes) == {u["name"] for u in units}
pts = [p for s in shapes.values() for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
W = 800
scale = W / ((x1 - x0) * K)
H = (y1 - y0) * scale


def simplify(p, tol):
    if len(p) < 3:
        return p
    (ax, ay), (bx, by) = p[0], p[-1]
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy)
    best, idx = 0, 0
    for i in range(1, len(p) - 1):
        px, py = p[i]
        d = abs(dy * (px - ax) - dx * (py - ay)) / n if n else math.hypot(px - ax, py - ay)
        if d > best:
            best, idx = d, i
    if best <= tol:
        return [p[0], p[-1]]
    return simplify(p[:idx + 1], tol)[:-1] + simplify(p[idx:], tol)


paths = {}
for name, ring in shapes.items():
    xy = [((x - x0) * K * scale, (y1 - y) * scale) for x, y in ring]
    half = len(xy) // 2
    s = simplify(xy[:half + 1], 0.35)[:-1] + simplify(xy[half:], 0.35)
    out, last = [], None
    for x, y in s:
        q = (round(x, 1), round(y, 1))
        if q != last:
            out.append(q)
            last = q
    paths[name] = "M" + "L".join(f"{a:g},{b:g}" for a, b in out) + "Z"

# Display name for city units: "NjA Nr. 5" -> "Nj.Ad. Nr. 5"
label = lambda n: n.replace("NjA ", "Nj.Ad. ", 1)
for u in units:
    u["name"] = label(u["name"])
paths = {label(k): v for k, v in paths.items()}

site = {"national": national, "regions": regions, "groups": GROUPS, "units": units,
        "map": {"w": W, "h": round(H), "paths": paths},
        "updated": "02/09/2025"}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(site, f, ensure_ascii=False, separators=(",", ":"))
print("site.json", round(os.path.getsize(OUT) / 1024, 1), "KB")
