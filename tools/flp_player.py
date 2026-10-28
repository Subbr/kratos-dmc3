"""Player de referência do FLP do GoW1 (T94): lista de exibição + ActionScript 1, sobre o hud.json de build_hud.py.

Uso: python -I tools/flp_player.py <pasta do hud.json> <saída.png> [var=valor ...] [--ticks N] [--call Rótulo]
Serve para validar a semântica fora do jogo; a DLL (KratosHud.cpp) implementa o mesmo. Regras (docs/formats/gow-flp.md):
- quadro-chave: começa no quadro dado e vale até o próximo; tipo 0 = vazio; objeto novo = instância nova (quadro 0)
- GotoFrame (0x81) e GotoLabel (0x8C) vão e param; Play (0x06) volta a tocar; GotoFrame2 (0x9F) usa quadro 1-based
- variáveis por instância; "/:x" e "_level0/:x" = raiz; "a/b:x" = da instância a/b; SetTarget muda o alvo
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

T0 = time.time()


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def fmt(v):
    if isinstance(v, float):
        return str(int(v)) if v == int(v) else repr(v)
    return v


class Inst:
    def __init__(self, player, tl: int, name: str, parent):
        self.p, self.tl, self.name, self.parent = player, tl, name, parent
        self.frame, self.playing, self.vars = 0, True, {}
        self.children: dict[int, tuple[tuple, Inst | None]] = {}  # elemento → (objeto, instância)
        self.entered = False

    @property
    def data(self):
        return self.p.doc["timelines"][self.tl]

    def child(self, name: str):
        for _, (obj, c) in self.children.items():
            if c is not None and c.name == name:
                return c
        return None

    def sync(self):
        """atualiza a lista de exibição no quadro atual; instâncias novas rodam o quadro 0"""
        for ei, kfs in enumerate(self.data["elements"]):
            kf = self.p.keyframe(kfs, self.frame)
            if kf is None:
                self.children.pop(ei, None)
                continue
            obj = (kf[1], kf[2], kf[5])
            prev = self.children.get(ei)
            if prev and prev[0] == obj:
                continue
            inst = None
            if kf[1] in (6, 7):
                sub = self.p.doc["data6"][kf[2]] if kf[1] == 6 else 1 + kf[2]
                inst = Inst(self.p, sub, kf[5], self)
            self.children[ei] = (obj, inst)
            if inst:
                inst.enter()

    def enter(self):
        self.sync()
        self.run_frame(self.frame)

    def run_frame(self, f: int):
        for code in self.data["scripts"].get(str(f), []):
            self.p.run(code, self)

    def goto(self, f: int, play: bool | None = None):
        n = self.data["frames"]
        f = max(0, min(n - 1, f))
        self.frame = f
        if play is not None:
            self.playing = play
        self.sync()
        self.run_frame(f)

    def tick(self):
        if self.playing and self.data["frames"] > 1:
            nf = self.frame + 1
            if nf >= self.data["frames"]:
                nf = 0
            self.frame = nf
            self.sync()
            self.run_frame(nf)
        for _, (obj, c) in list(self.children.items()):
            if c:
                c.tick()


class Player:
    def __init__(self, doc: dict):
        self.doc = doc
        self.root = Inst(self, 0, "", None)
        self.log = []

    @staticmethod
    def keyframe(kfs, frame):
        """quadro-chave vigente: o 1º campo é o quadro em que ele começa (vale até o próximo); tipo 0 = vazio"""
        cur = None
        for k in kfs:
            if k[0] > frame:
                break
            cur = k
        return cur if cur is not None and cur[1] != 0 else None

    # caminhos: "/a/b" absoluto, "a/b" relativo, "_level0/a", "" = alvo original, ".." = pai
    def resolve(self, path: str, base: Inst) -> Inst | None:
        if path in ("", "/"):
            return self.root if path == "/" else base
        cur = base
        low = path.lower()
        if low.startswith("_level0"):
            cur, path = self.root, path[7:]
        if path.startswith("/"):
            cur, path = self.root, path[1:]
        for part in [p for p in path.split("/") if p]:
            if part == "..":
                cur = cur.parent or cur
            else:
                nxt = cur.child(part)
                if nxt is None:
                    return None
                cur = nxt
        return cur

    def split_var(self, name: str, base: Inst):
        if ":" in name:
            path, var = name.rsplit(":", 1)
            return self.resolve(path, base) if path else base, var
        return base, name

    def get(self, name: str, base: Inst):
        inst, var = self.split_var(name, base)
        # o jogo começa com todos os eventos em -1 (nenhum); vazio seria lido como evento 0 (abre menus)
        default = "-1" if var.endswith("_Event") else ""
        if inst and var in inst.vars:
            return inst.vars[var]
        # sem caminho e sem a variável no alvo: a da raiz (as do jogo, PS2_*, ficam lá; SetHealthMeter lê
        # PS2_HealthMeter_Value com o alvo em /MainMeter/HealthMeter)
        if ":" not in name and var in self.root.vars:
            return self.root.vars[var]
        return default

    def set(self, name: str, value, base: Inst):
        inst, var = self.split_var(name, base)
        if inst:
            inst.vars[var] = value

    def call(self, name: str, base: Inst):
        inst, lab = self.split_var(name, base) if ":" in name else (base, name)
        if not inst:
            return
        f = inst.data["labels"].get(lab)
        if f is None:
            try:
                f = int(lab) - 1
            except ValueError:
                return
        inst.run_frame(f)

    def run(self, code: list, this: Inst):
        stack, target, pc, steps = [], this, 0, 0
        pop = lambda: stack.pop() if stack else ""
        while pc < len(code) and steps < 20000:
            op, arg = code[pc]
            pc += 1
            steps += 1
            if op == 0x00:
                break
            elif op == 0x96:
                stack.extend(arg)
            elif op == 0x1C:
                stack.append(self.get(str(pop()), target))
            elif op == 0x1D:
                v = pop()
                self.set(str(pop()), v, target)
            elif op == 0x8B:
                target = this if arg == "" else (self.resolve(arg, this) or Inst(self, 0, "?", None))
            elif op == 0x20:
                t = str(pop())
                target = this if t == "" else (self.resolve(t, this) or Inst(self, 0, "?", None))
            elif op == 0x81:
                target.goto(arg, False)
            elif op == 0x8C:
                f = target.data["labels"].get(arg)
                if f is not None:
                    target.goto(f, False)
            elif op == 0x9F:
                v = pop()
                f = target.data["labels"].get(v) if isinstance(v, str) and v in target.data["labels"] else int(num(v)) - 1
                target.goto(f, bool(arg & 1))
            elif op == 0x06:
                target.playing = True
            elif op == 0x07:
                target.playing = False
            elif op == 0x9E:
                self.call(str(pop()), target)
            elif op == 0x99:
                pc = arg
            elif op == 0x9D:
                if num(pop()) != 0:
                    pc = arg
            elif op == 0x0E:
                a, b = num(pop()), num(pop())
                stack.append(1.0 if abs(a - b) < 1e-6 else 0.0)
            elif op == 0x0F:
                a, b = num(pop()), num(pop())
                stack.append(1.0 if b < a else 0.0)
            elif op == 0x0A:
                a, b = num(pop()), num(pop())
                stack.append(b + a)
            elif op == 0x0B:
                a, b = num(pop()), num(pop())
                stack.append(b - a)
            elif op == 0x0C:
                a, b = num(pop()), num(pop())
                stack.append(b * a)
            elif op == 0x0D:
                a, b = num(pop()), num(pop())
                stack.append(b / a if a else 0.0)
            elif op == 0x10:
                a, b = num(pop()), num(pop())
                stack.append(1.0 if a and b else 0.0)
            elif op == 0x11:
                a, b = num(pop()), num(pop())
                stack.append(1.0 if a or b else 0.0)
            elif op == 0x12:
                stack.append(0.0 if num(pop()) else 1.0)
            elif op == 0x18:
                stack.append(float(int(num(pop()))))
            elif op == 0x21:
                a, b = pop(), pop()
                stack.append(str(fmt(b)) + str(fmt(a)))
            elif op == 0x34:
                stack.append(float(int((time.time() - T0) * 1000)))
            elif op == 0x83:
                self.log.append(arg)
            else:
                self.log.append(f"op {op:02X}")


def render(player: Player, out_dir: Path, dst: Path):
    from PIL import Image, ImageDraw
    import numpy as np
    doc = player.doc
    W, H = 900, 760
    img = Image.new("RGBA", (W, H), (40, 40, 48, 255))
    texs = {}

    REP = 24  # UV repetido (barras: v de -8 a 9): textura ladrilhada REP × REP, UV deslocado para o meio

    def tex(i):
        if i not in texs:
            t = Image.open(out_dir / f"{doc['textures'][i]}.png").convert("RGBA")
            big = Image.new("RGBA", (t.width * REP, t.height * REP))
            for y in range(REP):
                for x in range(REP):
                    big.paste(t, (x * t.width, y * t.height))
            texs[i] = (t, big)
        return texs[i]

    def mul(a, b):
        ox, oy, a0, a1, a2, a3 = a
        bx, by, b0, b1, b2, b3 = b
        return [bx * a0 + by * a2 + ox, bx * a1 + by * a3 + oy, b0 * a0 + b1 * a2, b0 * a1 + b1 * a3,
                b2 * a0 + b3 * a2, b2 * a1 + b3 * a3]

    def draw_ref(ri, t, color):
        r = doc["meshrefs"][ri]
        for oi, tris in enumerate(doc["parts"][r["part"]]):
            ti, c = r["mats"][oi] if oi < len(r["mats"]) else (-1, 0xFFFFFFFF)
            tint = [((c >> (8 * i)) & 0xFF) / 128.0 * color[i] for i in range(4)]
            for tri in tris:
                pts = [(tri[i] * t[2] + tri[i + 1] * t[4] + t[0], tri[i] * t[3] + tri[i + 1] * t[5] + t[1]) for i in (0, 4, 8)]
                if max(p[0] for p in pts) < 0 or min(p[0] for p in pts) > W or max(p[1] for p in pts) < 0 or min(p[1] for p in pts) > H:
                    continue
                mask = Image.new("L", (W, H), 0)
                ImageDraw.Draw(mask).polygon(pts, fill=255)
                if ti >= 0:
                    t1, tx = tex(ti)
                    us, vs = [tri[i + 2] for i in (0, 4, 8)], [tri[i + 3] for i in (0, 4, 8)]
                    ou, ov = REP // 2 - int(min(us) // 1) - 1, REP // 2 - int(min(vs) // 1) - 1
                    uv = [((u + ou) * t1.width, (v + ov) * t1.height) for u, v in zip(us, vs)]
                    A = np.array([[p[0], p[1], 1] for p in pts])
                    try:
                        cx, cy = np.linalg.solve(A, [q[0] for q in uv]), np.linalg.solve(A, [q[1] for q in uv])
                    except np.linalg.LinAlgError:
                        continue
                    layer = tx.transform((W, H), Image.AFFINE, (*cx, *cy), resample=Image.BILINEAR)
                else:
                    layer = Image.new("RGBA", (W, H), (255, 255, 255, 255))
                chans = [ch.point(lambda v, k=k: max(0, min(255, int(v * tint[k])))) for k, ch in enumerate(layer.split())]
                layer = Image.merge("RGBA", chans)
                layer.putalpha(Image.composite(layer.split()[3], Image.new("L", (W, H), 0), mask))
                img.alpha_composite(layer)

    GLYPH_ADVANCE = 0.0982  # avanço = largura do símbolo × escala × isto (calibrado nos rótulos estáticos)

    def draw_glyphs(font, glyphs, x, y, scale, t, color):
        for gid, w in glyphs:
            if 0 <= gid < len(font["glyphs"]):
                gt = mul(t, [x, y, scale, 0, 0, scale])
                draw_ref(font["glyphs"][gid], gt, color)
            x += w
        return x

    def draw_static(lab, t, color):
        t = mul(t, lab["tr"])
        font, scale, x, y, col = None, 1.0, 0.0, 0.0, color
        for c in lab["cmds"]:
            if c["flags"] & 8:
                font, scale = doc["fonts"][c["font"]], c["scale"]
            if c["flags"] & 4:
                col = [color[i] * c["color"][i] / 255.0 for i in range(4)]
            if c["flags"] & 2:
                x = c["x"]
            if c["flags"] & 1:
                y = c["y"]
            if font:
                x = draw_glyphs(font, c["glyphs"], x, y, scale, t, col)

    def draw_text(lab, text, t, color):
        font = doc["fonts"][lab["font"]]
        bc = lab["BlendColor"]
        col = [color[i] * ((bc >> (8 * i)) & 0xFF) / 128.0 for i in range(4)]
        scale = lab["Unk014"] / 48.0  # [HIPÓTESE] altura do texto
        glyphs = []
        for ch in text:
            o = ord(ch)
            gid = font["map"][o] if o < len(font["map"]) else -1
            if gid >= 0:
                glyphs.append([gid, font["widths"][gid] * scale * GLYPH_ADVANCE])
        draw_glyphs(font, glyphs, 0.0, 0.0, scale, t, col)

    def draw(inst: Inst, t, color, depth=0):
        for ei, kfs in enumerate(inst.data["elements"]):
            kf = player.keyframe(kfs, inst.frame)
            if kf is None:
                continue
            _, typ, oid, tri, ci, nm = kf
            nt = mul(t, doc["transforms"][tri]) if tri >= 0 else t
            nc = [color[i] * doc["colors"][ci][i] / 256.0 for i in range(4)] if ci >= 0 else color
            if nc[3] <= 0.01:
                continue
            if typ == 1:
                draw_ref(oid, nt, nc)
            elif typ == 4:
                draw_static(doc["statics"][oid], nt, nc)
            elif typ == 5:
                lab = doc["dynamics"][oid]
                draw_text(lab, str(fmt(player.get(lab["ValueName"], inst))), nt, nc)
            elif typ in (6, 7):
                c = inst.children.get(ei)
                if c and c[1] and depth < 16:
                    draw(c[1], nt, nc, depth + 1)

    draw(player.root, [0, 0, 1, 0, 0, 1], [1.0, 1.0, 1.0, 1.0])
    img.save(dst)


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    doc = json.loads((src / "hud.json").read_text())
    pl = Player(doc)
    pl.root.enter()
    args = sys.argv[3:]
    ticks = int(args[args.index("--ticks") + 1]) if "--ticks" in args else 30
    for a in args:
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1)
            pl.root.vars[k] = v
    for _ in range(ticks):
        pl.root.tick()
        pl.call("SimKeyEvent", pl.root)
    print("log:", pl.log[:10])
    render(pl, src, dst)
    print(dst)
