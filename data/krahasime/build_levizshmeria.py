"""Votes by party group and administrative unit for 2021, 2023 and 2025, all of Albania,
and the Pedersen volatility index between each pair of elections.

    python data/krahasime/build_levizshmeria.py [--out DIR]

Writes (default into data/krahasime/):
  levizshmeria_vota_2021_2023_2025.csv   Viti, Qarku, Bashkia, Njesia administrative, Grupi, Vota
  levizshmeria_pedersen.csv              Krahasimi, Niveli, Qarku, Bashkia, Njesia administrative,
                                         Pedersen, Nga subjektet e reja (one row per unit, municipality, district, Shqipëria)

Elections: 2021 = parliament (Kuvendi), 2023 = municipal council (Këshill bashkiak), 2025 = parliament,
votes cast inside the country only. Units use the 2025 names exactly as the Power BI model loads them
(before its 'Njësia Administrative' -> 'Nj.Ad.' display rename).

Party groups (the same in every year, so votes moving between them count as volatility):
  PS          PS
  PSD         PSD
  PD          2021: PD-AN (PD and allies) + LSI;  2023: BF (Bashkë Fitojmë) + PD;  2025: PD-ASHM
              LSI's successor (Partia e Lirisë) ran inside BF in 2023 and inside PD-ASHM in 2025, so it is merged in 2021.
  NISMA-SHB   2021 and 2023: NTH (Nisma Thurje);  2025: NISMA-SHB (Shqipëria Bëhet)
  MUNDESIA    2025 only
  BASHKE      2023 (Tiranë only) and 2025 (Lëvizja Bashkë)
  Te tjeret   every other list and independent candidate, as one bloc

Pedersen = 0.5 x sum over groups of |share(year 2) - share(year 1)|, in percentage points (0-100).
'Nga subjektet e reja' = the part of it from groups with no votes in that area in year 1.
"""
import csv, difflib, html, json, os, re, sys
from collections import defaultdict

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPS = ["PS", "PSD", "PD", "NISMA-SHB", "MUNDESIA", "BASHKE", "Te tjeret"]
G21 = {"PS": "PS", "PSD": "PSD", "PD-AN": "PD", "LSI": "PD", "NTH": "NISMA-SHB"}
G23 = {"PS": "PS", "PSD": "PSD", "BF": "PD", "PD": "PD", "NTH": "NISMA-SHB", "BASHKE": "BASHKE"}
G25 = {"PS": "PS", "PSD": "PSD", "PD-ASHM": "PD", "NISMA-SHB": "NISMA-SHB", "MUNDESIA": "MUNDESIA", "BASHKE": "BASHKE"}
PAIRS = [(2021, 2025), (2023, 2025), (2021, 2023)]

dec = lambda s: re.sub(r"\s+", " ", html.unescape(s)).strip()


def jload(*p):
    with open(os.path.join(DATA, *p), encoding="utf-8-sig") as f:
        t = f.read()
    return json.loads(t[t.index("{"):t.rindex("}") + 1])


def proper(s):
    """Power Query Text.Proper: first letter of each word upper, the rest lower."""
    return re.sub(r"[^\W\d_]+", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), s)


def norm(s):
    s = dec(s).casefold().replace("ë", "e").replace("ç", "c")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"^bashkia ", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"^qender .*$", "qender", s)
    s = re.sub(r"posht", "i poshtem", s)
    s = re.sub(r"sip", "i siperm", s)
    s = re.sub(r"^f memaliaj$", "memaliaj fshat", s)
    return re.sub(r"\s+", " ", s)


BASHKIA_ALIAS = {"ura vajgurore": "dimal", "rroskovec": "roskovec", "vau i dejes": "vau dejes"}


def bkey(name):
    n = norm(name)
    return BASHKIA_ALIAS.get(n, n)


def ukey(name):
    n = norm(name)
    m = re.search(r"nr (\d+)$", n)
    if m and "njesia" in n:
        return "nr " + m.group(1)
    return n


