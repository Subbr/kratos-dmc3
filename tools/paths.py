"""Lê config/paths.env (formato KEY=valor com ${VAR} e comentários #)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_VAR = re.compile(r"\$\{(\w+)\}")


def load(env_file: Path = ROOT / "config" / "paths.env") -> dict[str, str]:
    values: dict[str, str] = {"PROJECT_ROOT": str(ROOT)}
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "PROJECT_ROOT":  # calculado pela posição do repo (o .env usa $(...) do bash)
            continue
        value = value.strip().strip('"')
        values[key.strip()] = _VAR.sub(lambda m: values.get(m.group(1), ""), value)
    return values


def get(key: str) -> Path:
    value = load().get(key)
    if not value:
        raise KeyError(f"{key} não definido em config/paths.env")
    return Path(value)
