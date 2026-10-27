"""Gera o arquivo de golpes do motor Kratos (D11) a partir do grafo de combate do próprio GoW1.

Uso: python -I tools/build_engine_moves.py <pl000_00_2.pac base> <pl000.pac do Kratos> <saída kratosMoves_pl000_00_2.pac>
Grafo: TWK_CombatFile_000…006 (tools/gow_combat.py). Configuração em mapping/engine_moves.yaml. Saída extra:
KratosMoves.json para a DLL: por golpe, quadros, quadro do golpe, ficha de dano, janelas de invulnerabilidade e
**todas** as transições do GoW1 (gatilho, modo do botão, janela, chão/ar/Rage, nível da lâmina); tabelas do parado no
chão e no ar. O deslocamento (x, y, z) vem da `zeroJoint` do glb, no osso 0.
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_retarget as ar  # noqa: E402
import blade_chain  # noqa: E402
import gow_combat  # noqa: E402
import kratos_fit  # noqa: E402
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


# máscara da transição do GoW1 (FUN_002079d8 / FUN_00207220, docs/formats/gow-combat.md): bit 0 = janela que executa
# (antes dela o botão fica guardado), 0x2 chão, 0x4 ar; 0x200 qualquer arma, 0x100 sem 0x200 = só Artemis, nenhum =
# só Blades; 0x400 exige alvo; 0x2000 exige Rage, 0x8000 ignora Rage (sem os dois: fora da Rage)
F_EXEC, F_GROUND, F_AIR, F_TARGET, F_RAGE, F_NORAGE = 1, 2, 4, 8, 0x10, 0x20
NEUTRAL, FALL = -1, -3  # destinos especiais: volta ao parado (DMC3) / cai e aterrissa pelo DMC3


def flags(mask: int) -> int:
    f = mask & 1
    f |= F_GROUND if mask & 2 else 0
    f |= F_AIR if mask & 4 else 0
    f |= F_TARGET if mask & 0x400 else 0
    if not mask & 0x8000:
        f |= F_RAGE if mask & 0x2000 else F_NORAGE
    return f


def artemis_only(mask: int) -> bool:
    return bool(mask & 0x100) and not mask & 0x200


def transition(move: dict, trigger: int) -> tuple[int, float] | None:
    """(destino, ponto de corte) da transição de solo do gatilho: a de máscara com bit 0 (executa) dá o corte."""
    best = None
    for t in move["trans"]:
        if t["trigger"] != trigger or t["target"] < 0 or t["diff"] > 0:
            continue
        if t["mask"] & 1:
            return t["target"], t["window"][0]
        best = best or (t["target"], t["window"][1])
    return best


def zero_root(g: Glb, anim: ar.KratosAnim, frames: int, scale: float) -> tuple[list[float], list[float], list[float]] | None:
    """Deslocamento do GoW1: a junta `zeroJoint` do glb (fora da hierarquia do quadril) leva a translação do golpe
    (evadeFront −146 em z, dash −82, combo3A −24; T89) e a altura (blockLauncher sobe 83, comboJump sobe e cai,
    airImpale desce 191). Osso 0 = (posição − posição inicial) × escala, girada 180° em Y como o resto do esqueleto
    (kratos_fit.ROT_Y180). O evento TAUNT do DMC3 soma x, y e z do osso 0 à posição (FUN_1401fb540 modo 3, REA)."""
    node = next((i for i, n in enumerate(g.j["nodes"]) if n.get("name") == "zeroJoint"), None)
    if node is None:
        return None
    p0 = anim._value(node, "translation", 0.0, [0, 0, 0])[:3]
    xs, ys, zs = [], [], []
    for f in range(frames):
        d = (anim._value(node, "translation", min(f / 60.0, anim.duration), [0, 0, 0])[:3] - p0) * scale
        v = kratos_fit.ROT_Y180[:3, :3] @ d
        xs.append(float(v[0]))
        ys.append(float(v[1]))
        zs.append(float(v[2]))
    return xs, ys, zs


def windows(move: dict, action: int) -> list[list[float]]:
    """Janelas (fração da animação) dos eventos de uma ação: 28 = invulnerável (esquivas 0–0,6, finalizações
    inteiras; FUN_00205488 liga o bit 4 do herói, [HIPÓTESE] pelo padrão dos dados)."""
    return [list(e["window"]) for e in move["events"] if e["action"] == action]


def main(base_pac: Path, model: Path, out: Path) -> None:
    conf = yaml.safe_load((ROOT / "mapping/engine_moves.yaml").read_text(encoding="utf-8"))
    graph = {m["id"]: m for m in gow_combat.load_all(gow_combat.load_hashes())}
    # glb do herói + os das finalizações (grupos externos do ANM do herói nos WADs dos inimigos, T93); a 1ª que tiver
    # a animação vale
    glbs = [Glb(ROOT / "extracted/gow1" / f) for f in conf.get("glbs", ["hero0/hero_obj.glb"]) if (ROOT / "extracted/gow1" / f).exists()]
    anims, owner = {}, {}
    for gi, gg in enumerate(glbs):
        for a in gg.j["animations"]:
            short = a["name"].split(" ")[-1]
            if short.upper() not in anims:
                anims[short.upper()] = short
                owner[short.upper()] = gi
    for k, v in conf.get("anim_alias", {}).items():
        if v.upper() in anims:
            anims[k] = v
            owner[k] = owner[v.upper()]
    excluded = tuple(conf.get("exclude_prefix", []))
    neutral_anims, fall_anims = set(conf["neutral_anims"]), set(conf["fall_anims"])
    evades = conf.get("evades", {})
    evade_ids = set(evades.values()) | set(conf.get("rage_evades", {}).values())

    def special(mid: int) -> int | None:
        """destino que não é golpe: parado, queda/aterrissagem (o DMC3 cuida) ou fora do motor"""
        if mid < 0:
            return mid
        a = graph[mid]["anim"] if mid in graph else ""
        if a in neutral_anims:
            return NEUTRAL
        if a in fall_anims:
            return FALL
        return None

    def usable(mid: int) -> bool:
        if mid not in graph or graph[mid]["anim"] not in anims:
            return False
        return not graph[mid]["anim"].startswith(excluded)

    def edges(mv: dict) -> list[dict]:
        return [t for t in mv["trans"] if not artemis_only(t["mask"]) and t["trigger"] in conf["triggers_used"]]

    # fecho do grafo a partir das raízes (parado no chão, no ar, na Rage), magias e esquivas: todos os gatilhos
    roots = [conf["ground_root"], conf["air_root"], conf["rage_ground_root"], conf["rage_air_root"]]
    order, kind = [], {}
    spell_ids = list(conf.get("spells", {}).values()) + list(conf.get("air_spells", {}).values())
    todo = [t["target"] for r in roots for t in edges(graph[r])] + spell_ids + sorted(evade_ids)
    for mid in spell_ids:
        kind[mid] = "spell"
    for mid in evade_ids:
        kind[mid] = "evade"
    while todo:
        mid = todo.pop(0)
        if mid in order or special(mid) is not None or not usable(mid):
            continue
        order.append(mid)
        grab = graph[mid]["anim"].startswith(tuple(conf.get("grab_prefix", [])))
        kind.setdefault(mid, "grab" if grab else "heavy" if graph[mid]["anim"] in conf.get("heavy", []) else "light")
        for t in edges(graph[mid]):
            if t["target"] not in order:
                todo.append(t["target"])
                if kind.get(mid) == "spell" and t["trigger"] == 0x0B:
                    kind.setdefault(t["target"], "spell")
    index = {mid: k for k, mid in enumerate(order)}

    def encode(t: dict) -> list | None:
        """[destino, gatilho, modo, início, fim, flags, nível]; modo do GoW1 (+0x1D): 1 apertou, 2 soltou, 3/4
        segurando, 5 solto (FUN_002072a0)"""
        to = special(t["target"])
        if to is None:
            to = index.get(t["target"])
        if to is None:
            return None
        return [to, t["trigger"], t["sub"], t["window"][0], t["window"][1], flags(t["mask"]), t["diff"]]

    def table(mid: int, execute_only: bool) -> list[list]:
        out = []
        for t in edges(graph[mid]):
            if execute_only and not t["mask"] & 1:
                continue
            if t["trigger"] in (0x0B, 0x0C, 0x13, 0x14) and t["target"] not in evade_ids:
                continue  # fim de animação e cancelamentos não valem no parado
            e = encode(t)
            if e is not None:
                out.append(e)
        return out

    cfg = kratos_fit.blade_cfg(yaml.safe_load((ROOT / "mapping/skeleton_kratos_dante.yaml").read_text(encoding="utf-8")))
    body = mod.Model.parse(pac.Pac.parse(model.read_bytes()).entries[1])
    _, parent = kratos_fit.dante_joints(body)
    offsets = blade_chain.blade_offsets(body)
    p = pac.Pac.parse(base_pac.read_bytes())
    template = mot.Motion.parse(next(e for e in p.entries if e and e[4:8] == b"MOT\0"))
    struct.pack_into("<f", template.header, 0x08, 0.0)  # play_start (cópia em 0x10): toca desde o 1º quadro
    struct.pack_into("<f", template.header, 0x10, 0.0)
    entries, info = [], []
    files: dict[tuple[str, bool], int] = {}  # a mesma animação em vários ids do GoW1 (ex.: BERCOMBOH4 ×6) = um arquivo
    for mid in order:
        mv = graph[mid]
        name = anims[mv["anim"]]
        g = glbs[owner[mv["anim"]]]
        reach = kind[mid] not in ("spell", "evade", "grab")
        anim = ar.KratosAnim(g, name)
        frames = max(int(anim.duration * 60) + 1, 2)
        base = mot.Motion(bytearray(template.header))
        base.frames = float(frames - 1)
        # o retarget só escreve rotação nos ossos que têm trilha de rotação na base (anim_retarget.py): sem elas o
        # corpo ficava na pose de repouso (Kratos em T no jogo, 2026-10-25)
        base.tracks = [t for t in template.tracks if t.bone != ar.ROOT_MOTION_BONE and t.channel[0] == "r"]
        root = zero_root(g, anim, frames, float(cfg["scale"]))
        if root is None:
            root = ([0.0] * frames, [0.0] * frames, [0.0] * frames)
        base.tracks += [mot.Track.linear(ar.ROOT_MOTION_BONE, "tx", root[0]),
                        mot.Track.linear(ar.ROOT_MOTION_BONE, "ty", root[1]),
                        mot.Track.linear(ar.ROOT_MOTION_BONE, "tz", root[2])]
        m = ar.retarget(g, name, body, cfg, frames, base, "natural")
        hit = ar.strike_frame(m, body, parent, frames)
        if mv["anim"] in conf.get("spell_hit", {}):
            hit = int(frames * conf["spell_hit"][mv["anim"]])
        if (name, reach) not in files:
            blade_chain.add_blade_tracks(m, offsets, body, parent, reach=reach)  # magia/esquiva: lâminas na mão
            for b in offsets:
                for ch in ("sx", "sy", "sz"):
                    m.tracks.append(mot.Track.hermite(b, ch, [1.0] * frames))
            files[(name, reach)] = len(entries)
            entries.append(m.build(pad=True))
        dmg = conf["damage"].get(mv["anim"], conf["damage"].get(kind[mid], conf["damage"]["default"]))
        trans = [e for e in (encode(t) for t in edges(mv)) if e is not None]
        air = any(t["mask"] & 4 for t in mv["trans"]) and not any(t["mask"] & 2 for t in mv["trans"])
        info.append({"name": mv["anim"], "gowId": mid, "file": files[(name, reach)], "frames": frames, "hitFrame": hit,
                     "damage": str(dmg),
                     "kind": kind[mid], "spell": conf.get("spell_fx", {}).get(mv["anim"], ""), "air": air,
                     "rise": round(max(root[1]), 1), "invuln": windows(mv, 28), "trans": trans,
                     # deslocamento por quadro (osso 0): no ar a DLL aplica sozinha (o evento de queda do DMC3 não aplica)
                     "root": [[round(root[0][f], 1), round(root[1][f], 1), round(root[2][f], 1)] for f in range(frames)]})
        print(f"#{index[mid]} {mv['anim']} (id {mid}, {frames} quadros, golpe {hit}, {kind[mid]}) "
              f"{len(trans)} transições, sobe {max(root[1]):.0f}")
    p.entries = entries
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(p.build())
    # um arquivo por golpe, com a motion no índice 0: o jogo trata os índices do grupo TAUNTS (0–3 no Dante) e
    # travou ao tocar o índice 6 (T85); a DLL troca o arquivo do grupo a cada golpe
    for k, e in enumerate(entries):
        single = pac.Pac.parse(base_pac.read_bytes())
        single.entries = [e]
        (out.parent / f"kratosMove{k:02d}_pl000_00_2.pac").write_bytes(single.build())
    doc = {"moves": info,
           "ground": table(conf["ground_root"], True), "air": table(conf["air_root"], False),
           "rageGround": table(conf["rage_ground_root"], True), "rageAir": table(conf["rage_air_root"], False),
           "spells": {n: index[m] for n, m in conf.get("spells", {}).items() if m in index},
           "airSpells": {n: index[m] for n, m in conf.get("air_spells", {}).items() if m in index},
           "evades": {n: index[m] for n, m in evades.items() if m in index},
           "rageEvades": {n: index[m] for n, m in conf.get("rage_evades", {}).items() if m in index}}
    (out.parent / "KratosMoves.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"{len(order)} golpes em {len(entries)} arquivos; parado: {len(doc['ground'])} transições, ar: {len(doc['air'])}")
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
