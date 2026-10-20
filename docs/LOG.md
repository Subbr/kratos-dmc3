# LOG

## 2026-10-20
- Feito: estrutura do repositório, `.gitignore`, `config/paths.env`, permissões do agente em `.claude/settings.json`.
- Ambiente: WSL com git, python 3.12.3, node 22.23.2. Faltam: java/JDK 21, xdelta3, 7z, cmake (WSL), Blender, Ghidra, PCSX2.
- Instalação Steam em `D:\SteamLibrary\...\Devil May Cry HD Collection` está vazia (só `Installer`); o LG vai copiar o jogo de outro HD para a raiz do projeto.
- Próximo: receber cópia do DMC HD e a ISO do GoW1 em `iso/`; calcular hashes; DDMK + downpatch.
- Instalados: Blender 5.2.2, PCSX2, VS 2022 Build Tools (MSVC 14.44 + CMake 3.31.6) via winget; JDK 21 e Ghidra 12.1.4 no WSL em `vendor/` (sem sudo). Caminhos em `config/paths.env`.
- DMC HD copiado para a raiz. Hashes de `dmc3.exe`, `dmcLauncher.exe` e `dmc3-0.nbz` registrados em `docs/ambiente.md`.
- Achado: não existe `GData.afs` solto no HD; `data/dmc3/dmc3-0.nbz` é um ZIP com `GData.afs/` (4334 arquivos). Ver `docs/formats/nbz.md`.
- ISO do GoW1 veio em `God of War.7z` (7z legítimo: só `God of War.iso` + `readme.html`, sem executável). Instalado 7-Zip; ISO extraída para `iso/gow1.iso` (NTSC-U SCUS_973.99 v1.00). readme.html não extraído.
- Próximo: backup + downpatch/DDMK (pedir confirmação), god_of_war_browser na ISO, REA no dmc3.exe.
