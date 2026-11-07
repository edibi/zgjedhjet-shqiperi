"""Build the 2023 local results and the 2023-2025 comparison for one municipality.

    python data/krahasime/build_krahasime.py Vlorë [--out DIR]

Writes (default into the project's data folders):
  vendore-2023/normalized/<slug>_vendore_2023.csv              mayor and council, by unit and polling station
  vendore-2023/normalized/<slug>_vendore_2023_permbledhje.csv  voters and ballots, by unit and polling station
  krahasime/krahasimi_<slug>_2023_2025.csv                     votes by party group, by unit, 2023 vs 2025
  krahasime/pjesemarrja_<slug>_2023_2025.csv                   voters and registered voters, by unit
2023 = municipal council (Këshill bashkiak). 2025 = parliament (Kuvendi), inside the country.
"""
import csv, html, json, os, re, sys
from collections import defaultdict

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW23 = os.path.join(DATA, "vendore-2023", "raw")
RAW25 = os.path.join(DATA, "kuvend-2025", "raw")
SLUG = {"Tiranë": "tirane", "Vlorë": "vlore"}
FILES = {"Kryetar bashkie": ("json_all_summary_0_njesi_lh.txt", "json_all_summary_0_qv_lh.txt"),
         "Këshill bashkiak": ("json_all_summary_1_njesi.txt", "json_all_summary_1_qv.txt")}

dec = lambda s: html.unescape(s).strip()


def unit_key(name):
    n = dec(name).casefold().replace("njësia administrative", "nja")
    return re.sub(r"\s+", " ", n).strip()


def unit_label(name):
    """Same naming as the Power BI model before its display rename: 'NjA Nr. 5', 'Qendër - Vlore'."""
    n = dec(name).title().replace("Njësia Administrative", "NjA")
    return n


def load(f):
    return json.load(open(os.path.join(RAW23, f), encoding="utf-8"))["data_main"]


