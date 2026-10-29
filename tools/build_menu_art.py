"""Artes dos menus nativos com o Kratos no lugar do Dante (T59).

Uso: python -I tools/build_menu_art.py <saída>   (renders em work/install/menu_art/renders, blender/scripts/render_kratos.py)
Lê os id*.pac do .nbz do usuário, troca a textura (fundo da própria arte sem o Dante + render do Kratos) e reempacota
(round-trip do PAC e do bloco de textura conferidos antes).
"""
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pac  # noqa: E402
import paths  # noqa: E402
import tex  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NBZ = paths.get("DMC3_NBZ")
CRIMSON = ROOT / "work/backup/crimson_override"  # artes que o Crimson já troca (título, LOAD, menus): base = a dele
RENDERS = ROOT / "work/install/menu_art/renders"
FONT = Path("/mnt/c/Windows/Fonts/georgiaz.ttf")  # serifa negrito itálico, perto da fonte dos nomes do DMC3

# (pac, entrada, textura, modo, render, escala, centro x, base y) — escala/posições em fração do tamanho da arte.
# modo: scene = fundo da própria arte sem a figura (bordas esticadas); cutout = textura transparente (só a figura,
# no lugar da do Dante); right = troca só a metade direita (LOAD: Vergil fica); dark = fundo escuro novo,
# preservando os riscos vermelhos da arte; label = troca o texto "DANTE" por "KRATOS".
TARGETS = [
    ("id7168.pac", 1, 0, "scene", "blades_end.png", 0.92, 0.5, 1.0),   # fim de missão: Dante na poltrona
    ("id900.pac", 8, 0, "cutout", "blades_title.png", 1.0, 0.66, 1.0),  # título do Crimson (T77)
    ("id900.pac", 14, 0, "label", None, 0, 0, 0),                       # "VERGIL  DANTE"
    ("id7008.pac", 1, 0, "right", "blades_load.png", 0.92, 0.79, 1.0),  # LOAD/SAVE: Vergil e Dante
    ("id7008.pac", 17, 0, "label", None, 0, 0, 0),                      # rótulo do slot: "VERGIL" / "DANTE"
    ("id430.pac", 4, 0, "dark", "blades_menu.png", 0.84, 0.68, 0.88),   # fundos dos menus (Dante ao telefone)
    ("id435.pac", 0, 0, "dark", "blades_menu.png", 0.84, 0.68, 0.88),
    ("id440.pac", 0, 0, "dark", "blades_menu.png", 0.84, 0.68, 0.88),
    ("id470.pac", 0, 0, "dark", "blades_menu.png", 0.84, 0.68, 0.88),
]


