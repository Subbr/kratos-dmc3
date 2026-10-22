"""Round-trip do MOT: todas as motions do jogo (dentro dos PACs, recursivo)."""
import collections
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import mot  # noqa: E402
import pac  # noqa: E402
import paths  # noqa: E402

NBZ = paths.get("DMC3_NBZ")


def _mots():
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
            if e[4:8] == b"MOT\0":
                yield f"{name}#{i}", e
            elif e[:4] in pac.MAGICS:
                yield from walk(e, f"{name}#{i}")

    with zipfile.ZipFile(NBZ) as z:
        for info in z.infolist():
            if info.filename.endswith(".pac"):
                yield from walk(z.read(info), info.filename.removeprefix("GData.afs/"))


def test_roundtrip_all_mots():
    fails = collections.Counter()
    total = 0
    for name, data in _mots():
        total += 1
        m = mot.Motion.parse(data)
        if m.build() != data:
            fails["diferente"] += 1
        if m.build(pad=True) != data:
            fails["cauda != alinhamento 16"] += 1
    assert total > 10000
    assert not fails, f"{dict(fails)} de {total}"


def test_linear_track_roundtrip():
    values = [0.0, 0.5, -1.25, 3.0]
    t = mot.Track.linear(2, "rx", values)
    keys = t.decode()
    assert [k[0] for k in keys] == [0, 1, 2, 3]
    assert all(abs(k[1] - v) < 1e-3 for k, v in zip(keys, values))
    assert abs(t.sample(1.5) - (-0.375)) < 1e-3


def test_hermite_track_roundtrip():
    values = [0.0, 0.5, -1.25, 3.0, 3.0]
    t = mot.Track.hermite(2, "rx", values)
    assert all(abs(k[1] - v) < 1e-3 for k, v in zip(t.decode(), values))
    assert abs(t.sample(3.0) - 3.0) < 1e-3
    assert mot.Track(*[getattr(t, f) for f in ("bone", "channel", "comp", "start", "key_count", "params", "body")]).build() == t.build()


def test_play_start_combo_rebellion():
    """0x08 = quadro em que o jogo começa a tocar a motion (T18): combo da Rebellion no pl000_00_3."""
    if not NBZ.exists():
        pytest.skip("dmc3-0.nbz não encontrado")
    with zipfile.ZipFile(NBZ) as z:
        p = pac.Pac.parse(z.read("GData.afs/pl000_00_3.pac"))
    starts = {i: mot.Motion.parse(p.entries[i]).play_start for i in (3, 4, 5, 6, 7)}
    assert starts == {3: 0.0, 4: 23.0, 5: 40.0, 6: 23.0, 7: 75.0}