def match_unit(b, u):
    """2025 key for an older (municipality, unit) name: exact after normalising, else the closest name in that municipality."""
    k = (bkey(b), ukey(u))
    k = (k[0], UNIT_ALIAS.get(k, k[1]))
    if k in units:
        return k
    cands = [kk[1] for kk in units if kk[0] == k[0]]
    best = difflib.get_close_matches(k[1], cands, n=1, cutoff=0.6)
    if best:
        fuzzy.add((dec(b), dec(u), units[(k[0], best[0])][2]))
        return (k[0], best[0])
    missing.append((dec(b), dec(u)))
    return None


# Units KQZ later merged into a neighbour (checked against registered voters by year)
UNIT_ALIAS = {("diber", "fushe muhur"): "muhurr", ("kukes", "kolsh kukes"): "kolsh",
              ("mallakaster", "ngracan"): "ballsh",               # 2021 only; Ballsh grows by about that many voters in 2023
              ("mallakaster", "selite mallakaster"): "selite",
              ("kolonje", "barmash"): "leskovik",                 # 2021 Barmash = 2023 Qendër Leskovik, inside Leskovik in 2025
              ("kolonje", "qender leskovik"): "leskovik"}
fuzzy, missing = set(), []

# ---- 2025: the model's units (polling station file)
ps = jload("kuvend-2025", "raw", "polling_station_party_results.json")["data_main"]
units = {}          # (bkey, ukey) -> (Qarku, Bashkia, Njesia)
qv25 = {}
for r in ps[0]["data"]:
    q = dec(r["v1"]).upper()
    # exactly as the model loads them (Text.Proper only, spaces kept: "Berat ", "Qendër  - Bilisht")
    b, u = proper(html.unescape(r["v2"])), proper(html.unescape(r["v3"]))
    k = (bkey(b), ukey(u))
    assert units.setdefault(k, (q, b, u)) == (q, b, u), k
    qv25[r["v5"]] = k
votes = defaultdict(int)
for r in ps[1]["data"]:
    votes[(2025, qv25[r["v1"]], G25.get(r["v3"], "Te tjeret"))] += int(r["v5"])

# ---- 2023: municipal council by unit
tree = jload("vendore-2023", "raw", "json_strukture9.js")
sj = open(os.path.join(DATA, "vendore-2023", "raw", "json_subjekte8.js"), encoding="utf-8").read()
council = {(o["v1"], o["v2"]): o["v3"] for o in (json.loads(m) for m in re.findall(r'\{"v1":"\d+",[^{}]*\}', sj)) if "v6" in o}
u23 = {}
for q in tree["data"]:
    for b in q.get("child", []):
        bid = b["v1"][2:]
        for n in b["child"]:
            k = match_unit(b["bashkia"], n["njesi"])
            if k:
                u23[n["v1"][2:]] = (bid, k)
n23 = jload("vendore-2023", "raw", "json_all_summary_1_njesi.txt")["data_main"][1]["data"]
for r in n23:
    if r["v1"] in u23:
        bid, k = u23[r["v1"]]
        code = council.get((bid, r["v2"]), "")
        if True:
            votes[(2023, k, G23.get(code, "Te tjeret"))] += int(r["v3"])

# ---- 2021: parliament by polling station -> unit
tree = jload("kuvend-2021", "raw", "json_strukture.txt")
qv21 = {}
for q in tree["data"][1:]:
    for b in q["child"]:
        for n in b["child"]:
            k = match_unit(b["bashkia"], n["njesi"])
            if not k:
                continue
            for s in n["child"]:
                assert qv21.setdefault(s["qv"], k) == k, s["qv"]
assert not missing, missing
for f in sorted(fuzzy):
    print("matched by closest name:", f)


# where the parent code is shared by two units: the unit whose KQZ unit total is short by exactly that station's votes
ORPHAN21 = {"0781": ("mirdite", "fan"), "1172": ("diber", "arras"), "1264": ("kruje", "cudhi"),
            "2391": ("elbasan", "bradashesh"), "2895": ("lushnje", "allkaj"), "4308": ("gjirokaster", "lunxheri"),
            "4206": ("permet", "qender")}   # Suke already matches its KQZ total without it


