# GoW1 — ISO, PAK e WAD (via god_of_war_browser)

Ferramenta: god_of_war_browser compilado do fonte (commit de 2022-10-02, Go 1.27.3) em `vendor/gowb_bin/`.
A release beta4 é antiga (sem `-iso`) e não deve ser usada.

```
cd vendor/god_of_war_browser
../gowb_bin/god_of_war_browser -iso "$GOW1_ISO" -ps ps2 -gowversion 1 -i 127.0.0.1:8000
```

- Lê `GODOFWAR.TOC` + `PART1.PAK` / `PART2.PAK` (as duas camadas do DVD), somente leitura.
- `/json/pack`: 955 arquivos (339 VPK, 278 VAG, 217 WAD, 67 PSS, 53 PSW, 1 TXT).
- `/json/pack/<WAD>`: lista de tags (Tag 30 = recurso com nome e prefixo de tipo).
- `/action/<WAD>/<tagId>/gltf|fbx`: exporta objeto (OBJ = modelo + esqueleto + animações) ou MDL.

## WADs relevantes (pelos nomes; conteúdo a confirmar além do R_HERO0)
| WAD | Provável conteúdo |
|---|---|
| `R_HERO0..5.WAD` | Kratos (6 variantes/roupas). Cada um: `hero` (OBJ), `MDL_hero`, `ANM_hero`, TXR/MAT/PAL |
| `R_PERM.WAD` | Recursos permanentes (1735 tags): efeitos, `ANM_MagicGlowMaterial2`, `ANM_HealthGlowMaterial2`, `ANM_PowerGlowMaterial1`, baú, save point. Provável fonte do HUD e dos orbs |
| `R_SHELL.WAD` | Menus/interface [HIPÓTESE] |
| `R_LGHTN0..2.WAD` | Zeus' Fury [HIPÓTESE] |
| `R_MEDHD0..2.WAD` | Medusa's Gaze [HIPÓTESE] |
| `R_RDEAD0..2.WAD` | Army of Hades [HIPÓTESE] |
| `R_BRSRK0..2.WAD` | Rage of the Gods [HIPÓTESE] |

## Kratos (R_HERO0, tag 159 `hero`) — confirmado
- Exportado: `extracted/gow1/hero0/hero_obj.glb` (10.219.464 bytes), `.fbx`, `hero0.blend`.
- 111 ossos (`main`, `pelvis`, `vertebrae2..4`, `neck`, `head`, `jaw`, dedos completos, `lWeapIH`/`rWeapIH`,
  `lChain`/`rChain`, `leftBladeBack`/`rightBladeBack`, `skirtJoints`...).
- 7.418 vértices (7.409 após o import do Blender), 21 malhas, 7 materiais, 3 texturas (`maiF01..03`).
- **Máximo de 2 ossos por vértice** (medido no Blender).
- 251 animações com nome (lista em `extracted/gow1/hero0/animations.txt`). Grupos: wall 35, ber(serk) 23+4,
  combo 18, air 16, rope 16, hit 14, bolt 10, swim 10, block 9, evade 4, parry 3, grab 2...
