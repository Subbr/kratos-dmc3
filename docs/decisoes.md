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
- **Status:** **confirmado pelo T1** (2026-10-20): `pl000.pac` na pasta de override troca o modelo do Dante in-game.
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

## D1 — Blades of Chaos no slot Rebellion (2026-10-20, LG)
- **Escolha:** Blades of Chaos substituem a Rebellion (`plwp_sword*.pac`), arma inicial. O Kratos começa com elas, como no GoW1, e herda o moveset mais completo.
- **Consequência:** a Rebellion é de uma mão. A lâmina da mão esquerda precisa de outra solução (presa ao modelo do corpo ou a outra peça). Blade of Artemis vai para outro slot (Agni & Rudra ou similar), a definir.

## D2 — Estilos (PROVISÓRIA, agente, 2026-10-23 — aguardando o LG)
- **Em uso:** Trickster = rolamento do GoW1 (T21); Royalguard = bloqueio, parry e Release (T24, T39); Swordmaster =
  especiais (T23, T48); Gunslinger = sem mudança (as magias já estão nas armas de fogo, T49). Quicksilver e
  Doppelganger continuam do DMC3.
- **Aberto:** desligar Quicksilver/Doppelganger ou reaproveitá-los (ex.: Rage/Army of Hades).

## D3 — Recarga da magia (PROVISÓRIA, agente, 2026-10-23 — aguardando o LG)
- **Em uso:** a magia volta pelo dano causado (`magicPerDamage` 0,05 por ponto de vida tirado; vale em chefes, T43),
  sem recarga por tempo. No GoW1 ela vem dos orbs azuis.
- **Alternativa:** orbs verdes do DMC3 também recarregam magia; ou baús de orbs azuis.

## D4 — Níveis de arma (PROVISÓRIA, agente — aguardando o LG)
- **Em uso:** loja do Crimson (Customize) com os nomes do GoW1 (`renameUi`, T38); nenhum nível próprio das Blades.
  Magias sobem com os níveis das armas de fogo da loja (T74: +50% de dano por nível; Medusa +1,5 s).

## D5 — Controles (PROVISÓRIA, agente — aguardando o LG)
- **Em uso:** botões do DMC3 (§7.4 opção a). Agarrão no taunt (Back), magias nas armas de fogo (X; LT troca),
  Rage no DT (LB).
