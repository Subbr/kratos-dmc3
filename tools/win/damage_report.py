"""Resumo do log de acerto (KratosConfig logDamage): por motion, quantas vezes tocou e quantos danos deu.
python -I tools/win/damage_report.py <kratos.txt>"""
import collections
import sys

plays, hits, sides = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
dists: list[float] = []
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    w = line.split()
    if line.startswith("play motion"):
        plays[w[2]] += 1
    elif line.startswith("dmg motion"):
        hits[w[2]] += 1
        sides[w[2]][w[-1]] += 1
        if "dist" in w:
            dists.append(float(w[w.index("dist") + 1]))
for m in sorted(set(plays) | set(hits), key=lambda k: tuple(map(int, k.split("/")))):
    if m.startswith("3/") or hits[m]:
        print(f"{m:6} tocou {plays[m]:3}  danos {hits[m]:3}  {dict(sides[m])}")
print("total danos", sum(hits.values()))
if dists:  # distância jogador -> inimigo atingido (XZ): mostra o alcance real dos golpes
    dists.sort()
    print("alcance: mediana %.0f, p90 %.0f, máx %.0f" % (dists[len(dists) // 2], dists[int(len(dists) * 0.9)], dists[-1]))
