"""Vlorë municipality: unit boundaries from OpenStreetMap -> TopoJSON + unit centres.

    python data/gjeografi/build_vlore_map.py

Data © OpenStreetMap contributors, ODbL 1.0. Writes:
  gjeografi/vlore_njesite_administrative.topojson   one geometry per unit, id = unit name as in the model
  gjeografi/adresat_njesia_administrative.csv       adds/refreshes the Vlorë rows (Bashkia column)
"""
import csv, json, math, os, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REL = {1255534: "Vlorë", 1255549: "Novoselë", 1255538: "Orikum", 1255522: "Qendër - Vlore", 1255525: "Shushicë"}
TOL = 0.0002  # degrees, ~20 m


def fetch():
    q = "[out:json][timeout:90];rel(id:%s);out geom;" % ",".join(map(str, REL))
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(),
                                 headers={"User-Agent": "zgjedhjet-shqiperi-data-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def rings(rel):
    segs = [[(p["lon"], p["lat"]) for p in m["geometry"]] for m in rel["members"]
            if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
    out = []
    while segs:
        ring = segs.pop(0)
        while ring[0] != ring[-1]:
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]; segs.pop(i); break
                if s[-1] == ring[-1]:
                    ring += s[::-1][1:]; segs.pop(i); break
            else:
                raise ValueError(f"open ring in {rel['tags'].get('name')}")
        out.append(ring)
    return out


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


def close_simplify(r):
    h = len(r) // 2
    s = simplify(r[:h + 1], TOL)[:-1] + simplify(r[h:], TOL)
    s = [(round(x, 5), round(y, 5)) for x, y in s]
    if s[0] != s[-1]:
        s.append(s[0])
    return s


def area_centroid(r):
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:]):
        c = x1 * y2 - x2 * y1
        a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    a /= 2
    return abs(a), cx / (6 * a), cy / (6 * a)


data = fetch()
arcs, geoms, centres = [], [], {}
for rel in data["elements"]:
    name = REL[rel["id"]]
    rs = [close_simplify(r) for r in rings(rel)]
    rs = [r for r in rs if len(r) >= 4]
    ids = []
    for r in rs:
        arcs.append([list(p) for p in r]); ids.append(len(arcs) - 1)
    if len(ids) == 1:
        geoms.append({"type": "Polygon", "arcs": [[ids[0]]], "id": name, "properties": {"name": name}})
    else:
        geoms.append({"type": "MultiPolygon", "arcs": [[[i]] for i in ids], "id": name, "properties": {"name": name}})
    big = max(rs, key=lambda r: area_centroid(r)[0])
    _, cx, cy = area_centroid(big)
    centres[name] = (round(cx, 5), round(cy, 5))
    print(f"{name:16} rings {len(rs)}  points {sum(len(r) for r in rs)}  centre {centres[name]}")
assert set(centres) == set(REL.values())

topo = {"type": "Topology", "objects": {"njesite": {"type": "GeometryCollection", "geometries": geoms}}, "arcs": arcs}
out = os.path.join(HERE, "vlore_njesite_administrative.topojson")
json.dump(topo, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("topojson KB", round(os.path.getsize(out) / 1024, 1))

# centres file: add a Bashkia column, keep Tirana rows, refresh Vlorë rows
p = os.path.join(HERE, "adresat_njesia_administrative.csv")
rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
keep = [r for r in rows if r.get("Bashkia", "Tiranë") == "Tiranë"]
for r in keep:
    r["Bashkia"] = "Tiranë"
for n, (x, y) in sorted(centres.items()):
    keep.append({"Njesia administrative": n, "Longitude": x, "Latitude": y, "Bashkia": "Vlorë"})
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Njesia administrative", "Longitude", "Latitude", "Bashkia"])
    w.writeheader(); w.writerows(keep)
print("centres rows", len(keep))
