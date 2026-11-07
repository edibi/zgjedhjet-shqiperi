import csv, json, os
from collections import defaultdict

"""Non-voters: nationally, by district and in Bashkia Tiranë (by unit and polling station).

Run:  python data/analiza/mosvotuesit.py   -> writes data/analiza/mosvotuesit_tirane_qv.csv
"""
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))


def dec(s):
    for a, b in (("&Euml;", "Ë"), ("&euml;", "ë"), ("&Ccedil;", "Ç"), ("&ccedil;", "ç")):
        s = s.replace(a, b)
    return s.strip()


def unit(s):
    s = dec(s).title().replace("Njësia Administrative", "Nj.Ad.").replace("Nr.", "Nr.")
    return s


ps = json.load(open(os.path.join(D, "kuvend-2025", "raw", "polling_station_party_results.json"), encoding="utf-8"))
S, PR = ps["data_main"][0]["data"], ps["data_main"][1]["data"]
reg = json.load(open(os.path.join(D, "kuvend-2025", "raw", "regional_party_results.json"), encoding="utf-8"))["data_main"][0]["data"]
pop = {r["Qarku"]: r for r in json.load(open(os.path.join(D, "popullsia", "popullsia_2025_qarqe.json"), encoding="utf-8"))["data"]}

votes = defaultdict(dict)
for r in PR:
    votes[r["v1"]][r["v3"]] = votes[r["v1"]].get(r["v3"], 0) + int(r["v5"])

q = defaultdict(lambda: {"list": 0, "voters": 0})
qv = []
for r in S:
    Q = dec(r["v1"]).upper()
    v = int(r["v10"]) + int(r["v11"])
    q[Q]["list"] += int(r["v6"]); q[Q]["voters"] += v
    qv.append({"qarku": Q, "bashkia": dec(r["v2"]), "unit": unit(r["v3"]), "qv": r["v5"], "list": int(r["v6"]),
               "voters": v, "valid": int(r["v10"]), "p": votes.get(r["v5"], {})})

dia_list = sum(int(r["v40"]) for r in reg)
dia_vot = sum(int(r["v10_1"]) + int(r["v11_1"]) for r in reg)
L = sum(x["list"] for x in q.values()); V = sum(x["voters"] for x in q.values())
R = sum(pop[k]["Shtetas_18plus"] for k in q)
print("=== NATIONAL")
print(f"in-country list {L:,}  voters {V:,}  turnout(list) {V/L:.1%}  list non-voters {L-V:,}")
print(f"diaspora list {dia_list:,}  voters {dia_vot:,}  turnout {dia_vot/dia_list:.1%}")
print(f"all list {L+dia_list:,} voters {V+dia_vot:,} turnout {(V+dia_vot)/(L+dia_list):.1%}  non-voters {L+dia_list-V-dia_vot:,}")
print(f"residents 18+ {R:,}  voters in Albania {V:,}  resident turnout {V/R:.1%}  resident non-voters {R-V:,}")
print(f"list minus residents (emigrants still on the domestic list, approx) {L-R:,}")
PSv = 855831
print(f"PS votes {PSv:,} = {PSv/(L+dia_list):.1%} of all registered, {PSv/R:.1%} of resident adults; resident non-voters / PS votes = {(R-V)/PSv:.2f}")
print("--- by qarku (resident turnout)")
for k, x in sorted(q.items(), key=lambda kv: kv[1]["voters"] / pop[kv[0]]["Shtetas_18plus"]):
    r_ = pop[k]["Shtetas_18plus"]
    print(f"{k:12} residents {r_:>8,} voters {x['voters']:>8,} resident turnout {x['voters']/r_:6.1%}  resident non-voters {r_-x['voters']:>8,}  list turnout {x['voters']/x['list']:.1%}")

