"""Instalador do modo Kratos (Windows nativo ou WSL): gera tudo a partir do jogo e da ISO do usuário e instala.

Uso: python -X utf8 tools/kratos_install.py <comando> [opções]
  all        bases → export → build → install (o que o setup.ps1 e o install.sh rodam)
  bases      junta os arquivos-base do DMC3/Crimson em work/backup/crimson_override (config/bases.sha256)
  export     extrai da ISO do GoW1 (god_of_war_browser) para extracted/gow1
  build      gera os arquivos do Kratos em work/install/release (ou --out)
  install    copia para o jogo: override, configs, efeitos, corpo, sons, HUD e Crimson.dll
  check      compara o que está no jogo com work/install/release
  restore    devolve os originais do Crimson (desinstala)
  sounds/hud só os sons ou só o HUD do GoW1 (parte do install)
Caminhos em config/paths.env; DMC_HD_DIR e GOW1_ISO podem vir de variáveis de ambiente.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

ROOT = paths.ROOT
P = paths.load()
GAME = Path(P["DMC_HD_DIR"])
NBZ = Path(P["DMC3_NBZ"])
ISO = Path(P["GOW1_ISO"])
OVERRIDE = GAME / "data/dmc3/GData.afs"
CRIMSON = GAME / "Crimson"
BACKUP = ROOT / "work/backup/crimson_override"
RELEASE = ROOT / "work/install/release"
G = ROOT / "extracted/gow1"
U = ROOT / "extracted/dmc3/unpacked"
REPO = "https://github.com/Subbr/kratos-dmc3"
EXE_SHA = "e454272ed0fb0247fcbcf300e5d55d7a3e96d50b89b9ffaff81bb978dcbdd082"
OURS = {"id7168.pac"}  # arquivos só nossos: nunca viram "original do Crimson" no backup (T77)
GOWB = ROOT / "vendor/gowb_bin" / ("god_of_war_browser.exe" if os.name == "nt" else "god_of_war_browser")
GOWB_URL = "http://127.0.0.1:8000"


def step(t: str) -> None:
    print(f"\n== {t}", flush=True)


def die(t: str) -> None:
    sys.exit(f"\nERRO: {t}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def py(*args: object) -> None:
    """Roda uma ferramenta Python do projeto com o mesmo interpretador."""
    subprocess.run([sys.executable, "-I", "-X", "utf8", *map(str, args)], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)


def nbz_read(name: str) -> bytes:
    with zipfile.ZipFile(NBZ) as z:
        return z.read(f"GData.afs/{name}")


def unpack(pac: Path, name: str) -> Path:
    d = U / name
    if not d.is_dir():
        py("tools/pac.py", "unpack", pac, d)
    return d


# --- bases ---------------------------------------------------------------------------------------------------------
def cmd_bases() -> None:
    step("arquivos-base do DMC3/Crimson")
    BACKUP.mkdir(parents=True, exist_ok=True)
    bad = []
    for line in (ROOT / "config/bases.sha256").read_text(encoding="utf-8").splitlines():
        want, name = line.split()
        dst = BACKUP / name
        if dst.is_file() and sha(dst) == want:
            continue
        src = GAME / "Crimson.dll" if name == "Crimson.dll.release-0.5a" else OVERRIDE / name
        if src.is_file() and sha(src) == want:
            shutil.copy2(src, dst)
            continue
        try:
            data = nbz_read(name)
        except KeyError:
            data = b""
        if hashlib.sha256(data).hexdigest() == want:
            dst.write_bytes(data)
            continue
        bad.append(name)
    if bad:
        die(f"{len(bad)} arquivo(s)-base faltando ou diferentes ({', '.join(bad[:5])}...). O Crimson 0.5a precisa estar "
            "instalado e a pasta data/dmc3/GData.afs ainda sem arquivos de outro mod.")
    print("bases ok")


# --- export --------------------------------------------------------------------------------------------------------
def get(path: str) -> bytes:
    return urllib.request.urlopen(GOWB_URL + path, timeout=600).read()


def tags(wad: str) -> dict[str, int]:
    d = json.loads(get(f"/json/pack/{wad}"))
    nodes = d["Nodes"].values() if isinstance(d["Nodes"], dict) else d["Nodes"]
    return {n["Tag"]["Name"]: n["Tag"]["Id"] for n in nodes}


def gowb_up() -> bool:
    try:
        urllib.request.urlopen(GOWB_URL + "/json/pack", timeout=5)
        return True
    except OSError:
        return False


def cmd_export(out: Path = G) -> None:
    step("assets do GoW1 a partir da ISO (~4 min)")
    import yaml
    if not GOWB.is_file():
        die(f"god_of_war_browser não compilado em {GOWB}")
    proc = None
    if not gowb_up():
        proc = subprocess.Popen([str(GOWB), "-iso", str(ISO), "-ps", "ps2", "-gowversion", "1", "-i", "127.0.0.1:8000"],
                                cwd=ROOT / "vendor/god_of_war_browser", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(90):
            if gowb_up():
                break
            time.sleep(2)
        else:
            die("god_of_war_browser não respondeu")
    try:
        for sub in ("hero0", "weapons", "sound/hero", "sound/general", "sound/magic", "sound/all", "hud", "magic", "twk",
                    "flp", "finishers"):
            (out / sub).mkdir(parents=True, exist_ok=True)

        def save(rel: str, data: bytes) -> None:
            (out / rel).write_bytes(data)
        # modelos: (WAD, tag, arquivo)
        for wad, name, dst in [("R_HERO0.WAD", "hero", "hero0/hero_obj.glb"),
                               ("R_WPN0_0.WAD", "maiblade", "weapons/maiblade.glb"),
                               ("R_WPN0_0.WAD", "maigodblade", "weapons/maigodblade.glb"),
                               ("ATHN08C.WAD", "athenablade", "weapons/athenablade.glb")]:
            save(dst, get(f"/action/{wad}/{tags(wad)[name]}/gltf"))
        # modelos das magias (mapping/magic_fx.yaml → tools/build_fx.py), pelo número da tag
        fx = yaml.safe_load((ROOT / "mapping/magic_fx.yaml").read_text(encoding="utf-8"))
        for n, m in fx["models"].items():
            save(f"magic/{n}.glb", get(f"/action/{m['wad']}/{m['tag']}/gltf"))
        st = fx["stone"]
        img = json.loads(get(f"/json/pack/{st['wad']}/{st['tag']}"))["Data"]["Images"][0]["Image"]
        save("magic/Maitext01Stone.png", base64.b64decode(img))
        # vozes (banco "Hero") e sons de combate (banco "GENERAL", inteiro: T95) do R_PERM
        t = tags("R_PERM.WAD")
        for s in json.loads(get(f"/json/pack/R_PERM.WAD/{t['Hero']}"))["Data"]["Sounds"]:
            save(f"sound/hero/{s['Name']}.wav", get(f"/action/R_PERM.WAD/{t['Hero']}/wav?snd={s['Name']}"))
        gen = json.loads(get(f"/json/pack/R_PERM.WAD/{t['GENERAL']}"))["Data"]
        for s in gen["Sounds"]:
            seen, k = set(), 0
            for c in gen["Bank"]["BankSounds"][s["StreamId"]]["Commands"]:
                r = c.get("SampleRef")
                if not r or (r["AdpcmOffset"], r["AdpcmSize"]) in seen:
                    continue
                seen.add((r["AdpcmOffset"], r["AdpcmSize"]))
                save(f"sound/general/{s['Name']}_{k}.wav",
                     get(f"/action/R_PERM.WAD/{t['GENERAL']}/smpd?offset={r['AdpcmOffset']}&size={r['AdpcmSize']}"))
                k += 1
        # sons soltos na ISO: magia (T58) e vozes usadas por install_sounds (T79)
        for name in ("POSMAG06.VAG", "RAGEMIME.VAG"):
            save(f"sound/magic/{name[:-4]}.wav", get(f"/dump/pack/{name}/wav"))
        for name in ("STAINVOC.VAG", "PUSHGRNT.VAG", "A01HL17.VPK", "A08HL02A.VAG"):
            save(f"sound/all/{name.replace('.', '_')}.wav", get(f"/dump/pack/{name}/wav"))
        # tabelas de combate do GoW1 (D11, docs/formats/gow-combat.md)
        for name, tid in t.items():
            if re.match(r"TWK_(CombatFile_\d+|CombatFileSet_000|Player)$", name):
                save(f"twk/{name[4:]}.json", get(f"/json/pack/R_PERM.WAD/{tid}"))
        save("twk/goHero.json", get(f"/json/pack/R_HERO0.WAD/{tags('R_HERO0.WAD')['TWK_goHero']}"))
        # HUD: TXR_HUD* e o filme FLP_HUD com a malha HUD_0 (T94)
        for name, tid in t.items():
            if re.match(r"TXR_HUD\d+$", name):
                imgs = (json.loads(get(f"/json/pack/R_PERM.WAD/{tid}")).get("Data") or {}).get("Images") or []
                if imgs:
                    save(f"hud/{name}.png", base64.b64decode(imgs[0]["Image"]))
        for name in ("FLP_HUD", "HUD_0"):
            save(f"flp/{name}.json", get(f"/json/pack/R_PERM.WAD/{t[name]}"))
        # finalizações do agarrão (T93): só o gowb do fork (carregador ?anm=WAD:tag) exporta
        hero = tags("R_HERO0.WAD")["hero"]
        data = get(f"/action/R_HERO0.WAD/{hero}/gltf?anm=R_SKA.WAD:{tags('R_SKA.WAD')['ANM_MAISKA']}")
        if b"maiSka" in data or len(data) > 10_400_000:
            save("finishers/maiSka.glb", data)
        else:
            print("gowb sem o carregador de ANM externo: finalizações não exportadas")
    finally:
        if proc:
            proc.terminate()
    print("export ok")


# --- build ---------------------------------------------------------------------------------------------------------
def find_blender() -> Path | None:
    cands = [P.get("BLENDER_EXE", "")]
    for base in ("C:/Program Files/Blender Foundation", "/mnt/c/Program Files/Blender Foundation"):
        cands += sorted(map(str, Path(base).glob("Blender */blender.exe")), reverse=True) if Path(base).is_dir() else []
    return next((Path(c) for c in cands if c and Path(c).is_file()), None)


def native(p: Path) -> str:
    """Caminho que um .exe do Windows entende (no WSL, via wslpath)."""
    if os.name == "nt":
        return str(p)
    return subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True, check=True).stdout.strip()


def render_menu_art() -> bool:
    m = ROOT / "work/install/menu_art"
    if (m / "renders/blades_title.png").is_file():
        return True
    blender = find_blender()
    if not blender:
        print("Blender não encontrado: artes de menu ficam as do Crimson")
        return False
    (m / "glb").mkdir(parents=True, exist_ok=True)
    (m / "renders").mkdir(parents=True, exist_ok=True)
    glb = m / "glb/kratos_blades.glb"
    py("tools/glb_add_weapon.py", G / "hero0/hero_obj.glb", G / "weapons/maiblade.glb", glb, "--flip-edge")
    for out, anim, frac, side, ang in [("blades_title", "idleCombat2", "0.5", "1400", "25"),
                                       ("blades_load", "boltThrow", "0.35", "1200", "25"),
                                       ("blades_menu", "idleCombat", "0.3", "1000", "35"),
                                       ("blades_end", "idleCombat2", "0.5", "800", "25")]:
        r = subprocess.run([str(blender), "-b", "-P", native(ROOT / "blender/scripts/render_kratos.py"), "--", native(glb),
                            native(m / "renders") + "\\" + out + ".png", anim, frac, side, side, ang],
                           capture_output=True, text=True)
        if not any(line.startswith("ok") for line in r.stdout.splitlines()):
            print(f"render falhou ({out}): artes de menu ficam as do Crimson")
            return False
    return True


def cmd_build(out: Path = RELEASE) -> None:
    step("build dos arquivos do Kratos (~1 min)")
    out.mkdir(parents=True, exist_ok=True)
    B = BACKUP
    glb, blade = G / "hero0/hero_obj.glb", G / "weapons/maiblade.glb"
    fit = ["--both-hands", "--blade-bones", "--flip-edge"]
    # Dante original do jogo (sem Crimson): esqueleto de referência de tools/build_motions.py
    if not (U / "pl000").is_dir():
        U.mkdir(parents=True, exist_ok=True)
        (U / "pl000.pac").write_bytes(nbz_read("pl000.pac"))
        unpack(U / "pl000.pac", "pl000")
        (U / "pl000.pac").unlink()
    # 1. corpo e roupas do Kratos (T3–T10, T41–T42)
    py("tools/kratos_fit.py", glb, unpack(B / "pl000.pac", "crimson_pl000"), out / "pl000.pac", "--left-weapon", blade, *fit)
    for n in ("pl011", "pl013", "pl015", "pl016", "pl018"):
        py("tools/kratos_fit.py", glb, unpack(B / f"{n}.pac", f"base_{n}"), out / f"{n}.pac", "--left-weapon", blade, *fit)
    # 2. Devil Trigger dourado em todas as armas, Blades em brasa do GoW1 (T22, T32, T60)
    for n in ("pl005", "pl006", "pl007", "pl008", "pl009", "pl017"):
        d = unpack(B / f"{n}.pac", f"crimson_{n}")
        hide = ",".join(sorted(f for f in os.listdir(d) if "MOD" in f and not f.startswith("001")))
        py("tools/kratos_fit.py", glb, d, out / f"{n}.pac", "--left-weapon", G / "weapons/maigodblade.glb", *fit,
           "--hide", hide, "--tint", "1,0.75,0.2,0.35")
    # 3. armas: Artemis no slot Agni & Rudra (T26); as do Dante escondidas (T8, T45, T49, T50)
    py("tools/weapon_fit.py", G / "weapons/athenablade.glb", unpack(B / "plwp_2sword.pac", "crimson_plwp_2sword"),
       out / "plwp_2sword.pac")
    for n in ("plwp_sword", "plwp_sword2", "plwp_sword3", "plwp_gun", "plwp_shotgun", "plwp_laser", "plwp_rifle",
              "plwp_grenade", "plwp_nunchaku", "plwp_guitar", "plwp_fight"):
        py("tools/hide_models.py", B / f"{n}.pac", out / f"{n}.pac")
    # 4. motions, motor Kratos (D11), efeitos das magias e corpo desenhado pela DLL (T98)
    py("tools/build_motions.py", B, out, "--model", out / "pl000.pac")
    py("tools/build_fx.py", G / "magic", out / "kratos_fx")
    py("tools/build_engine_moves.py", B / "pl000_00_2.pac", out / "pl000.pac", out / "kratosMoves_pl000_00_2.pac")
    py("tools/build_body.py", glb, blade, out / "kratos_body/kratos.kbd")
    # 5. textos (T38) e 6. artes dos menus (T59, T77; precisa do Blender)
    py("tools/build_text.py", B / "msg_eng.pac", out / "msg_eng.pac")
    if render_menu_art():
        py("tools/build_menu_art.py", out)
        for f in out.glob("*.preview.png"):
            f.unlink()
    print(f"pronto: {len(list(out.iterdir()))} arquivos em {out}")


# --- install / check / restore ------------------------------------------------------------------------------------
def same(a: Path, b: Path) -> bool:
    return b.is_file() and a.stat().st_size == b.stat().st_size and a.read_bytes() == b.read_bytes()


def pairs() -> list[tuple[Path, Path]]:
    """(arquivo gerado, destino no jogo) de tudo o que o modo Kratos instala a partir de work/install/release."""
    out = [(f, OVERRIDE / f.name) for f in sorted(RELEASE.glob("*.pac"))]
    out.append((RELEASE / "KratosMoves.json", CRIMSON / "configs/KratosMoves.json"))
    out.append((RELEASE / "kratos_body/kratos.kbd", CRIMSON / "kratos_body/kratos.kbd"))
    out += [(f, CRIMSON / "kratos_fx" / f.name) for f in sorted((RELEASE / "kratos_fx").glob("*.kfx"))]
    out.append((RELEASE / "kratos_fx/stone.png", CRIMSON / "kratos_fx/stone.png"))
    return out


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def install_sounds() -> None:
    """Sons do GoW1 em Crimson\\sound\\kratos\\<evento>_<n>.wav, nomes lidos por KratosSound.cpp (T31, T79, T95)."""
    S, D = G / "sound", CRIMSON / "sound/kratos"
    shutil.rmtree(D, ignore_errors=True)
    D.mkdir(parents=True)

    def files(*pats: str) -> list[Path]:
        return [f for p in pats for f in sorted(S.glob(p))]

    def put(event: str, *pats: str, dst: Path = D) -> None:
        for n, f in enumerate(files(*pats)):
            shutil.copy2(f, dst / f"{event}_{n}.wav")
    put("swing", "general/SND_WHOOSHMID_FAST_*.wav", "general/SND_WHOOSHMID_MEDIUM_*.wav", "general/SND_CHAINSNAP_A_*.wav")
    put("voice_short", "hero/H_ATTKS[1-4].wav")
    put("voice_long", "hero/H_ATTKL[12].wav")
    put("hit", "general/SND_SWORDHIT_CHEST_*.wav", "general/SND_ENEMY_GETHIT_S_*.wav")
    put("gun_hit", "general/SND_BOLT_HIT_*.wav")
    put("hurt", "hero/H_DMG[1-6].wav")
    put("die", "hero/DIEVOC1.wav")
    put("jump", "hero/JUMPVOC[12].wav")
    put("medusa_shot", "general/SND_MEDUSA_RAY_SHOT_*.wav")
    put("stone", "general/SND_MEDUSA_TURNTOSTONE_*.wav")
    put("flesh", "general/SND_MEDUSA_TURNTOFLESH_*.wav")
    put("block", "general/SND_BLADEBLOCK_*.wav")
    put("step_walk", "general/SND_FOOTSTEP_STONEWALK_*.wav")
    put("step_run", "general/SND_FOOTSTEP_STONERUN_*.wav")
    put("land", "general/SND_FOOTSTEP_STONELAND_*.wav")
    # RAGEMIME/POSMAG06 são narração (T79): trocados pelos sons de jogo
    put("rage", "all/STAINVOC_VAG.wav")  # [HIPÓTESE: voz do Kratos, conferir de ouvido]
    put("rage_fx", "general/SND_TRANSFORM_LP_0.wav")
    put("poseidon", "general/SND_LIGHTNING360_START_0.wav", "general/SND_LIGHTNING360_BOLT_1.wav")
    put("zeus", "general/SND_BOLT_FIRE_0.wav")
    put("hades", "general/SND_RAISEDEAD_SHOT_0.wav")
    put("grab", "all/PUSHGRNT_VAG.wav", "general/SND_KICKCHARGEVO_LP_0.wav", "general/SND_MAI_STRUGGLEVO_LP_3.wav")
    # falas do Kratos no começo da luta com chefe, recortadas do áudio original (regra 5)
    (S / "cut").mkdir(exist_ok=True)
    for src, start, dur, dst in [("A01HL17_VPK", 0, 5.3, "boss_hades"), ("A08HL02A_VAG", 5.1, 2.2, "boss_demons")]:
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(S / f"all/{src}.wav"), "-ss", str(start), "-t", str(dur),
                        "-ac", "1", "-af", f"afade=t=out:st={dur - 0.25:g}:d=0.25", str(S / f"cut/{dst}.wav")], check=True)
    put("boss_start", "cut/boss_hades.wav", "cut/boss_demons.wav")
    # T95: banco GENERAL inteiro em sfx\ e as vozes do Hero com os nomes de evento da tabela de combate
    X = D / "sfx"
    X.mkdir()
    for f in files("general/*.wav"):
        shutil.copy2(f, X / f.name)
    for events, pat in [(("SND_HERO_ATTKVOC_SHORT", "SND_HERO_ATKVOC_SHORT_A"), "hero/H_ATTKS[1-4].wav"),
                        (("SND_HERO_ATTKVOC_LONG", "SND_HERO_ATKVOC_LONG_A"), "hero/H_ATTKL[12].wav"),
                        (("SND_HERO_GETHITVOC", "SND_HERO_GETHITVOC_A"), "hero/H_DMG[1-6].wav"),
                        (("SND_HERO_DIEVOC",), "hero/DIEVOC1.wav")]:
        for e in events:
            put(e, pat, dst=X)


def install_hud() -> None:
    """Arte do HUD do GoW1 em Crimson\\huds\\kratos (nomes lidos por KratosMode::OnGUI) e o filme FLP_HUD (T94)."""
    S, D = G / "hud", CRIMSON / "huds/kratos"
    D.mkdir(parents=True, exist_ok=True)
    for src, dst in [("029", "frame"), ("014", "poseidon"), ("015", "medusa"), ("016", "zeus"), ("017", "hades"),
                     ("019", "fill"), ("013", "orb"), ("004", "rage_cap"), ("003", "rage_bar"), ("036", "boss_cap"),
                     ("037", "boss_bar")]:
        shutil.copy2(S / f"TXR_HUD{src}.png", D / f"{dst}.png")
    if (G / "flp/FLP_HUD.json").is_file():
        py("tools/build_hud.py", G / "flp", D / "flp")


def dll_path() -> Path:
    return ROOT / "dll/crimson/build/bin/Release/Crimson.dll"


def cmd_install() -> None:
    step("instalação no jogo")
    for src, dst in pairs():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if (dst.parent == OVERRIDE and dst.is_file() and not (BACKUP / dst.name).is_file() and dst.name not in OURS
                and not dst.name.startswith("kratosMove") and not same(src, dst)):
            print(f"sem backup de {dst.name} (original do Crimson?): guardando em {BACKUP}")
            shutil.copy2(dst, BACKUP / dst.name)
        shutil.copy2(src, dst)
    cfg = CRIMSON / "configs/KratosConfig.json"
    if not cfg.is_file():
        shutil.copy2(ROOT / "config/KratosConfig.default.json", cfg)
        print("KratosConfig.json instalado (padrão)")
    step("sons e HUD do GoW1")
    install_sounds()
    install_hud()
    step("Crimson.dll do modo Kratos")
    dll = Path(os.environ["KRATOS_DLL"]) if os.environ.get("KRATOS_DLL") else dll_path()
    if not dll.is_file():
        dll.parent.mkdir(parents=True, exist_ok=True)
        print("baixando a DLL da página de Releases")
        urllib.request.urlretrieve(f"{REPO}/releases/latest/download/Crimson.dll", dll)
    bk = BACKUP / "Crimson.dll.release-0.5a"
    if not bk.is_file():
        shutil.copy2(GAME / "Crimson.dll", bk)
    shutil.copy2(dll, GAME / "Crimson.dll")


def cmd_check() -> int:
    diff = [s.name for s, d in pairs() if not same(s, d)]
    for n in diff:
        print("difere:", n)
    print(f"{len(diff)} arquivo(s) diferente(s)")
    return len(diff)


def cmd_restore() -> None:
    for src, dst in pairs():
        if dst.parent == OVERRIDE and (BACKUP / dst.name).is_file():
            shutil.copy2(BACKUP / dst.name, dst)
        elif dst.is_file():
            dst.unlink()
    for d in ("kratos_body", "kratos_fx", "sound/kratos", "huds/kratos"):
        shutil.rmtree(CRIMSON / d, ignore_errors=True)
    if (BACKUP / "Crimson.dll.release-0.5a").is_file():
        shutil.copy2(BACKUP / "Crimson.dll.release-0.5a", GAME / "Crimson.dll")
    print("desinstalado: arquivos e DLL originais do Crimson de volta")


def preflight() -> None:
    step("jogo, Crimson e ISO")
    if not (GAME / "dmc3.exe").is_file():
        die(f"jogo não encontrado em {GAME}")
    if not (GAME / "Crimson.dll").is_file():
        die("Crimson 0.5a não instalado no jogo (github.com/berthrage/DMC3-Crimson/releases/tag/V0.5a)")
    if not ISO.is_file():
        die(f"ISO do God of War (NTSC-U SCUS_973.99) não encontrada em {ISO}")
    if sha(GAME / "dmc3.exe") != EXE_SHA:
        print("AVISO: dmc3.exe diferente do testado (docs/ambiente.md); o Crimson 0.5a instalado deveria gerar esse exe.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["all", "bases", "export", "build", "install", "check", "restore", "sounds", "hud"])
    ap.add_argument("--out", type=Path, help="pasta de saída de export/build")
    a = ap.parse_args()
    if a.command == "all":
        preflight()
        cmd_bases()
        if not (G / "twk/goHero.json").is_file():
            cmd_export()
        cmd_build()
        cmd_install()
        print(f"\nPronto! Abra o Devil May Cry 3 pela Steam. Desinstalar: {Path(sys.argv[0]).name} restore")
    elif a.command == "bases":
        cmd_bases()
    elif a.command == "export":
        cmd_export(a.out or G)
    elif a.command == "build":
        cmd_build(a.out or RELEASE)
    elif a.command == "install":
        cmd_install()
    elif a.command == "sounds":
        install_sounds()
    elif a.command == "hud":
        install_hud()
    elif a.command == "check":
        sys.exit(1 if cmd_check() else 0)
    else:
        cmd_restore()


if __name__ == "__main__":
    main()
