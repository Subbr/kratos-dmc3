#!/usr/bin/env bash
# Baixa (ou atualiza) o repositório em ~/kratos-dmc3, liga a pasta do jogo e a ISO e roda o install.sh.
# Chamado pelo setup.ps1; também funciona sozinho no WSL:
#   curl -fsSL https://raw.githubusercontent.com/Subbr/kratos-dmc3/main/tools/bootstrap.sh | bash -s -- "<pasta do jogo>" "<ISO>"
# Os caminhos podem ser do Windows (C:\...) ou do WSL (/mnt/c/...).
set -eu
GAME=${1:?pasta do Devil May Cry HD Collection}; ISO=${2:?ISO do God of War}
DIR=${KRATOS_DIR:-$HOME/kratos-dmc3}
to_wsl() { case $1 in [A-Za-z]:*) wslpath -u "$1" ;; *) echo "$1" ;; esac; }
GAME=$(to_wsl "$GAME"); ISO=$(to_wsl "$ISO")
[ -f "$GAME/dmc3.exe" ] || { echo "ERRO: não achei dmc3.exe em $GAME"; exit 1; }
[ -f "$ISO" ] || { echo "ERRO: não achei a ISO $ISO"; exit 1; }

if [ -d "$DIR/.git" ]; then git -C "$DIR" pull -q --ff-only
else git clone -q --depth 1 https://github.com/Subbr/kratos-dmc3.git "$DIR"; fi
cd "$DIR"
# o mod é instalado direto na pasta do jogo (backups em work/backup; desfazer: ./install.sh --restore)
[ -e "Devil May Cry HD Collection" ] || ln -s "$GAME" "Devil May Cry HD Collection"
mkdir -p iso && ln -sfn "$ISO" iso/gow1.iso
./install.sh
