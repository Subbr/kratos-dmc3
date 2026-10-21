# MOT — animação do DMC3 HD

Ferramenta: `tools/mot.py` (round-trip byte a byte em **12181/12181** motions do jogo, `tests/test_mot.py`).
Base de campos: DMC3-Blender-Import-Addon (MIT), `DMC3/motion.py`; corrigido/estendido com a varredura do jogo.

## Onde ficam
- `pl000_00_N.pac`: cada item é uma motion (`size` + `MOT\0`). Grupo N = `MOTION_GROUP_DANTE` do DDMK
  (`vendor/ddmk/Mary/Vars.ixx`, `motionArchiveHelperDante`): 0 BASE, 1 DAMAGE, 2 TAUNTS, 3 REBELLION, 4 CERBERUS,
  5 AGNI_RUDRA, 6 NEVAN, 7 BEOWULF, 8 EBONY_IVORY ... 13 SWORDMASTER_REBELLION ...
- `pl000_00_0.pac` #0 = idle (105 frames). Confirmado como idle pela FK (pose em pé) — [INFERIDO], teste in-game T7.

## Layout
```
0x00 u32 header_size (0x50 no Dante)    0x04 "MOT\0"
0x0C f32 último frame (= 0x14)           0x18 u16 ?  0x1A u16 ?
0x1C u16 número de ossos (24)            0x1E u16[ossos] máscara de canais por osso
     bits: 0x100 TX 0x080 TY 0x040 TZ 0x020 RX 0x010 RY 0x008 RZ 0x004 SX 0x002 SY 0x001 SZ
header_size: u32 número de tracks (= total de bits das máscaras, 12181/12181)
tracks em sequência (osso crescente, canais na ordem dos bits acima):
  u16 tamanho, u16 chaves, u16 compressão, u16 início   (+ parâmetros + chaves)
zeros até alinhar o fim em 16 (12181/12181)
```
| compressão | parâmetros | chave | ocorrências |
|---|---|---|---|
| 0 linear f32 | — | u16 tempo, u16 ?, f32 valor | 2731 |
| 1 hermite f32 | — | u16 tempo, u16 ?, f32 valor, entrada, saída | 13032 |
| 2 linear i16 | f32 min, range | u16 tempo, u16 valor | 461090 |
| 3 hermite i16 | f32 min, range ×3 (valor, entrada, saída) | u16 tempo, valor, entrada, saída | 245971 |
| 7 ? | ? | ~4 bytes (preservado cru) | 12 (só `m07_b00.pac`) |

- Valor i16: `v × range / 65535 + min`. Tempo: bits 0–14 = frame (60 fps), bit 15 ligado nas chaves vistas.
- Rotação em **radianos**, local ao pai. Translação em unidades do modelo (quadril do Dante ≈ 113).
- Pose de repouso do esqueleto do Dante: só offsets, **sem rotação** (pose T). Logo a rotação da motion é a
  rotação local absoluta do osso.
- Dante idle: osso 1 (quadril) só TX/TY/TZ; ossos 2–23 só RX/RY/RZ; osso 0 nada.
- Ordem de Euler: **XYZ, R = Rz·Ry·Rx** [INFERIDO do importador; a prova é o T7].

## Índices conhecidos
| arquivo | índice | o que é | evidência |
|---|---|---|---|
| pl000_00_0 | 0, 1, 3, 11, 58 | paradas (variações) | pose (folha `tools/motion_sheet.py`); 0 confirmado in-game (T7b) |
| pl000_00_0 | 2, 51 | corrida | `CrimsonGameplay.cpp:4480` (`playerRunning`: motion 2/51/30) |
| pl000_00_0 | 4 / 5 / 9 | salto vertical / para a frente / para trás (osso 0 TY até ~270) | trilha do osso 0 |
| pl000_00_0 | 6 | aterrissagem (15 f) | pose [INFERIDO] |
| pl000_00_0 | 7 / 8 | rolamento esquerda / direita (osso 0 TX +350 / −350) | trilha do osso 0 |
| pl000_00_0 | 10 | levantar do chão | pose |
| pl000_00_0 | 16 | no ar, braços abertos (6 f) | pose [INFERIDO] |
| pl000_00_3 | 0, 1 | guarda com a arma | pose; in-game (T9) |
| pl000_00_3 | 3, 4, 5 | combo 1 | `CrimsonFX.cpp:467`; in-game (T9) |
| pl000_00_3 | 6, 7 | combo 2 (golpes 2 e 3) | `CrimsonFX.cpp:468` |
| pl000_00_3 | 13 | lançador (High Time) | pose [INFERIDO] |
| pl000_00_3 | 16 | Stinger nível 1 | `CrimsonDetours.cpp:449` |
| pl000_00_3 | 17, 18, 19 | Drive | `CrimsonGameplay.cpp:5418` |
