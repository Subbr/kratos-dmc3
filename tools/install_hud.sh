#!/usr/bin/env bash
# Copia a arte do HUD do GoW1 (extracted/gow1/hud, god_of_war_browser: R_PERM.WAD TXR_HUD*) para
# Crimson\huds\kratos (fora do git), nomes lidos por KratosMode::OnGUI. Uso: tools/install_hud.sh
set -e
cd "$(dirname "$0")/.."
S=extracted/gow1/hud
D="Devil May Cry HD Collection/Crimson/huds/kratos"
mkdir -p "$D"
cp $S/TXR_HUD029.png "$D/frame.png"      # lâmina da Blade of Chaos (vida e magia) com o medalhão (Rage)
cp $S/TXR_HUD014.png "$D/poseidon.png"   # ícones das magias
cp $S/TXR_HUD015.png "$D/medusa.png"
cp $S/TXR_HUD016.png "$D/zeus.png"
cp $S/TXR_HUD017.png "$D/hades.png"
ls "$D"
