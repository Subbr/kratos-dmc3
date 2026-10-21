"""Round-trip dos blocos de textura em todos os PACs do jogo."""
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pac  # noqa: E402
import paths  # noqa: E402
import tex  # noqa: E402

NBZ = paths.get("DMC3_NBZ")


def _blocks():
    if not NBZ.exists():
        pytest.skip("dmc3-0.nbz não encontrado")

    def walk(data, name):
        try:
            p = pac.Pac.parse(data)
        except ValueError:
            return
        for i, e in enumerate(p.entries):
            if e is None:
                continue
            if tex.TextureBlock.looks_like(e):
                yield f"{name}#{i}", e
            elif e[:4] in pac.MAGICS:
                yield from walk(e, f"{name}#{i}")

    with zipfile.ZipFile(NBZ) as z:
        for info in z.infolist():
            if info.filename.endswith(".pac"):
                yield from walk(z.read(info), info.filename)


def test_roundtrip_all_texture_blocks():
    total, fails = 0, []
    for name, data in _blocks():
        total += 1
        if tex.TextureBlock.parse(data).build() != data:
            fails.append(name)
    assert total > 0
    assert not fails, f"{len(fails)}/{total}: {fails[:10]}"


def test_make_texture_reproduces_descriptor_fields():
    with zipfile.ZipFile(NBZ) as z:
        block = tex.TextureBlock.parse(pac.Pac.parse(z.read("GData.afs/pl000.pac")).entries[0])
    for t in block.textures:
        made = tex.make_texture(t.dds, t.descriptor)
        assert made.descriptor == t.descriptor and made.sectors == t.sectors
