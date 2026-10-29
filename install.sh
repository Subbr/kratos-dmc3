#!/usr/bin/env bash
# Instalação completa do modo Kratos a partir do jogo e da ISO do próprio usuário (nenhum asset vem no repo).
# Para quem só quer jogar: setup.ps1 (Windows, sem WSL). Este é o caminho de desenvolvedor no WSL.
# Uso (no WSL, na raiz do repo):
#   ./install.sh            dependências + tools/kratos_install.py all (bases, extração, build, instalação, DLL)
#   ./install.sh --check    só compara o que está instalado com work/install/release
#   ./install.sh --restore  devolve os arquivos originais do Crimson (desinstala)
# Dependências baixadas sem sudo: Python 3.12 (uv), Go (go.dev), ffmpeg (imageio-ffmpeg), DLL (Releases).
set -eu
cd "$(dirname "$0")"
GOWB=https://github.com/Subbr/god_of_war_browser.git
GO_VER=1.22.12
step() { printf '\n== %s\n' "$*"; }
export PATH="$PWD/tools/.venv/bin:$HOME/.local/bin:$PATH"

case ${1:-} in
  --check) exec tools/install_all.sh --check ;;
  --restore) exec tools/install_all.sh --restore ;;
esac

step "dependências (sem sudo)"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
if [ ! -x tools/.venv/bin/python ]; then
  uv venv -q --python 3.12 tools/.venv
fi
uv pip install -q --python tools/.venv/bin/python -r requirements.txt
if [ ! -x vendor/gowb_bin/god_of_war_browser ]; then
  GO=$(command -v go || true)
  if [ -z "$GO" ]; then
    mkdir -p vendor && curl -LsS "https://go.dev/dl/go$GO_VER.linux-amd64.tar.gz" | tar -xz -C vendor
    GO=$PWD/vendor/go/bin/go
  fi
  [ -d vendor/god_of_war_browser ] || git clone -q --depth 1 -b kratos "$GOWB" vendor/god_of_war_browser
  (cd vendor/god_of_war_browser && "$GO" build -o ../gowb_bin/god_of_war_browser .)
fi

tools/.venv/bin/python -X utf8 tools/kratos_install.py all
