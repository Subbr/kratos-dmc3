# Ambiente

| Item | Valor | SHA-256 |
|---|---|---|
| SO | Windows + WSL2 (kernel 6.6.114.1) | — |
| Python | 3.12.3 | — |
| Node | 22.23.2 | — |
| JDK (WSL) | Temurin 21.0.12.1 em `vendor/jdk21` | — |
| Ghidra (WSL) | 12.1.4 em `vendor/ghidra_12.1.4_PUBLIC` | — |
| Blender (Windows) | 5.2.2 LTS | — |
| PCSX2 (Windows) | instalado via winget | — |
| VS 2022 Build Tools | MSVC 14.44.35207, CMake 3.31.6 | — |
| xdelta3 | 3.1.0 (exe Windows) em `vendor/xdelta3` | — |
| DMC HD Collection | `./Devil May Cry HD Collection/` (4,6 GB) | — |
| dmc3.exe (original, antes do downpatch) | 6.790.632 bytes | `425d05bf1ea6531aca7633469b0d6c45af86b7fb05260b8b7eaa9329cf0ac805` |
| dmcLauncher.exe (original) | — | `f77d735db75fb140057f1941dbae71f22d2962fbc6a79fee840334ec0f645d64` |
| dmc3-0.nbz (contém GData.afs/) | 960.359.030 bytes | `dfdff00d4d3faaa810c0731278659677ec94c471c03f16914004e48430336da1` |
| ISO GoW1 (`./iso/gow1.iso`) | 8.522.792.960 bytes; NTSC-U `SCUS_973.99`, VER 1.00, volume GODOFWAR, 2005-02-14; DVD dupla camada (camada 0 = 4.260.986.880) | `0a41e19fae36ec8bd1f2a36d4ea42f120f525973d19b6d548eae792d1a15a338` |
| 7-Zip (Windows) | via winget | — |

## Build travada (a partir de 2026-10-20): Steam de lançamento, março de 2018
Obtida com `download_depot 631510 631511 7469687047717691926`. A cópia de 2026 (acima) foi movida para
`work/backup/game_2026/`.

| Item | Valor | SHA-256 |
|---|---|---|
| dmc3.exe (2018, original) | 6.356.432 bytes, PE timestamp 2018-03-23 | `4ae4bb5c83c19a649fc60edc5ca40e7f3ceee6337e4e4275025bfa9caa40c0a0` |
| dmc3.exe (2018, ASLR off = exe do Crimson) | DllCharacteristics 0x8120; adler32 0x7D3B3019 | `e454272ed0fb0247fcbcf300e5d55d7a3e96d50b89b9ffaff81bb978dcbdd082` |
| dmcLauncher.exe (2018) | 1.111.504 bytes | `5670afd7c862140922e328a743d159b229df5bc8111e47b63d3258e4912187ca` |
| dmc3-0.nbz (2018) | 960.358.951 bytes; 4334 entradas, só `msg_{eng,frn,ger,ita,spa}.pac` diferem da de 2026 | `2c2302cef5251d9a2499be728d81427e9689d0b9c3ceaeef10d9786260fd13df` |

**Hash travado para RE:** `e454272e…dd082` (exe que roda com o Crimson).
