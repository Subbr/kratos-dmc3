#!/usr/bin/env bash
# Instalação completa do modo Kratos a partir do jogo e da ISO do próprio usuário (nenhum asset vem no repo).
# Passo a passo e pré-requisitos: docs/INSTALACAO.md.
# Uso (no WSL, na raiz do repo):
#   ./install.sh            tudo: checagem, venv, bases, extração do GoW1, build, instalação, DLL
#   ./install.sh --check    só compara o que está instalado com work/install/release
#   ./install.sh --restore  devolve os arquivos originais do Crimson (desinstala)
set -eu
cd "$(dirname "$0")"
source config/paths.env
step() { printf '\n== %s\n' "$*"; }
die() { echo "ERRO: $*"; exit 1; }

case ${1:-} in
  --check) exec tools/install_all.sh --check ;;
  --restore) tools/install_all.sh --restore; tools/win/install_crimson_dll.sh restore
             rm -rf "$DMC_HD_DIR/Crimson/sound/kratos" "$DMC_HD_DIR/Crimson/huds/kratos"; echo "desinstalado"; exit ;;
esac

step "1/7 pré-requisitos"
[ -f "$DMC3_EXE" ] || die "jogo não encontrado em '$DMC_HD_DIR' (copie a pasta do DMC HD Collection para a raiz do repo)"
[ -f "$DMC_HD_DIR/Crimson.dll" ] || die "Crimson 0.5a não instalado no jogo (github.com/berthrage/DMC3-Crimson/releases)"
[ -f "$GOW1_ISO" ] || die "ISO do God of War (NTSC-U SCUS_973.99) não encontrada em $GOW1_ISO"
[ -x vendor/gowb_bin/god_of_war_browser ] || die "god_of_war_browser não compilado em vendor/gowb_bin (docs/INSTALACAO.md, passo 3)"
command -v unzip >/dev/null || die "instale o unzip (sudo apt install unzip)"

step "2/7 ambiente Python (tools/.venv)"
[ -x tools/.venv/bin/python ] || python3 -m venv tools/.venv
tools/.venv/bin/pip install -q -r requirements.txt

step "3/7 arquivos-base do DMC3/Crimson"
tools/prepare_bases.sh

step "4/7 assets do GoW1 a partir da ISO (~4 min)"
[ -f extracted/gow1/hero0/hero_obj.glb ] || tools/export_gow1.sh

step "5/7 build dos arquivos do Kratos (~1 min)"
tools/build_all.sh work/install/release

step "6/7 instalação no override, sons e HUD"
tools/install_all.sh
tools/install_sounds.sh >/dev/null
tools/install_hud.sh >/dev/null

step "7/7 Crimson.dll do fork (modo Kratos)"
if [ ! -f dll/crimson/build/bin/Release/Crimson.dll ]; then
  mkdir -p dll/crimson/build/bin/Release
  if [ -f "${KRATOS_DLL:-}" ]; then cp "$KRATOS_DLL" dll/crimson/build/bin/Release/Crimson.dll
  elif command -v cmd.exe >/dev/null && [ -f dll/crimson/CMakeLists.txt ]; then cmd.exe /c 'tools\win\build_crimson.bat configure'
  else die "sem Crimson.dll: baixe da página de Releases e rode KRATOS_DLL=/caminho/Crimson.dll ./install.sh"; fi
fi
tools/win/install_crimson_dll.sh
echo; echo "Pronto. Abra o jogo pelo dmcLauncher.exe / dmc3.exe da pasta '$DMC_HD_DIR'."
