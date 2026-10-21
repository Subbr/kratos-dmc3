"""Round-trip do PAC em todos os .pac do dmc3-0.nbz (lê do jogo, não grava nada nele)."""
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pac  # noqa: E402
import paths  # noqa: E402

NBZ = paths.get("DMC3_NBZ")


def _pacs():
    if not NBZ.exists():
        pytest.skip("dmc3-0.nbz não encontrado")
    with zipfile.ZipFile(NBZ) as z:
        for info in z.infolist():
            if info.filename.endswith(".pac"):
                yield info.filename, z.read(info)


def test_roundtrip_all():
    failures = [name for name, data in _pacs() if pac.Pac.parse(data).build() != data]
    assert not failures, f"{len(failures)} falhas, ex.: {failures[:10]}"


def test_unpack_repack_dir(tmp_path):
    with zipfile.ZipFile(NBZ) as z:
        data = z.read("GData.afs/pl000.pac")
    src = tmp_path / "pl000.pac"
    src.write_bytes(data)
    pac.unpack(src, tmp_path / "out")
    pac.repack(tmp_path / "out", tmp_path / "re.pac")
    assert (tmp_path / "re.pac").read_bytes() == data
