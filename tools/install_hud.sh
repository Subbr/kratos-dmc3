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
cp $S/TXR_HUD019.png "$D/fill.png"       # gradiente branco das barras (tingido; T61)
cp $S/TXR_HUD013.png "$D/orb.png"        # orb (tingido de vermelho no contador)
cp $S/TXR_HUD004.png "$D/rage_cap.png"   # voluta dourada do medidor de Rage
cp $S/TXR_HUD003.png "$D/rage_bar.png"   # barra de ouro do medidor de Rage
cp $S/TXR_HUD036.png "$D/boss_cap.png"   # ponta de lança dourada da barra do chefe (T69)
cp $S/TXR_HUD037.png "$D/boss_bar.png"   # barra de pedra do chefe
