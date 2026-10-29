#!/usr/bin/env bash
# Instalação completa do modo Kratos a partir do jogo e da ISO do próprio usuário (nenhum asset vem no repo).
# Jeito mais simples: setup.ps1 (Windows) chama este script. Passo a passo manual: docs/INSTALACAO.md.
# Uso (no WSL, na raiz do repo):
#   ./install.sh            tudo: dependências, bases, extração do GoW1, build, instalação, DLL
#   ./install.sh --check    só compara o que está instalado com work/install/release
#   ./install.sh --restore  devolve os arquivos originais do Crimson (desinstala)
# Dependências baixadas sem sudo: Python 3.12 (uv), Go (go.dev), ffmpeg (imageio-ffmpeg), DLL (Releases).
set -eu
cd "$(dirname "$0")"
source config/paths.env
REPO=https://github.com/Subbr/kratos-dmc3
GOWB=https://github.com/Subbr/god_of_war_browser.git
GO_VER=1.22.12
EXE_SHA=e454272ed0fb0247fcbcf300e5d55d7a3e96d50b89b9ffaff81bb978dcbdd082
step() { printf '\n== %s\n' "$*"; }
die() { echo; echo "ERRO: $*"; exit 1; }
export PATH="$PWD/tools/.venv/bin:$HOME/.local/bin:$PATH"

case ${1:-} in
  --check) exec tools/install_all.sh --check ;;
  --restore) tools/install_all.sh --restore; tools/win/install_crimson_dll.sh restore
             rm -rf "$DMC_HD_DIR/Crimson/sound/kratos" "$DMC_HD_DIR/Crimson/huds/kratos"; echo "desinstalado"; exit ;;
esac

step "1/8 jogo, Crimson e ISO"
[ -f "$DMC3_EXE" ] || die "jogo não encontrado em '$DMC_HD_DIR' (link ou cópia da pasta do DMC HD Collection)"
[ -f "$DMC_HD_DIR/Crimson.dll" ] || die "Crimson 0.5a não instalado no jogo (github.com/berthrage/DMC3-Crimson/releases/tag/V0.5a)"
[ -f "$GOW1_ISO" ] || die "ISO do God of War (NTSC-U SCUS_973.99) não encontrada em $GOW1_ISO"
[ "$(sha256sum < "$DMC3_EXE" | cut -c1-64)" = "$EXE_SHA" ] ||
  echo "AVISO: dmc3.exe diferente do testado (docs/ambiente.md). O Crimson 0.5a instalado deveria gerar esse exe."

step "2/8 dependências (sem sudo)"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
if [ ! -x tools/.venv/bin/python ]; then
  uv venv -q --python 3.12 tools/.venv
fi
uv pip install -q --python tools/.venv/bin/python -r requirements.txt
if ! command -v ffmpeg >/dev/null; then
  uv pip install -q --python tools/.venv/bin/python imageio-ffmpeg
  ln -sf "$(tools/.venv/bin/python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" tools/.venv/bin/ffmpeg
fi
if [ ! -x vendor/gowb_bin/god_of_war_browser ]; then
  GO=$(command -v go || true)
  if [ -z "$GO" ]; then
    mkdir -p vendor && curl -LsS "https://go.dev/dl/go$GO_VER.linux-amd64.tar.gz" | tar -xz -C vendor
    GO=$PWD/vendor/go/bin/go
  fi
  [ -d vendor/god_of_war_browser ] || git clone -q --depth 1 -b kratos "$GOWB" vendor/god_of_war_browser
  (cd vendor/god_of_war_browser && "$GO" build -o ../gowb_bin/god_of_war_browser .)
fi

step "3/8 arquivos-base do DMC3/Crimson"
tools/prepare_bases.sh

step "4/8 assets do GoW1 a partir da ISO (~4 min)"
[ -f extracted/gow1/hero0/hero_obj.glb ] || tools/export_gow1.sh

step "5/8 build dos arquivos do Kratos (~1 min)"
tools/build_all.sh work/install/release

step "6/8 instalação no jogo"
tools/install_all.sh

step "7/8 sons e HUD do GoW1"
tools/install_sounds.sh >/dev/null
tools/install_hud.sh >/dev/null

step "8/8 Crimson.dll do modo Kratos"
DLL=dll/crimson/build/bin/Release/Crimson.dll
if [ -f "${KRATOS_DLL:-}" ]; then mkdir -p "$(dirname "$DLL")"; cp "$KRATOS_DLL" "$DLL"
elif [ ! -f "$DLL" ]; then
  if [ -f dll/crimson/CMakeLists.txt ] && command -v cmd.exe >/dev/null && [ -n "${KRATOS_BUILD_DLL:-}" ]; then
    cmd.exe /c 'tools\win\build_crimson.bat configure'
  else
    mkdir -p "$(dirname "$DLL")"
    curl -fLsS -o "$DLL" "$REPO/releases/latest/download/Crimson.dll" || die "não consegui baixar a DLL de $REPO/releases"
  fi
fi
tools/win/install_crimson_dll.sh >/dev/null
echo; echo "Pronto! Abra o Devil May Cry 3 pela Steam (ou dmc3.exe). Desinstalar: ./install.sh --restore"
