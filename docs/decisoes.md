# Decisões

## D7 — Base do código: fork do DMC3 Crimson (2026-10-20)
- **Escolha:** fork do Crimson (zlib) em vez de DLL própria junto do DDMK.
- **Por quê:** o DDMK está parado; o Crimson é o sucessor, com o mesmo núcleo, ativo (commit em 2026-10-19,
  release 0.5a). Ele já resolve várias coisas que teríamos de escrever do zero: golpes novos, HUD customizável
  (`Crimson\huds`), sons próprios, troca de arma/estilo, roda de armas, GUI. Também traz material de RE
  (`Research/`: tabelas do Cheat Engine, ReClass, FakePDB).
- **Custo/risco:** o Crimson mexe muito no gameplay; usar o Game Mode "Vanilla" como base. Travar o fork
  numa tag.
- **Decidido por:** agente, na revisão do plano pedida pelo LG. O LG pode reverter.

## D8 — Assets pela pasta de override `data/dmc3/GData.afs/` (2026-10-20)
- **Escolha:** os arquivos trocados vão soltos nessa pasta; o `.nbz` original não é tocado.
- **Evidência:** DDMK `Mary/File.ixx` (`FileManager::Push` abre `data\dmc3\GData.afs\<nome>` antes de extrair
  do `.nbz`); Crimson `src/CrimsonFileHandling.cpp` (`Paths::gameMods`); relatos da comunidade de que a pasta
  sobrescreve o `.nbz`.
- **Status:** [HIPÓTESE] para os arquivos do jogador carregados pelo jogo — validar no teste T1.
- **Plano B:** gerar novo `.nbz` (ZIP) numa cópia.

## D9 — Jogo na raiz do projeto, fora da Steam (2026-10-20)
- **Escolha:** usar a cópia em `./Devil May Cry HD Collection/`.
- **Por quê:** a pasta da Steam está vazia; uma cópia fora da Steam não recebe updates, e isso trava o hash
  do exe.

## D10 — Build de 2018 + exe com ASLR desligado (2026-10-20)
- **Escolha:** usar a build de lançamento oficial (depot 631511, manifest 7469687047717691926) e gerar o exe
  do Crimson desligando só o bit DYNAMIC_BASE, em vez de aplicar patches de terceiros.
- **Evidência:** o resultado tem o mesmo tamanho e o mesmo adler32 do alvo declarado no patch oficial do Crimson.
- **Launcher:** não usamos o launcher patcheado. O jogo será aberto pelo `dmc3.exe` direto, com
  `steam_appid.txt` = 631510 [HIPÓTESE: funciona sem o launcher; testar].