def unit21(code):
    """29 stations in the 2021 results (6,606 votes) are missing from KQZ's structure file. Split stations
    carry their parent's code plus a digit (3268 -> 32681), so use the parent's unit, or a split sibling's."""
    if code in qv21:
        return qv21[code]
    if code in ORPHAN21:
        return ORPHAN21[code]
    for c in (code[:-1], code[:-2]):
        if c in qv21:
            return qv21[c]
    sib = [k for c, k in qv21.items() if c.startswith(code) or c[:-1] == code[:-1]]
    assert len(set(sib)) == 1, (code, set(sib))
    return sib[0]


for r in jload("kuvend-2021", "raw", "json_qv.txt")["data"]:
    k = unit21(r["v1"])
    if r["v1"] not in qv21 and r["v2"] == "1":
        print("2021 station", r["v1"], "->", units[k][1], "/", units[k][2])
    votes[(2021, k, G21.get(r["v3"], "Te tjeret"))] += int(r["v5"])
assert not missing, missing

# ---- checks against KQZ's own totals
tot = lambda y: sum(v for (yy, _, _), v in votes.items() if yy == y)
nat21 = sum(int(r["v5"]) for r in jload("kuvend-2021", "raw", "json_all.txt")["data"])
assert tot(2021) == nat21, (tot(2021), nat21)
# KQZ's 2023 unit file is 1,386 votes (0.1%) short of its municipality file in every municipality,
# so the unit total is the check here
nat23 = sum(int(r["v3"]) for r in n23)
assert tot(2023) == nat23, (tot(2023), nat23)
print("votes 2021", tot(2021), "2023", tot(2023), "2025", tot(2025), "units", len(units))
for y in (2021, 2023):
    lost = [units[k] for k in units if not any(votes.get((y, k, g)) for g in GROUPS)]
    if lost:
        print(f"units with no {y} votes:", lost)


# ---- Pedersen at every level
def pedersen(a, b):
    ta, tb = sum(a.values()), sum(b.values())
    if not ta or not tb:
        return None, None
    d = [(abs(b.get(g, 0) / tb - a.get(g, 0) / ta), a.get(g, 0) == 0) for g in GROUPS]
    return round(50 * sum(x for x, _ in d), 2), round(50 * sum(x for x, new in d if new), 2)


levels = {"Njësia": lambda u: u, "Bashkia": lambda u: (u[0], u[1], ""), "Qarku": lambda u: (u[0], "", ""), "Shqipëria": lambda u: ("", "", "")}
agg = defaultdict(lambda: defaultdict(int))
for (y, k, g), v in votes.items():
    for lv, f in levels.items():
        agg[(lv, f(units[k]), y)][g] += v
ped = []
for y1, y2 in PAIRS:
    for lv in levels:
        for place in sorted({p for (l, p, _) in agg if l == lv}):
            p, n = pedersen(agg[(lv, place, y1)], agg[(lv, place, y2)])
            if p is not None:
                ped.append([f"{y1}-{y2}", lv, *place, p, n])

out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(DATA, "krahasime")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "levizshmeria_vota_2021_2023_2025.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Viti", "Qarku", "Bashkia", "Njesia administrative", "Grupi", "Vota"])
    for (y, k, g) in sorted(votes, key=lambda x: (x[0], units[x[1]], GROUPS.index(x[2]))):
        if votes[(y, k, g)]:
            w.writerow([y, *units[k], g, votes[(y, k, g)]])
with open(os.path.join(out, "levizshmeria_pedersen.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Krahasimi", "Niveli", "Qarku", "Bashkia", "Njesia administrative", "Pedersen", "Nga subjektet e reja"])
    w.writerows(ped)
for r in ped:
    if r[1] in ("Shqipëria",) or r[3] in ("Tiranë", "Vlorë") and r[1] == "Bashkia":
        print(r)
