"""HUD do GoW1 (Fase 7, T94): converte o filme FLP_HUD (R_PERM.WAD) e a malha HUD_0 para o player da DLL (KratosHud.cpp).

Uso: python -I tools/build_hud.py <pasta com FLP_HUD.json e HUD_0.json (gowb)> <saída> [--preview frame:alvo=quadro,...]
Saída: hud.json (timelines, quadros-chave, triângulos com UV, transformações, cores, fontes, rótulos e scripts) e as
texturas TXR_*.png. Formato do FLP: docs/formats/gow-flp.md (leitura do visualizador do gowb, BrowserWadFlp.js).
Scripts: ActionScript 1 (opcodes SWF) como o gowb os descompila; viram [opcode, argumento] com os saltos resolvidos.
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

# índice da timeline no hud.json: 0 = raiz (Data8), 1.. = Datas7, depois os Sub1 dos Datas6
TYPE_MESH, TYPE_FONT, TYPE_STATIC, TYPE_DYNAMIC, TYPE_D6, TYPE_D7, TYPE_ROOT = 1, 3, 4, 5, 6, 7, 8


def strips(packet: dict) -> list[list[float]]:
    """Tiras de triângulos do PS2 (Skip = vértice que não fecha triângulo) → triângulos [x, y, u, v] × 3."""
    t, uv = packet["Trias"], packet["Uvs"]
    xs, ys, skip = t["X"], t["Y"], t["Skip"]
    us, vs = uv["U"] or [0.0] * len(xs), uv["V"] or [0.0] * len(xs)
    tris = []
    for k in range(2, len(xs)):
        if skip[k]:
            continue
        idx = (k - 2, k - 1, k) if k % 2 == 0 else (k - 1, k - 2, k)
        tris.append([c for i in idx for c in (xs[i], ys[i], us[i], vs[i])])
    return tris


def compile_script(lines: list[str]) -> list[list]:
    """Linhas descompiladas do gowb → [[opcode, argumento], ...]; rótulos $nome viram índices de instrução."""
    ops, labels = [], {}
    for raw in lines:
        code = raw.split("//")[0].strip()
        if not code:
            continue
        if code.startswith("$"):
            labels[code.split()[0]] = len(ops)
            continue
        m = re.match(r"([0-9A-F]{2}):\s*(.*)$", code)
        if not m:
            continue
        op, rest = int(m.group(1), 16), m.group(2).strip()
        strs = re.findall(r'"((?:[^"\\]|\\.)*)"', rest)
        if op in (0x99, 0x9D):
            arg = rest.split()[0]
        elif op in (0x81, 0x9F):
            arg = int(rest.split()[0]) if rest else 0
        elif strs:
            arg = strs if op in (0x96, 0x83) else strs[0]
        else:
            arg = None
        ops.append([op, arg])
    for o in ops:
        if o[0] in (0x99, 0x9D):
            o[1] = labels.get(o[1], len(ops))
    return ops


def timeline(tl: dict, ids: dict) -> dict:
    els = []
    for el in tl["ElementsAnimation"]:
        kfs = []
        for kf in el["KeyFrames"]:
            h = kf["ElementHandler"]
            kfs.append([kf["WhenThisFrameEnds"], h["TypeArrayId"], h["IdInThatTypeArray"], kf["TransformationId"],
                        kf["ColorId"], kf["Name"]])
        els.append(kfs)
    labels, scripts = {}, {}
    for fl in tl.get("FrameScriptLables") or []:
        f = fl["TriggerFrameNumber"]
        if fl["LabelName"]:
            labels[fl["LabelName"]] = f
        for sub in fl.get("Subs") or []:
            scripts.setdefault(str(f), []).append(compile_script(sub["Script"]["Decompiled"]))
    return {"frames": tl["TotalFramesCount"], "elements": els, "labels": labels, "scripts": scripts}


def build(src: Path, out: Path) -> dict:
    root = json.loads((src / "FLP_HUD.json").read_text())["Data"]
    flp, mesh = root["FLP"], json.loads((src / "HUD_0.json").read_text())["Data"]
    out.mkdir(parents=True, exist_ok=True)
    tex_names = sorted(n for n, t in root["Textures"].items() if t.get("Images"))
    for n in tex_names:
        (out / f"{n}.png").write_bytes(base64.b64decode(root["Textures"][n]["Images"][0]["Image"]))
    tex_index = {n: i for i, n in enumerate(tex_names)}
    parts = []
    for p in mesh["Parts"]:
        objs = []
        for g in p["Groups"]:
            for o in g["Objects"]:
                tris = [t for pk in o["Packets"] for q in pk for t in strips(q)]
                objs.append(tris)
        parts.append(objs)
    meshrefs = []
    for r in flp["MeshPartReferences"]:
        mats = [[tex_index.get(m["TextureName"], -1), m["Color"]] for m in r.get("Materials") or []]
        meshrefs.append({"part": r["MeshPartIndex"], "mats": mats})
    tls = [timeline(flp["Data8"], {})]
    tls += [timeline(d, {}) for d in flp["Datas7"]]
    d6 = []
    for d in flp["Datas6"]:
        d6.append(len(tls))
        tls.append(timeline(d["Sub1"], {}))
    tr = [[t["OffsetX"], t["OffsetY"], *t["Matrix"]] for t in flp["Transformations"]]
    col = [c["Color"] for c in flp["BlendColors"]]
    fonts = [{"glyphs": [g["MeshPartIndex"] if "MeshPartIndex" in g else -1 for g in f["MeshesRefs"]],
              "glyphRefs": [len(meshrefs) + 0] * 0, "widths": f["SymbolWidths"], "map": f["CharNumberToSymbolIdMap"],
              "scale": f.get("Float020", 1.0)} for f in flp["Fonts"]]
    # glifos das fontes: meshrefs próprios (data2 dentro da fonte) anexados à lista
    for fi, f in enumerate(flp["Fonts"]):
        refs = []
        for g in f["MeshesRefs"]:
            refs.append(len(meshrefs))
            meshrefs.append({"part": g["MeshPartIndex"],
                             "mats": [[tex_index.get(m["TextureName"], -1), m["Color"]] for m in g.get("Materials") or []]})
        fonts[fi]["glyphs"] = refs
    statics = []
    for s in flp["StaticLabels"]:
        cmds = []
        for c in s["RenderCommandsList"]:
            cmds.append({"flags": c["Flags"], "font": flp["GlobalHandlersIndexes"][c["FontHandler"]]["IdInThatTypeArray"]
                         if c["Flags"] & 8 else -1, "scale": c["FontScale"], "color": c["BlendColor"],
                         "x": c["OffsetX"], "y": c["OffsetY"], "glyphs": [[g["GlyphId"], g["Width"]] for g in c["Glyphs"]]})
        t = s["Transformation"]
        statics.append({"tr": [t["OffsetX"], t["OffsetY"], *t["Matrix"]], "cmds": cmds})
    dynamics = [{k: d[k] for k in d if k != "FontHandler"} | {"font": d["FontHandler"]["IdInThatTypeArray"]}
                for d in flp["DynamicLabels"]]
    doc = {"textures": tex_names, "parts": parts, "meshrefs": meshrefs, "timelines": tls, "data6": d6,
           "transforms": tr, "colors": col, "fonts": fonts, "statics": statics, "dynamics": dynamics}
    (out / "hud.json").write_text(json.dumps(doc, separators=(",", ":")))
    return doc


def keyframe(kfs: list, frame: int) -> list | None:
    """quadro-chave vigente: o 1º campo é o quadro em que ele começa (vale até o próximo); tipo 0 = vazio. Pela raiz:
    MainMeter em (0), vazio em (2) e o rótulo "HUD" no quadro 1"""
    cur = None
    for k in kfs:
        if k[0] > frame:
            break
        cur = k
    return cur if cur is not None and cur[1] != 0 else None


def preview(doc: dict, out: Path, frames: dict[str, int], dst: Path) -> None:
    """Prévia sem scripts: raiz no quadro dado; sprites no quadro de `frames` (nome da instância → quadro)."""
    from PIL import Image, ImageDraw
    W, H = 900, 760
    img = Image.new("RGBA", (W, H), (40, 40, 48, 255))
    texs = [Image.open(out / f"{n}.png").convert("RGBA") for n in doc["textures"]]

    def mul(a, b):  # (ox, oy, m00, m01, m10, m11): ponto' = (x*m00 + y*m10 + ox, x*m01 + y*m11 + oy)
        ox, oy, a0, a1, a2, a3 = a
        bx, by, b0, b1, b2, b3 = b
        return [bx * a0 + by * a2 + ox, bx * a1 + by * a3 + oy, b0 * a0 + b1 * a2, b0 * a1 + b1 * a3,
                b2 * a0 + b3 * a2, b2 * a1 + b3 * a3]

    def draw_ref(ri, t, color):
        r = doc["meshrefs"][ri]
        for oi, tris in enumerate(doc["parts"][r["part"]]):
            tex, c = r["mats"][oi] if oi < len(r["mats"]) else (-1, 0xFFFFFFFF)
            tint = [((c >> (8 * i)) & 0xFF) / 128.0 * color[i] for i in range(4)]  # 0x80 = 1,0 no PS2
            for tri in tris:
                pts = [(tri[i] * t[2] + tri[i + 1] * t[4] + t[0], tri[i] * t[3] + tri[i + 1] * t[5] + t[1]) for i in (0, 4, 8)]
                mask = Image.new("L", (W, H), 0)
                ImageDraw.Draw(mask).polygon(pts, fill=255)
                if tex >= 0:
                    tx = texs[tex]
                    uv = [(tri[i + 2] * tx.width, tri[i + 3] * tx.height) for i in (0, 4, 8)]
                    # afim tela → textura (resolve 3 pontos)
                    import numpy as np
                    A = np.array([[p[0], p[1], 1] for p in pts])
                    try:
                        cx = np.linalg.solve(A, [q[0] for q in uv])
                        cy = np.linalg.solve(A, [q[1] for q in uv])
                    except np.linalg.LinAlgError:
                        continue
                    layer = tx.transform((W, H), Image.AFFINE, (*cx, *cy), resample=Image.BILINEAR)
                else:
                    layer = Image.new("RGBA", (W, H), (255, 255, 255, 255))
                r_, g_, b_, a_ = layer.split()
                r_, g_, b_, a_ = [ch.point(lambda v, k=k: max(0, min(255, int(v * tint[k])))) for k, ch in enumerate((r_, g_, b_, a_))]
                layer = Image.merge("RGBA", (r_, g_, b_, a_))
                a2 = Image.composite(layer.split()[3], Image.new("L", (W, H), 0), mask)
                layer.putalpha(a2)
                img.alpha_composite(layer)

    def draw_tl(ti, frame, t, color, name, depth=0):
        tl = doc["timelines"][ti]
        for kfs in tl["elements"]:
            kf = keyframe(kfs, frame)
            if kf is None:
                continue
            _, typ, oid, tri, ci, nm = kf
            nt = mul(t, doc["transforms"][tri]) if tri >= 0 else t
            nc = color
            if ci >= 0:
                cc = doc["colors"][ci]
                nc = [color[i] * cc[i] / 256.0 for i in range(4)] if isinstance(cc, list) else color
            if typ == TYPE_MESH:
                draw_ref(oid, nt, nc)
            elif typ in (TYPE_D6, TYPE_D7) and depth < 12:
                sub = doc["data6"][oid] if typ == TYPE_D6 else 1 + oid
                draw_tl(sub, frames.get(nm, 0), nt, nc, nm, depth + 1)

    draw_tl(0, frames.get("", 1), [0, 0, 1, 0, 0, 1], [1.0, 1.0, 1.0, 1.0], "")
    img.save(dst)


if __name__ == "__main__":
    doc = build(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{len(doc['timelines'])} timelines, {len(doc['meshrefs'])} malhas, {len(doc['textures'])} texturas")
    if "--preview" in sys.argv:
        spec = sys.argv[sys.argv.index("--preview") + 1]
        fr = {k: int(v) for k, v in (p.split("=") for p in spec.split(","))} if spec else {}
        preview(doc, Path(sys.argv[2]), fr, Path(sys.argv[2]) / "preview.png")
