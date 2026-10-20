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
- Revisão 1 do plano: pesquisa mostrou que (1) DDMK/Crimson leem `data/dmc3/GData.afs/` solto antes do nbz; (2) Crimson (zlib, ativo) é base melhor que DDMK; (3) não existe exportador público de `.mod`. CLAUDE.md §3, §4, §6, §8, §9 reescritas; decisões D7–D9 em `docs/decisoes.md`. Crimson clonado em `vendor/DMC3-Crimson`.
- Backup de `dmc3.exe`, `dmcLauncher.exe`, `dmc3-0.nbz` em `work/backup/` (hashes em `work/backup/SHA256SUMS`, iguais aos de `docs/ambiente.md`).
- Crimson 0.5a extraído na pasta do jogo (1211 arquivos; 406 em `data/dmc3/GData.afs/`, incluindo `pl000.pac` próprio e `pl000_00_3.pac`). HUDs são `id100.pac`/`id100V.pac` em `Crimson/huds/<nome>/`.
- **Falha:** `apply_patch.bat` do Crimson não aplica. `xdelta3`: "target window checksum mismatch". O patch espera o `dmc3.exe` "original steam" (fonte ≥ 6.567.320 bytes); o nosso tem 6.790.632 bytes (update da Steam de set/2026). Mesmo problema com o downpatch do DDMK 2.7.3. Exe e launcher foram restaurados pelo script (hashes conferidos).
- Testado `hdc_patches_2026.zip` (fork ProjectXsent/ddmk, de terceiro): o launcher sai idêntico ao do DDMK 2.7.3 (adler32 BE2F9BE2 confere), mas o `dmc3.exe` sai com adler32 09BF3785 ≠ 97803703 do DDMK oficial → binário de origem não verificável. **Descartado** (arquivo apagado) e não executado. O script dele também altera `steam_api64.dll`.
- Caminho escolhido: baixar a build antiga oficial pela Steam (`download_depot 631510 631511 7469687047717691926`, manifest pré-update de 2023, fonte: discussão na Steam) e aplicar o patch do Crimson, que valida por checksum.
- Inventário do nbz: `tools/nbz_inventory.py` → `extracted/dmc3/inventory.csv` (4333 arquivos; .pac com magic `PAC` 3513 / `PNST` 212; HUD = `id100.pac`).
- god_of_war_browser compilado do fonte (beta4 não tem `-iso`). Kratos exportado do `R_HERO0.WAD` para glTF com 111 ossos, 7418 vértices e 251 animações com nome; importado no Blender 5.2 headless (`blender/scripts/inspect_gltf.py`). Ver `docs/formats/gow-wad.md`.
- REA adiado até o exe final (os endereços dependem do hash).
- Cutscenes: 30 .webm em `data/dmc3/Video` (12 de missão). O resto da história deve rodar no motor [HIPÓTESE]. Ver `docs/design/cutscenes.md`.
