#!/usr/bin/env bash
# Renders do Kratos com as Blades para as artes dos menus (T50, T77): glb do corpo + lâminas (tools/glb_add_weapon.py)
# e uma pose por arte, fundo transparente, em work/install/menu_art/renders (fora do git; usados por build_menu_art.py).
# Uso: tools/render_menu_art.sh   (precisa do extracted/gow1 e do Blender de config/paths.env)
set -eu
cd "$(dirname "$0")/.."
source config/paths.env
M=work/install/menu_art; mkdir -p "$M/glb" "$M/renders"
G=extracted/gow1
tools/.venv/bin/python -I tools/glb_add_weapon.py $G/hero0/hero_obj.glb $G/weapons/maiblade.glb "$M/glb/kratos_blades.glb" --flip-edge >/dev/null
r() {  # r <saída> <animação> <fração> <lado> [ângulo]
  "$BLENDER_EXE" -b -P "$(wslpath -w blender/scripts/render_kratos.py)" -- "$(wslpath -w "$M/glb/kratos_blades.glb")" \
    "$(wslpath -w "$M/renders")\\$1.png" "$2" "$3" "$4" "$4" "${5:-25}" | grep "^ok" >/dev/null || { echo "falhou: $1" >&2; exit 1; }
}
r blades_title idleCombat2 0.5 1400
r blades_load boltThrow 0.35 1200
r blades_menu idleCombat 0.3 1000 35
r blades_end idleCombat2 0.5 800
echo "renders em $M/renders"