def background(img: Image.Image) -> Image.Image:
    """Fundo da arte sem a figura: as bordas esquerda e direita (onde não há personagem) esticadas e borradas."""
    a = np.asarray(img.convert("RGB")).astype(float)
    w = a.shape[1]
    edge = np.concatenate([a[:, : w // 8], a[:, -w // 8 :]], axis=1).mean(axis=1, keepdims=True)
    bg = np.repeat(edge, w, axis=1)
    # vinheta escura como nas artes do DMC3
    yy, xx = np.mgrid[0 : a.shape[0], 0:w]
    d = np.hypot((xx - w / 2) / w, (yy - a.shape[0] / 2) / a.shape[0])
    bg *= np.clip(1.15 - d, 0.35, 1.0)[..., None]
    return Image.fromarray(bg.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))


def cut(render: Image.Image) -> Image.Image:
    # o fundo do render não é transparente de todo (luz do mundo): zera o alfa baixo antes de recortar
    alpha = render.getchannel("A").point(lambda v: 0 if v < 40 else v)
    render = render.copy(); render.putalpha(alpha)
    return render.crop(alpha.getbbox())


def place(out: Image.Image, render: Image.Image, scale: float, cx: float, base: float, glow_a: float = 0.7) -> None:
    W, H = out.size
    r = cut(render)
    k = scale * H / r.height
    r = r.resize((int(r.width * k), int(r.height * k)), Image.LANCZOS)
    # contorno vermelho suave atrás do Kratos
    glow = Image.new("RGBA", r.size, (200, 30, 20, 0))
    glow.putalpha(r.getchannel("A").filter(ImageFilter.GaussianBlur(max(6, H // 60))).point(lambda v: v * glow_a))
    pos = (int(cx * W - r.width / 2), int(base * H - r.height))
    out.alpha_composite(glow, pos)
    out.alpha_composite(r, pos)


def dark_bg(orig: Image.Image) -> Image.Image:
    """Fundo escuro quente (vinheta + ruído) com os riscos vermelhos da arte original (decoração dos menus)."""
    a = np.asarray(orig.convert("RGB")).astype(float)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot((xx - w * 0.65) / w, (yy - h * 0.45) / h)
    base = np.clip(0.55 - d, 0.04, 1.0)[..., None] * np.array([150, 70, 45])
    base += np.random.default_rng(7).normal(0, 3, (h, w, 1))
    red = (a[..., 0] > 90) & (a[..., 1] < 45) & (a[..., 2] < 45) & (xx < w * 0.55)
    base[red] = a[red]
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))


def right_half(orig: Image.Image, x0: float) -> Image.Image:
    """Apaga a figura da direita repetindo a coluna x0 (fundo e linhas horizontais), com a ponta das linhas indo ao
    vermelho como na arte."""
    a = np.asarray(orig.convert("RGB")).astype(float).copy()
    c = int(x0 * a.shape[1])
    col = a[:, c:c + 1]
    n = a.shape[1] - c
    t = np.linspace(0, 1, n)[None, :, None]
    line = (col.max(axis=2, keepdims=True) > 40)  # as linhas (o fundo é quase preto)
    lum = col.mean(axis=2, keepdims=True)
    reddish = np.concatenate([lum * 1.6, lum * 0.25, lum * 0.3], axis=2)
    a[:, c:] = np.where(line, col * (1 - t) + reddish * t, col)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def label(orig: Image.Image) -> Image.Image:
    """"DANTE" (letras vermelhas) → "KRATOS" na mesma cor, altura e centro; comprimido na largura do original. Com
    contorno claro quando o original tem (rótulo do slot na tela LOAD, id7008)."""
    from PIL import ImageDraw, ImageFont
    out = orig.copy()
    A = np.asarray(orig).astype(int)
    m = (A[..., 3] > 60) & (A[..., 0] > A[..., 2] + 40) & (A[..., 0] > A[..., 1] + 40)  # letras vermelhas
    ys, xs = np.nonzero(m)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    color = tuple(int(v) for v in np.median(A[m][:, :3], axis=0))
    pad = max(3, (box[3] - box[1]) // 8)
    clear = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
    # contorno: pixels opacos e claros em volta das letras
    ring = A[clear[1]:clear[3], clear[0]:clear[2]]
    light = (ring[..., 3] > 60) & (ring[..., :3].min(axis=2) > 120)
    stroke = max(1, (box[3] - box[1]) // 14) if light.mean() > 0.03 else 0
    out.paste((0, 0, 0, 0), clear)
    hgt = box[3] - box[1]
    font = ImageFont.truetype(str(FONT), int(hgt * 1.38))
    tmp = Image.new("RGBA", (hgt * 12, hgt * 3), (0, 0, 0, 0))
    dr = ImageDraw.Draw(tmp)
    dr.text((hgt, hgt), "KRATOS", font=font, fill=color + (255,), stroke_width=stroke, stroke_fill=(200, 200, 200, 255))
    txt = tmp.crop(tmp.getbbox())
    w = min(txt.width, int((box[2] - box[0]) * 1.08))
    txt = txt.resize((w, hgt + 2 * stroke), Image.LANCZOS)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    out.alpha_composite(txt, (int(cx - txt.width / 2), int(cy - txt.height / 2)))
    return out


def compose(orig: Image.Image, mode: str, render: Image.Image | None, scale: float, cx: float, base: float) -> Image.Image:
    if mode == "label":
        return label(orig.convert("RGBA"))
    if mode == "cutout":
        out = Image.new("RGBA", orig.size, (0, 0, 0, 0))
        place(out, render, scale, cx, base, 0.5)
        return out
    bg = {"scene": background, "dark": dark_bg, "right": lambda o: right_half(o, 0.58)}[mode](orig)
    out = bg.convert("RGBA")
    place(out, render, scale, cx, base)
    return out


def source(z: zipfile.ZipFile, name: str) -> bytes:
    return (CRIMSON / name).read_bytes() if (CRIMSON / name).exists() else z.read(f"GData.afs/{name}")


def main() -> None:
    dst = Path(sys.argv[1])
    dst.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(NBZ)
    pacs: dict[str, pac.Pac] = {}
    for name, entry, k, mode, render, scale, cx, base in TARGETS:
        if name not in pacs:
            raw = source(z, name)
            pacs[name] = pac.Pac.parse(raw)
            assert pacs[name].build() == raw, f"round-trip do PAC falhou: {name}"
        p = pacs[name]
        blk = tex.TextureBlock.parse(p.entries[entry])
        assert blk.build() == p.entries[entry], f"round-trip do bloco falhou: {name}"
        t = blk.textures[k]
        orig = Image.open(io.BytesIO(t.dds))
        fmt = t.dds[84:88].decode()
        art = compose(orig, mode, Image.open(RENDERS / render).convert("RGBA") if render else None, scale, cx, base)
        art.convert("RGBA").save(dst / f"{name}_{entry}_{k}.preview.png")
        buf = io.BytesIO()
        (art if fmt == "DXT5" else art.convert("RGB")).save(buf, format="DDS", pixel_format=fmt)
        new = tex.make_texture(buf.getvalue(), t.descriptor)
        if t.trailer:  # id440: bytes depois do DDS no espaço da textura (formato do Crimson), mantidos
            new.trailer = t.trailer
            new.sectors = max(new.sectors, t.sectors)
        blk.textures[k] = new
        p.entries[entry] = blk.build()
        print(name, entry, k, mode, orig.size, fmt)
    for name, p in pacs.items():
        (dst / name).write_bytes(p.build())


if __name__ == "__main__":
    main()
