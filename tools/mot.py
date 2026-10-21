"""MOT (animação do DMC3 HD): leitura e escrita. Formato em docs/formats/mot.md.

Cabeçalho (header_size bytes, 0x50 no Dante): tamanho, "MOT\\0", frames, contagem de ossos e uma
máscara u16 de canais por osso. Depois: u32 com o número de tracks (= total de bits das máscaras),
tracks em sequência (ordem: osso, depois TX TY TZ RX RY RZ SX SY SZ) e zeros até alinhar em 16.
Base de campos: DMC3-Blender-Import-Addon (MIT), DMC3/motion.py.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

# bit da máscara de cada canal, na ordem em que as tracks aparecem
CHANNEL_BITS = (1 << 8, 1 << 7, 1 << 6, 1 << 5, 1 << 4, 1 << 3, 1 << 2, 1 << 1, 1 << 0)
CHANNELS = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")

LINEAR_F32, HERMITE_F32, LINEAR_I16, HERMITE_I16 = 0, 1, 2, 3
# tamanho dos parâmetros após os 8 bytes fixos da track (min/range em f32) e de cada chave
PARAM_SIZE = {LINEAR_F32: 0, HERMITE_F32: 0, LINEAR_I16: 8, HERMITE_I16: 24}
KEY_SIZE = {LINEAR_F32: 8, HERMITE_F32: 16, LINEAR_I16: 4, HERMITE_I16: 8}
Q16 = 1.0 / 65535.0


def _align(n: int, a: int = 16) -> int:
    return (n + a - 1) // a * a


@dataclass
class Track:
    bone: int
    channel: str
    comp: int
    start: int                      # u16 após o tipo; 0 na maioria
    key_count: int
    params: bytes                   # min/range (e min/range das tangentes no HERMITE_I16)
    body: bytes                     # chaves cruas (tipo 7: formato desconhecido, só preservado)

    def decode(self) -> list[tuple[int, float, float | None, float | None]]:
        """(frame, valor, tangente de entrada, tangente de saída) por chave."""
        if self.comp == LINEAR_I16:
            vmin, vrange = struct.unpack_from("<2f", self.params)
            return [(t & 0x7FFF, v * vrange * Q16 + vmin, None, None)
                    for t, v in struct.iter_unpack("<2H", self.body)]
        if self.comp == HERMITE_I16:
            vmin, vrange, imin, irange, omin, orange = struct.unpack_from("<6f", self.params)
            return [(t & 0x7FFF, v * vrange * Q16 + vmin, i * irange * Q16 + imin, o * orange * Q16 + omin)
                    for t, v, i, o in struct.iter_unpack("<4H", self.body)]
        if self.comp == LINEAR_F32:
            return [(t & 0x7FFF, v, None, None) for t, _, v in struct.iter_unpack("<2Hf", self.body)]
        if self.comp == HERMITE_F32:
            return [(t & 0x7FFF, v, i, o) for t, _, v, i, o in struct.iter_unpack("<2H3f", self.body)]
        raise NotImplementedError(f"compressão {self.comp}")

    def sample(self, frame: float) -> float:
        keys = self.decode()
        if frame <= keys[0][0]:
            return keys[0][1]
        for (t0, v0, _, o0), (t1, v1, i1, _) in zip(keys, keys[1:]):
            if frame <= t1:
                if o0 is None:
                    return v0 + (v1 - v0) * (frame - t0) / (t1 - t0)
                return _hermite(frame, t0, v0, o0, t1, v1, i1)
        return keys[-1][1]

    @classmethod
    def hermite(cls, bone: int, channel: str, values: list[float]) -> "Track":
        """Track nova HERMITE_I16 (a única que o Dante usa), uma chave por frame; tangentes = diferença
        central em unidades por frame; bit 15 do tempo ligado em todas as chaves, como no jogo."""
        n = len(values)
        tan = [(values[min(i + 1, n - 1)] - values[max(i - 1, 0)]) / max(min(i + 1, n - 1) - max(i - 1, 0), 1)
               for i in range(n)]

        def quant(xs: list[float]) -> tuple[float, float, list[int]]:
            lo, rng = min(xs), max(xs) - min(xs)
            return lo, rng, [round((x - lo) / rng * 65535) if rng else 0 for x in xs]

        vmin, vrange, qv = quant(values)
        tmin, trange, qt = quant(tan)
        body = b"".join(struct.pack("<4H", 0x8000 | f, v, t, t) for f, (v, t) in enumerate(zip(qv, qt)))
        params = struct.pack("<6f", vmin, vrange, tmin, trange, tmin, trange)
        return cls(bone, channel, HERMITE_I16, 0, n, params, body)

    @classmethod
    def linear(cls, bone: int, channel: str, values: list[float]) -> "Track":
        """Track nova LINEAR_I16 com uma chave por frame. [NÃO USAR NO JOGADOR] o Dante só usa HERMITE_I16 e
        nas poucas tracks LINEAR_I16 do jogo o bit 15 do tempo fica desligado; o T7 com este tipo falhou."""
        vmin, vmax = min(values), max(values)
        vrange = vmax - vmin
        q = [round((v - vmin) / vrange * 65535) if vrange else 0 for v in values]
        body = b"".join(struct.pack("<2H", 0x8000 | f, x) for f, x in enumerate(q))
        return cls(bone, channel, LINEAR_I16, 0, len(values), struct.pack("<2f", vmin, vrange), body)

    def build(self) -> bytes:
        size = 8 + len(self.params) + len(self.body)
        return struct.pack("<4H", size, self.key_count, self.comp, self.start) + self.params + self.body


def _hermite(f: float, t0: float, v0: float, out0: float, t1: float, v1: float, in1: float) -> float:
    # mesma forma do importador (DMC3/motion.py), tangentes em unidades por frame
    t = f - t0
    step = 1.0 / (t1 - t0)
    a = t * t * step * step
    b = t * t * step
    c = a * t
    return ((t + c - b - b) * out0 + (step * c + step * c - a * 3 + 1) * v0
            + (a * 3 - (step * c + step * c)) * v1 + (c - b) * in1)


@dataclass
class Motion:
    header: bytearray               # cabeçalho inteiro (máscaras regravadas em build)
    tracks: list[Track] = field(default_factory=list)
    tail: bytes = b""               # bytes após a última track (zeros de alinhamento)

    @property
    def bone_count(self) -> int:
        return struct.unpack_from("<H", self.header, 0x1C)[0]

    @property
    def frames(self) -> float:
        return struct.unpack_from("<f", self.header, 0x0C)[0]

    @frames.setter
    def frames(self, n: float) -> None:
        struct.pack_into("<f", self.header, 0x0C, n)
        struct.pack_into("<f", self.header, 0x14, n)

    @classmethod
    def parse(cls, b: bytes) -> "Motion":
        if b[4:8] != b"MOT\0":
            raise ValueError("não é MOT")
        (hs,) = struct.unpack_from("<I", b)
        m = cls(bytearray(b[:hs]))
        masks = struct.unpack_from(f"<{m.bone_count}H", b, 0x1E)
        (count,) = struct.unpack_from("<I", b, hs)
        pos = hs + 4
        slots = [(bone, ch) for bone, mask in enumerate(masks)
                 for bit, ch in zip(CHANNEL_BITS, CHANNELS) if mask & bit]
        if len(slots) != count:
            raise ValueError(f"máscaras indicam {len(slots)} tracks, arquivo diz {count}")
        for bone, ch in slots:
            size, kc, comp, start = struct.unpack_from("<4H", b, pos)
            psize = PARAM_SIZE.get(comp, 0)
            m.tracks.append(Track(bone, ch, comp, start, kc, b[pos + 8:pos + 8 + psize], b[pos + 8 + psize:pos + size]))
            pos += size
        m.tail = b[pos:]
        return m

    def build(self, pad: bool | None = None) -> bytes:
        """pad=None: reusa a cauda lida; True: zeros até alinhar em 16."""
        masks = [0] * self.bone_count
        order = {ch: i for i, ch in enumerate(CHANNELS)}
        self.tracks.sort(key=lambda t: (t.bone, order[t.channel]))
        for t in self.tracks:
            masks[t.bone] |= CHANNEL_BITS[order[t.channel]]
        out = bytearray(self.header)
        struct.pack_into(f"<{self.bone_count}H", out, 0x1E, *masks)
        out += struct.pack("<I", len(self.tracks))
        for t in self.tracks:
            out += t.build()
        if pad:
            out += bytes(_align(len(out)) - len(out))
        elif pad is None:
            out += self.tail
        return bytes(out)

    def track(self, bone: int, channel: str) -> Track | None:
        return next((t for t in self.tracks if t.bone == bone and t.channel == channel), None)