# ---- Tirana municipality
kT = pop["TIRANË"]["Shtetas_18plus"] / q["TIRANË"]["list"]
T = [x for x in qv if x["bashkia"] == "Tiranë"]
FL = ("NISMA-SHB", "MUNDESIA", "BASHKE")
for x in T:
    x["res"] = x["list"] * kT
    x["nonv_list"] = x["list"] - x["voters"]
    x["nonv_res"] = x["res"] - x["voters"]
    x["sheshi"] = sum(x["p"].get(c, 0) for c in FL)
    x["pspsd"] = x["p"].get("PS", 0) + x["p"].get("PSD", 0)
    x["pd"] = x["p"].get("PD-ASHM", 0)
tl = sum(x["list"] for x in T); tv = sum(x["voters"] for x in T); tsh = sum(x["sheshi"] for x in T); tval = sum(x["valid"] for x in T)
print(f"\n=== TIRANA (Bashkia)  stations {len(T)}  k(residents/list, Tirana qark) {kT:.3f}")
print(f"list {tl:,} voters {tv:,} turnout {tv/tl:.1%}  list non-voters {tl-tv:,}  resident est {tl*kT:,.0f} resident non-voters {tl*kT-tv:,.0f}")
print(f"SHESHI share {tsh/tval:.1%}")

U = defaultdict(lambda: defaultdict(float))
for x in T:
    u = U[x["unit"]]
    for k in ("list", "voters", "valid", "nonv_list", "nonv_res", "sheshi", "pspsd", "pd"):
        u[k] += x[k]
    u["n"] += 1
print("--- units, by resident non-voters")
rows = []
for name, u in sorted(U.items(), key=lambda kv: -kv[1]["nonv_res"]):
    rows.append(name)
    print(f"{name:16} st {int(u['n']):3}  list {int(u['list']):>7,}  turnout {u['voters']/u['list']:5.1%}  non-voters(list) {int(u['nonv_list']):>7,}  (res) {int(u['nonv_res']):>7,}  share of city non-voters {u['nonv_list']/(tl-tv):5.1%}  SHESHI {u['sheshi']/u['valid']:5.1%}")

# station level: priority = large pool and above-average SHESHI share
avg = tsh / tval
for x in T:
    x["turnout"] = x["voters"] / x["list"] if x["list"] else 0
    x["sh_share"] = x["sheshi"] / x["valid"] if x["valid"] else 0
    x["score"] = x["nonv_list"] * (x["sh_share"] / avg)
top = sorted(T, key=lambda x: -x["score"])[:25]
print("--- top 25 stations: non-voters weighted by SHESHI affinity")
for x in top:
    print(f"{x['qv']}  {x['unit']:14} list {x['list']:>5}  turnout {x['turnout']:5.1%}  non-voters {x['nonv_list']:>5}  SHESHI {x['sh_share']:5.1%}")
by_unit = defaultdict(int)
for x in sorted(T, key=lambda x: -x["score"])[:100]:
    by_unit[x["unit"]] += 1
print("top-100 priority stations by unit:", dict(sorted(by_unit.items(), key=lambda kv: -kv[1])))
big = sorted(T, key=lambda x: -x["nonv_list"])
print("top 100 stations hold", f"{sum(x['nonv_list'] for x in big[:100]) / (tl - tv):.1%}", "of city non-voters;", len(T), "stations total")
gap = 136485
print(f"Tirana gap to PS+PSD {gap:,} = {gap/(tl*kT-tv):.1%} of resident non-voters, {gap/(tl-tv):.1%} of list non-voters")
with open(os.path.join(OUT, "mosvotuesit_tirane_qv.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["QV", "Njesia", "Zgjedhes_lista", "Votues", "Pjesemarrja", "Mosvotues_lista", "Mosvotues_rezidente_vleresim", "Sheshi_perqindje", "PS_PSD_perqindje", "Pikezimi"])
    for x in sorted(T, key=lambda x: -x["score"]):
        w.writerow([x["qv"], x["unit"], x["list"], x["voters"], f"{x['turnout']:.3f}", x["nonv_list"], round(x["nonv_res"]),
                    f"{x['sh_share']:.3f}", f"{x['pspsd']/x['valid'] if x['valid'] else 0:.3f}", round(x["score"])])
print("csv written")