def build(bashkia, out_norm, out_kr):
    st = open(os.path.join(RAW23, "json_strukture9.js"), encoding="utf-8").read()
    tree = json.loads(st[st.index("{"):st.rindex("}") + 1])
    node = next(b for q in tree["data"] for b in q["child"] if dec(b["bashkia"]) == bashkia)
    bid = node["v1"][2:]
    units = {n["v1"][2:]: n for n in node["child"]}
    qv_unit = {q["v1"][2:]: (uid, q["qv"], int(q["v3"])) for uid, n in units.items() for q in n["child"]}

    sj = open(os.path.join(RAW23, "json_subjekte8.js"), encoding="utf-8").read()
    objs = [json.loads(m) for m in re.findall(r'\{"v1":"' + bid + r'",[^{}]*\}', sj)]
    council = {o["v2"]: (o["v3"], dec(o["v4"])) for o in objs if "v6" in o}
    mayor = {o["v2"]: (o["v5"], dec(o["v4"]), dec(o["v3"])) for o in objs if "v6" not in o and "v3" in o and "v5" in o}

    # 2025 unit names in this municipality (as the model shows them)
    ps = json.load(open(os.path.join(RAW25, "polling_station_party_results.json"), encoding="utf-8"))
    S25, P25 = ps["data_main"][0]["data"], ps["data_main"][1]["data"]
    rows25 = [r for r in S25 if dec(r["v2"]) == bashkia]
    names25 = {unit_key(r["v3"]): unit_label(r["v3"]) for r in rows25}
    label = {}
    for uid, n in units.items():
        k = unit_key(n["njesi"])
        assert k in names25, f"2023 unit without 2025 match: {n['njesi']}"
        label[uid] = names25[k]

    raw_name = {uid: dec(n["njesi"]) for uid, n in units.items()}   # KQZ's own unit names, as in the 2023 files
    res, summ = [], []
    for gara, (fu, fq) in FILES.items():
        subj = mayor if gara == "Kryetar bashkie" else council
        fb = fu.replace("_njesi", "_bashki")
        for r in load(fb)[0]["data"]:
            if r["v1"] == bid:
                summ.append([gara, "bashkia", "", "", r["v8"], r["v9"], r["v10"], r["v11"], r["v13"], r["v12"]])
        for level, f in (("njesia", fu), ("qv", fq)):
            blocks = load(f)
            ids = units if level == "njesia" else qv_unit
            for r in blocks[0]["data"]:
                if r["v1"] in ids:
                    u = r["v1"] if level == "njesia" else qv_unit[r["v1"]][0]
                    q = "" if level == "njesia" else qv_unit[r["v1"]][1]
                    summ.append([gara, level, raw_name[u], q, r["v8"], r["v9"], r["v10"], r["v11"], r["v13"], r["v12"]])
            for r in blocks[1]["data"]:
                if r["v1"] in ids and r["v2"] in subj:
                    u = r["v1"] if level == "njesia" else qv_unit[r["v1"]][0]
                    q = "" if level == "njesia" else qv_unit[r["v1"]][1]
                    s = subj[r["v2"]]
                    res.append([2023, "Vendore", gara, level, bashkia, raw_name[u], q, s[0], s[1], s[2] if len(s) > 2 else "", int(r["v3"]), ""])
    to_label = {raw_name[u]: label[u] for u in units}

    slug = SLUG[bashkia]
    os.makedirs(out_norm, exist_ok=True); os.makedirs(out_kr, exist_ok=True)
    with open(os.path.join(out_norm, f"{slug}_vendore_2023.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["Viti", "Zgjedhja", "Gara", "Niveli", "Bashkia", "Njesia administrative", "Qender Votimi", "Kodi", "Subjekti", "Kandidati", "Vota", "Mandate"]); w.writerows(res)
    with open(os.path.join(out_norm, f"{slug}_vendore_2023_permbledhje.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["Gara", "Niveli", "Njesia administrative", "Qender Votimi", "Votues", "Gra votuese", "Vota te vlefshme", "Vota te pavlefshme", "Fleta te kontestuara", "QV"]); w.writerows(summ)

    # ---- comparison: 2023 council vs 2025 parliament, by party group
    G23 = {"PS": ("PS + PSD", "PS"), "PSD": ("PS + PSD", "PSD"), "BF": ("PD-ASHM", "PD-ASHM"), "PD": ("PD-ASHM", "PD-ASHM"),
           "NTH": ("NISMA-SHB", "NISMA-SHB"), "BASHKE": ("BASHKE", "BASHKE")}
    G25 = {"PS": ("PS + PSD", "PS"), "PSD": ("PS + PSD", "PSD"), "PD-ASHM": ("PD-ASHM", "PD-ASHM"),
           "NISMA-SHB": ("NISMA-SHB", "NISMA-SHB"), "BASHKE": ("BASHKE", "BASHKE"), "MUNDESIA": ("MUNDESIA", "MUNDESIA")}
    kr = defaultdict(int)
    for r in res:
        if r[2] == "Këshill bashkiak" and r[3] == "njesia":
            g = G23.get(r[7], ("Te tjeret", "Te tjeret"))
            kr[(2023, to_label[r[5]]) + g] += r[10]
    unit25 = {r["v5"]: names25[unit_key(r["v3"])] for r in rows25}
    for r in P25:
        if r["v1"] in unit25:
            g = G25.get(r["v3"], ("Te tjeret", "Te tjeret"))
            kr[(2025, unit25[r["v1"]]) + g] += int(r["v5"])
    with open(os.path.join(out_kr, f"krahasimi_{slug}_2023_2025.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["Viti", "Njesia administrative", "Grupi", "Grupi i detajuar", "Vota"])
        for k in sorted(kr):
            if kr[k]:
                w.writerow(list(k) + [kr[k]])

    pj = defaultdict(lambda: [0, 0])
    for r in summ:
        if r[0] == "Këshill bashkiak" and r[1] == "njesia":
            pj[(2023, to_label[r[2]])][0] += int(r[6]) + int(r[7])
    for uid, n in units.items():
        pj[(2023, label[uid])][1] += int(n["v3"])
    for r in rows25:
        u = names25[unit_key(r["v3"])]
        pj[(2025, u)][0] += int(r["v10"]) + int(r["v11"])
        pj[(2025, u)][1] += int(r["v6"])
    with open(os.path.join(out_kr, f"pjesemarrja_{slug}_2023_2025.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["Viti", "Njesia administrative", "Votues", "Zgjedhes"])
        for k in sorted(pj):
            w.writerow(list(k) + pj[k])
    return len(units), len(res)


if __name__ == "__main__":
    b = sys.argv[1]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    n = build(b, out or os.path.join(DATA, "vendore-2023", "normalized"), out or os.path.join(DATA, "krahasime"))
    print(b, "units", n[0], "result rows", n[1])
