# Instalar o modo Kratos do zero (Fase 10)

Nenhum asset da Sony ou da Capcom é distribuído: tudo é gerado a partir do jogo e da ISO **do próprio usuário**
(regras 2 e 3 do CLAUDE.md). Este roteiro foi validado em 2026-10-23 (T57): ISO → export → build → arquivos
idênticos aos instalados.

## Pré-requisitos
- Devil May Cry HD Collection (Steam, build de 2018) com o **DMC3 Crimson 0.5a** instalado e o exe com ASLR
  desligado (D10, `docs/ambiente.md`).
- ISO do God of War (PS2, NTSC-U `SCUS_973.99`) em `iso/gow1.iso` (`config/paths.env`: `GOW1_ISO`).
- WSL com Python 3.12: `python3 -m venv tools/.venv && tools/.venv/bin/pip install -r requirements.txt`.
- god_of_war_browser compilado do fonte em `vendor/gowb_bin/` (docs/formats/gow-wad.md).
- Visual Studio 2022 Build Tools + CMake (DLL), Blender 5.2 (só para renders de menu, opcional).

## Passos
1. **Backups do Crimson:** copiar para `work/backup/crimson_override/` os arquivos originais do override do Crimson
   que o modo Kratos substitui (lista em `tools/build_all.sh`; `work/backup/crimson_override/SHA256SUMS` tem os hashes
   esperados). O `install_all.sh` também guarda backup de qualquer arquivo que ainda não tenha.
2. **Assets do GoW1:** `tools/export_gow1.sh` (≈ 3,5 min) → `extracted/gow1`.
3. **Build:** `tools/build_all.sh work/install/release` (≈ 1 min) → 62 PACs.
4. **Instalar:** `tools/install_all.sh`, `tools/install_sounds.sh`, `tools/install_hud.sh`.
5. **DLL:** `cmd.exe /c tools\win\build_crimson.bat` e `tools/win/install_crimson_dll.sh` (jogo fechado).
6. **Config:** `install_all.sh` instala `config/KratosConfig.default.json` se não houver; ajustar em `Crimson/configs/KratosConfig.json` — ver `dll/crimson/src/KratosMode.hpp`
   (cada recurso tem uma flag; `"enabled": false` desliga tudo).

## Desinstalar
- `tools/install_all.sh --restore` devolve os originais do Crimson; `"enabled": false` no KratosConfig desliga o
  código; o `Crimson.dll` original está em `work/backup/crimson_override/Crimson.dll.release-0.5a`.

## Pendente para uma distribuição pública
- Empacotar a DLL compilada e os scripts sem o resto do repositório (os scripts `tools/win` já calculam a raiz com
  `wslpath`, T57); checar a licença do god_of_war_browser (sem licença: o usuário
  precisa baixá-lo por conta própria).
