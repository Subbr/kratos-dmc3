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
import tex  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NBZ = ROOT / "Devil May Cry HD Collection/data/dmc3/dmc3-0.nbz"
RENDERS = ROOT / "work/install/menu_art/renders"

# (pac, entrada, textura, render, escala, centro x, base y) — fração do tamanho da arte
TARGETS = [
    ("id7168.pac", 1, 0, "pose_10_idleCombat.png", 0.92, 0.5, 1.0),  # fim de missão: Dante na poltrona
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


def compose(orig: Image.Image, render: Image.Image, scale: float, cx: float, base: float) -> Image.Image:
    W, H = orig.size
    out = background(orig).convert("RGBA")
    # o fundo do render não é transparente de todo (luz do mundo): zera o alfa baixo antes de recortar
    alpha = render.getchannel("A").point(lambda v: 0 if v < 40 else v)
    render = render.copy(); render.putalpha(alpha)
    r = render.crop(alpha.getbbox())
    k = scale * H / r.height
    r = r.resize((int(r.width * k), int(r.height * k)), Image.LANCZOS)
    # contorno vermelho suave atrás do Kratos
    glow = Image.new("RGBA", r.size, (200, 30, 20, 0))
    glow.putalpha(r.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 0.7))
    pos = (int(cx * W - r.width / 2), int(base * H - r.height))
    out.alpha_composite(glow, pos)
    out.alpha_composite(r, pos)
    return out


def main() -> None:
    dst = Path(sys.argv[1])
    dst.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(NBZ)
    for name, entry, k, render, scale, cx, base in TARGETS:
        raw = z.read(f"GData.afs/{name}")
        p = pac.Pac.parse(raw)
        assert p.build() == raw, f"round-trip do PAC falhou: {name}"
        blk = tex.TextureBlock.parse(p.entries[entry])
        assert blk.build() == p.entries[entry], f"round-trip do bloco falhou: {name}"
        t = blk.textures[k]
        orig = Image.open(io.BytesIO(t.dds))
        art = compose(orig, Image.open(RENDERS / render).convert("RGBA"), scale, cx, base)
        art.convert("RGB").save(dst / f"{name}.preview.png")
        buf = io.BytesIO()
        art.save(buf, format="DDS", pixel_format="DXT5")
        blk.textures[k] = tex.make_texture(buf.getvalue(), t.descriptor)
        p.entries[entry] = blk.build()
        (dst / name).write_bytes(p.build())
        print(name, orig.size)


if __name__ == "__main__":
    main()
