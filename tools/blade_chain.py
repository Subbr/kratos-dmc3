"""Trilhas dos ossos das lâminas nas motions do jogador (esqueleto do kratos_fit --blade-bones).

O jogador só pode ter 24 ossos (T15): a lâmina direita usa o osso 23 (filho da mão 9) e a esquerda o 4
(filho da mão 13); a cabeça (5) passa a ser filha do peito (3). Nas motions originais do Dante a rotação do
pescoço é composta na da cabeça (mesma pose). Toda motion precisa da trilha das lâminas: sem ela o jogo
mantém a última posição do osso (T14). Nos golpes do grupo das Blades, cada lâmina sai da mão ao longo do
antebraço quando a mão dela está rápida e volta depois (alcance da corrente do GoW1).
"""
from __future__ import annotations

import struct

import numpy as np

import anim_retarget as ar
import mod
import mot

HANDS = {23: (9, -1.0), 4: (13, 1.0)}  # osso da lâmina: (mão, sentido do antebraço em x na pose de repouso)
NECK, HEAD = 4, 5
REACH = 200.0       # alcance máximo da corrente (unidades do modelo; braço do Dante ≈ 70). T16: 120 ficou sutil
FAST = 0.40         # fração da velocidade máxima da mão que conta como golpe
RAMP = 12           # quadros de subida/descida em volta do trecho rápido


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


def fold_neck_into_head(mo: mot.Motion, neck_off: np.ndarray, head_off: np.ndarray) -> None:
    """Motion original do Dante: a cabeça passa a ser filha do peito, então a cada quadro
    R5' = R4 · R5 e T5' = T4 + R4 · T5 (offsets do esqueleto original do Dante; mesma pose exata)."""
    neck = [mo.track(NECK, "r" + c) for c in "xyz"]
    if not any(neck):
        return
    head = [mo.track(HEAD, "r" + c) for c in "xyz"]
    frames = int(round(mo.frames)) + 1
    vals: dict[str, list[float]] = {c: [] for c in "xyz"}
    pos: dict[str, list[float]] = {c: [] for c in "xyz"}
    prev = None
    for f in range(frames):
        r4 = ar.rot_xyz(*[t.sample(f) if t else 0.0 for t in neck])
        r5 = ar.rot_xyz(*[t.sample(f) if t else 0.0 for t in head])
        e = np.array(ar.euler_xyz(r4 @ r5))
        if prev is not None:
            e = prev + (e - prev + np.pi) % (2 * np.pi) - np.pi
        prev = e
        for c, v in zip("xyz", e):
            vals[c].append(float(v))
        for c, v in zip("xyz", neck_off + r4 @ head_off):
            pos[c].append(float(v))
    mo.tracks = [t for t in mo.tracks if t.bone != HEAD]
    mo.tracks += [mot.Track.hermite(HEAD, "r" + c, vals[c]) for c in "xyz"]
    mo.tracks += [mot.Track.hermite(HEAD, "t" + c, pos[c]) for c in "xyz"]


def add_blade_tracks(mo: mot.Motion, offsets: dict[int, np.ndarray], body: mod.Model | None = None,
                     parent: list[int] | None = None, reach: bool = False) -> None:
    """Troca as trilhas dos ossos das lâminas por translação (repouso ou alcance) e rotação nula."""
    frames = int(round(mo.frames)) + 1
    curves = {b: reach_curve(mo, body, parent, frames, HANDS[b][0]) if reach else [0.0] * frames for b in offsets}
    mo.tracks = [t for t in mo.tracks if t.bone not in offsets]
    for b, off in offsets.items():
        side = HANDS[b][1]
        mo.tracks.append(mot.Track.hermite(b, "tx", [off[0] + side * REACH * c for c in curves[b]]))
        mo.tracks.append(mot.Track.hermite(b, "ty", [off[1]] * frames))
        mo.tracks.append(mot.Track.hermite(b, "tz", [off[2]] * frames))
