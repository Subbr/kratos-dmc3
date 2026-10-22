# Engenharia reversa — jogador (dmc3.exe)

Executável: `dmc3.exe` sha256 `e454272ed0fb0247fcbcf300e5d55d7a3e96d50b89b9ffaff81bb978dcbdd082` (Steam 2018, ASLR off).
Ferramenta: REA 6.7.0 + Ghidra 12.1.4 (`tools/rea_bridge.py` + `tools/rea_q.sh`, ver "Como usar o REA").

## Limite de 24 ossos por modelo do jogador
- endereço: `FUN_1401ef040` (monta os esqueletos do ator) → `FUN_14030f850(esqueleto, modelo, nós)`
- evidência: `FUN_14030f850` itera `i < *(u16*)(modelo+0xEA)` (nº de ossos do MOD) escrevendo em
  `nós[i]+0xFA`, `+0x110` (= matriz i, stride 0x40), `+0x80` (stride 0xA0). A lista `nós` vem do ator em
  +0x1880 / +0x1940 / +0x1A00 / +0x1AC0, espaçadas 0xC0 = 24 ponteiros. Crash do T15 (26 ossos):
  escrita em 0xFA a partir de `dmc3.exe+0x30F902` (dump do Windows).
- status: confirmado (T15 crash; T16 com 24 ossos carrega)

## Tabela de encaixe da arma na mão
- endereço: `.data` RVA 0x58BF90 (entrada da arma corpo a corpo na mão; translação -7.6, -3, -1 no espaço da mão).
  Outras entradas com o mesmo valor: 0x5796B0, 0x58BFF0, 0x58D250, 0x58D910, 0x58D940, 0x58D970.
- evidência: T13 — somar 40 ao Y da entrada 0x58BF90 mudou a matriz lógica da arma para (-7.6, 37, -1) · mão.
- o jogo lê a tabela a cada quadro para a **matriz lógica** da arma (`WeaponData::weaponCDraw[0].bonesMatrixesPtr`,
  osso 1 = cabo), que o **acerto** usa; o **desenho** da arma não usa essa matriz (T12/T13: nada mudou na tela).
- status: confirmado (log `logs/kratos.txt`)

## Volume de acerto dos golpes (T18)
- endereço: gancho do Crimson `InterceptingCollisions` (`CrimsonDetours.cpp`, chamado de `dmc3.exe+2CCC98` antes de
  gravar o raio); `KratosMode::OnCollision` registra cada `CollisionDataMetadata`.
- hash do executável: `e454272e…dd082`
- evidência (`logs/kratos.txt`, testes t18_dante3/t18_v7d): nos golpes da Rebellion aparecem volumes com
  `sourceMatrixAddr − ator = 0x80E40` (raio 40) e, no combo 2 golpe 2, 0x80F40 (raio 30). Os demais volumes existem o
  tempo todo (corpo, outros atores). São 3 esferas por quadro a ~0, ~22 e ~100 ao longo do eixo da "espada" da
  matriz de origem. `matrix1` (0x30) = cópia da matriz de origem; `hitboxPos` (0x130) = `pos2[0]` = `pos2[2]` =
  posição atual; `pos2[1]` = posição no quadro anterior.
- a matriz de origem **não** é a matriz de desenho da arma (`weaponCDraw[0]`, ator + 0x118800…) nem os ossos do corpo;
  [HIPÓTESE] é a matriz lógica da arma (tabela de encaixe × mão, T13).
- escrever `hitboxPos`/`pos2` no gancho **não** gerou dano (ímã: esferas a 0–7 do inimigo, 3/5 sem dano), e mover a
  matriz de origem no OnTick também não, mas esse teste foi com a mão parada (motions_v7) → inconclusivo.
- o dano exige a mão em movimento dentro da janela do golpe: o 3/5 com a animação do Dante e o resto do Kratos
  acerta 3/3; com a do Kratos começando no quadro errado, 0 (ver `docs/formats/mot.md`, `play_start`).
- status: confirmado (offset, campos, esferas); [HIPÓTESE] (origem = matriz lógica; exigência de varredura).

## Vida dos inimigos e rotação do jogador (T18)
- lista de inimigos: `*(dmc3.exe+0xC90E28)[8]` → `EnemyVectorData` (`Actor.cpp`, `CreateEnemyActor`);
  `metadata[i].baseAddr` = `EnemyActorData`. Hells (`PRIDE_1`…`HELL_VANGUARD`): vida em `hitPointsHells` (0x2E5C).
- `PlayerActorData::rotation` (u16): frente = (sin θ, 0, cos θ), θ = rot·2π/65536. Evidência: rot 0 anda em +z;
  rot 13551 (74,4°) avança (+97, +27) e atan2(97, 27) = 74,4°.
- OnTick (`TriggerOnTickFuncs`) roda **2 vezes por quadro** de motion [INFERIDO]: o dano do Dante cai em
  play_start + ticks/2 = quadro do golpe (3/3: 0 + 27/2 ≈ 14 → 15; 3/4: 23 + 24/2 = 35 → 35; 3/5: 40 + 40/2 = 60 → 61).

## Ordem do quadro (inferida)
- `TriggerOnTickFuncs` do Crimson (gancho `dmc3.exe+4F23B`, contagem de tempo de jogo) roda depois do desenho:
  escrever a matriz lógica da arma ali muda o acerto do quadro seguinte, mas não o desenho (T12).
- status: [HIPÓTESE] consistente com T12/T13

## Estruturas usadas (do Crimson, `dll/crimson/src/Vars.hpp`)
- `PlayerActorDataBase`: `modelData[3]` 0x200 (ModelData 0x780), `activeModelIndex` 0x3E6C, `action` 0x3FA4,
  `motionData[2]` 0x39B0 (index, group), `weapons[5]` 0x6498, `weaponDataAddr[5]` 0x64A0 (vazio com o módulo Actor
  do Crimson desligado), `nextBaseAddr` 0x30 = arma corpo a corpo atual (`WeaponData`).
- `ModelData::bonesMatrixesPtr` 0x208: matrizes 4x4 de mundo, vetor-linha, posição em [12..14].
- `GetVanillaPlayerActor()`: `[[dmc3+0xC90E28]+0x18]`.

## Como usar o REA
1. `tools/.venv/bin/python -I tools/rea_bridge.py` em segundo plano (mantém `rea --mcp` vivo; prazo de análise
   60 min e 6 GB de heap em `tools/rea.sh`).
2. `rm -f work/re/rea_session.json; tools/.venv/bin/python -I tools/rea_client.py open_binary '{"path": "/mnt/d/Code/god1_dmc3/work/re/dmc3.exe", "provider_id": "ghidra"}'`
3. Primeira consulta dispara a auto-análise (~10–15 min). Depois: `tools/rea_q.sh procedure_pseudo_code '{"procedure": "0x14030f902"}'`,
   `tools/rea_q.sh xrefs '{"address": "0x14030f850"}'`, `search_bytes`, `read_bytes`, `batch_decompile`.
- A versão npm (6.7.0) não tem `rea mcp --http`; não carrega PDB externo (o FakePDB do Crimson não é usado).
- Desmonte rápido sem REA: capstone no venv (ver LOG, crash do T15).
