"""Round-trip do MOD: reconstrução do zero de todos os MODs do jogo (dentro dos PACs, recursivo)."""
import collections
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import mod  # noqa: E402
import pac  # noqa: E402
import paths  # noqa: E402

NBZ = paths.get("DMC3_NBZ")


def _mods():
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
            if e[:4] == b"MOD ":
                yield f"{name}#{i}", e
            elif e[:4] in pac.MAGICS:
                yield from walk(e, f"{name}#{i}")

    with zipfile.ZipFile(NBZ) as z:
        for info in z.infolist():
            if info.filename.endswith(".pac"):
                yield from walk(z.read(info), info.filename.removeprefix("GData.afs/"))


def test_roundtrip_all_mods():
    fails = collections.Counter()
    examples = {}
    total = 0
    for name, data in _mods():
        total += 1
        try:
            ok = mod.Model.parse(data).build() == data
            reason = "diferente"
        except Exception as e:  # noqa: BLE001
            ok, reason = False, type(e).__name__ + ": " + str(e)[:60]
        if not ok:
            fails[reason] += 1
            examples.setdefault(reason, name)
    assert not fails, f"{sum(fails.values())}/{total} falhas: {dict(fails)} ex.: {examples}"
