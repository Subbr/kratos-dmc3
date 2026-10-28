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

## D5 — Controles: os mesmos do GoW1 (2026-10-27, LG)
- **Escolha:** "vamos deixar os mesmos controles do gow1". `"controls": "gow"` (padrão no código e na config do LG):
  □ X, △ Y, ○ B (agarrão), ✕ A (pulo), L1 LB (bloqueio e combinações), R1 RB (Hermes Rush/Stomp/Fury), R2 RT (magia),
  direcional = escolhe a magia, L3 + R3 = Rage of the Gods, analógico direito = esquiva. LT continua trocando a magia
  em ciclo (troca de arma de fogo do DMC3).
- **Evidência dos botões:** lista de golpes do HUD do GoW1 (FLP_HUD, T95) e tabela de gatilhos do ELF (gow-combat.md).
- **Como:** o motor lê os botões do GoW1 e apaga do DMC3 os que usa; direcional = apertos de CHANGE_GUN injetados até a
  arma da magia; L3 + R3 = soltura injetada do botão de DT (o DMC3 liga o DT na soltura, `FUN_1401e7500`, REA T96).
- **[HIPÓTESE]:** ordem do direcional (cima Poseidon, direita Medusa, baixo Zeus, esquerda Hades), `dpadSpells`.
- **Limite:** o DMC3 equipa no máximo as armas de fogo do save/loja; magia não equipada não é escolhida.

## D11 — Motor de combate do GoW1 dentro do DMC3 (2026-10-24, LG)
- **Problema:** até o T79 o Kratos é o DMC3 com pele do GoW1 — cada animação do GoW1 foi encaixada num golpe do Dante e
  o código do DMC3 decide combo, janela, cancelamento e tempo. Nunca terá a sensação do GoW1, por mais polimento.
- **Achado:** o combate do GoW1 é orientado a dados: `TWK_CombatFile_000…006` (R_PERM.WAD) = tabela de golpes
  (animação por hash, id, sub-tabelas), `TWK_Player` = parâmetros reais de magia/Rage/lâminas, `goHero` = tempos de
  transição. Ver `docs/formats/gow-combat.md`.
- **Escolha:** a DLL ganha um "motor Kratos" que **executa a tabela de golpes do GoW1** (animações no tempo original,
  transições e janelas da tabela, acerto por esferas nas lâminas). O DMC3 fica com câmera, física, fases e a reação
  dos inimigos ao dano (o LG achou razoáveis). Finalizações: genéricas ou só as principais. Flag `kratosEngine`.
- **Descartado:** usar o DMC3 de PS2 (o código do Kratos depende do motor inteiro do GoW1; perderíamos Crimson, REA e
  testes); levar o DMC3 para o GoW1 (sem ferramenta de importar fases); medir no PCSX2 (o LG não tem PS2 para extrair
  a BIOS — fica de fora).
- **Aproveita-se:** modelo, armas, Rage, HUD, menus, sons, infraestrutura. Sai: as motions do Kratos encaixadas nos
  golpes do Dante (ficam como modo antigo, sem a flag).
- **Gate:** protótipo do combo básico das Blades jogável na M3; o LG decide se a sensação está no caminho.
