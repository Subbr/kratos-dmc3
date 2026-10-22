"""Trilhas dos ossos das lâminas (24 = direita, filho da mão 9; 25 = esquerda, filho de 13) nas motions.

Toda motion do jogador passa a ter 26 ossos: sem trilha, o jogo mantém a última posição do osso e a lâmina
fica presa onde a motion anterior a deixou (T14). Nos golpes (grupo da arma das Blades), cada lâmina sai
da mão ao longo do antebraço quando a mão dela está rápida e volta depois (alcance da corrente do GoW1).
"""
from __future__ import annotations

import struct

import numpy as np

import anim_retarget as ar
import mod
import mot

HANDS = {24: (9, -1.0), 25: (13, 1.0)}  # osso da lâmina: (mão, sentido do antebraço em x na pose de repouso)
REACH = 120.0       # alcance máximo da corrente (unidades do modelo; braço do Dante ≈ 70)
FAST = 0.55         # fração da velocidade máxima da mão que conta como golpe
RAMP = 8            # quadros de subida/descida em volta do trecho rápido


def blade_offsets(model: mod.Model) -> dict[int, np.ndarray]:
    return {b: np.array(struct.unpack_from("<3f", model.skeleton.transforms[b])) for b in HANDS}


def reach_curve(mo: mot.Motion, body: mod.Model, parent: list[int], frames: int, hand: int) -> list[float]:
    """0..1 por quadro: 1 enquanto a mão está acima de FAST da sua velocidade máxima, com rampas suaves."""
    pos = [ar._fk(mo, f, body, parent)[hand] for f in range(frames)]
    speed = np.array([0.0] + [np.linalg.norm(pos[f] - pos[f - 1]) for f in range(1, frames)])
    if speed.max() < 2.0:  # mão quase parada: não é golpe dessa mão
        return [0.0] * frames
    fast = speed >= FAST * speed.max()
    out = np.zeros(frames)
    for f in np.nonzero(fast)[0]:
        for d in range(-RAMP, RAMP + 1):
            g = f + d
            if 0 <= g < frames:
                out[g] = max(out[g], 0.5 + 0.5 * np.cos(np.pi * abs(d) / (RAMP + 1)) if d else 1.0)
    return out.tolist()


def add_blade_tracks(mo: mot.Motion, offsets: dict[int, np.ndarray], body: mod.Model | None = None,
                     parent: list[int] | None = None, reach: bool = False) -> None:
    """Deixa a motion com 26 ossos e trilhas de translação para as lâminas (em repouso ou com alcance)."""
    if mo.bone_count == len(offsets) + 24 and any(t.bone in offsets for t in mo.tracks):
        return
    frames = int(round(mo.frames)) + 1
    curves = {b: reach_curve(mo, body, parent, frames, HANDS[b][0]) if reach else [0.0] * frames for b in offsets}
    mo.resize_bones(24 + len(offsets))
    for b, off in offsets.items():
        side = HANDS[b][1]
        mo.tracks.append(mot.Track.hermite(b, "tx", [off[0] + side * REACH * c for c in curves[b]]))
        mo.tracks.append(mot.Track.hermite(b, "ty", [off[1]] * frames))
        mo.tracks.append(mot.Track.hermite(b, "tz", [off[2]] * frames))
