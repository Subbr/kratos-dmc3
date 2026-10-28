# Trabalhar aqui com um agente (Claude Code ou similar) gastando pouco

O projeto inteiro foi feito por agente. Estas regras saíram do que mais custou tokens nas sessões anteriores.

## Ao abrir a sessão
1. O agente lê `CLAUDE.md` sozinho. Peça logo uma tarefa concreta de `docs/STATUS.md` ("Pendências").
2. **Não leia `docs/LOG.md` inteiro** (~120 KB). Busque o tema: `grep -n "Medusa" docs/LOG.md`, e leia só o
   teste mais recente (Tnn) sobre ele.
3. Código do mod: `dll/crimson/src/Kratos*.cpp` (DLL) e `tools/*.py` (geração de arquivos). Use busca, não leitura
   de arquivo inteiro — `KratosMode.cpp` passa de milhares de linhas.

## Testar sem gastar
- Teste automático em segundo plano: `"virtualPad": true` no KratosConfig, depois `tools/win/to_mission.sh` e
  `tools/win/act.sh` / `tools/win/burst.sh` (CLAUDE.md §12, item 4). Desligar `virtualPad` antes de jogar.
- **Imagens são caras.** Monte uma folha de miniaturas (`tools/win/zoom.py`, `thumb.py`) e veja uma imagem só, em
  vez de abrir capturas 1920×1080 uma a uma.
- Valide golpe e efeito pela imagem, mas só depois de o log (`logDamage`) indicar que algo mudou.
- Junte várias mudanças por teste: abrir o jogo leva ~75 s.

## Ao fechar
- Registre o teste em `docs/LOG.md` (data, o que fez, resultado, próximo passo) e atualize `CLAUDE.md` §12 e
  `docs/STATUS.md`.
- `./install.sh --check` deve dar 0 diferenças; restaure a config de testes (`virtualPad`, `logDamage`, dano).
- Commits pequenos, em português: `tipo(escopo): descrição`. Mudanças na DLL vão no submódulo `dll/crimson`
  (branch `kratos`) **e** no ponteiro do submódulo no repo principal.
