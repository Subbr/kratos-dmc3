# GoW1 — FLP (interface estilo Flash) e o HUD (T94)

Fonte: `R_PERM.WAD` tag 2581 `FLP_HUD` (filme) + tag 2575 `HUD_0` (malha com os quads), exportados pelo gowb em
`extracted/gow1/flp/` (`/json/pack/R_PERM.WAD/<tag>`). Conversor: `tools/build_hud.py` → `hud.json`; player de
referência `tools/flp_player.py`; player do jogo `dll/crimson/src/KratosHud.cpp`.

## Estrutura (gowb `pack/wad/flp`, BrowserWadFlp.js)
- Handlers: tipo 1 = malha (MeshPartReference: parte da HUD_0 + material por objeto: textura, cor RGBA com 0x80 = 1,0),
  3 fonte, 4 rótulo estático (comandos com glifos), 5 rótulo dinâmico (texto da variável `ValueName`),
  6 = Data6 (sprite com `Sub1` timeline e `Sub2s` de botões), 7 = Data7 (sprite), 8 = raiz (Data8).
- Timeline: `ElementsAnimation` (um por profundidade) com `KeyFrames`: **`WhenThisFrameEnds` é o quadro em que o
  quadro-chave começa** (vale até o próximo; o visualizador do gowb lê ao contrário); tipo 0 = vazio.
  Prova: na raiz o MainMeter está em (0) e vazio em (2), e o rótulo "HUD" (jogo) é o quadro 1.
- Transformação `(OffsetX, OffsetY, Matrix[4])`, cor `[r, g, b, a]/256` multiplicando para baixo.
- Malha: tiras de triângulos do PS2 (`Skip` = vértice que não fecha triângulo), em pixels de uma tela 800 × 600;
  UV repetido (barras: v de −8 a 9).
- Scripts: ActionScript 1 (opcodes SWF: 0x96 push, 0x1C/0x1D get/set, 0x8B SetTarget, 0x8C GotoLabel, 0x81 GotoFrame,
  0x9F GotoFrame2 (1-based), 0x9E Call, 0x9D If, 0x99 Jump, 0x06 Play, 0x07 Stop, aritmética e lógica, 0x34 GetTime,
  0x83 FSCommand), por quadro (`FrameScriptLables`).
- Variáveis: por instância; `/:x`, `_level0/:x` = raiz; sem caminho e ausente no alvo = raiz (SetHealthMeter lê
  `PS2_HealthMeter_Value` com o alvo no medidor). Os eventos `*_Event` começam em −1.

## Contrato com o jogo (lido dos scripts; os nomes não estão no ELF)
- A raiz chama `SimKeyEvent` (quadro 7) a cada quadro: lê `PS2_*_Event`, aciona os sprites e volta o evento a −1.
- `PS2_InterfaceStyle_Event`: 1 título (quadro 93), 2 jogo (0 → "HUD"), 3 carregando. `PS2_MeterBar_Event` 1 = mostra o MainMeter.
- Vida: `PS2_HealthMeter_Value/Level`, evento 1. Magia: `PS2_MagicMeter_Value/Level`, evento ≥ 2 (0/1 = brilho).
  Valor em unidades da moldura: nível L comporta 100 + 25·L (preview `levels.png`, T94). O valor só entra quando o
  nível já é o mesmo do evento anterior (SetHealthMeter compara `HealthMeter_Level`).
- Magia equipada: `PS2_PickUp_Event` = quadro do sprite `MainMeter/PickUps`: 5 Poseidon (Lightning), 7 Medusa,
  9 Zeus (Thunderbolt), 11 Hades (RaiseDead); ícone no medalhão no nível `PS2_<magia>_Level`.
- Hits: `PS2_HitCounter_Value`, evento 1 mostra, 0 esconde, 2 marco (tremor/efeitos). Rótulo dinâmico `_level0/:HitCounter`.
- Rage (CoolMeter, capacete): `PS2_CoolMeter_Value` 0–100, evento 1 valor (som em 100), 2 brilho, 0 desliga.
- Orbs: `PS2_PowerOrb_Count`, evento 1; barra `PowerUpMeter` = orbs / 6 até `PS2_PowerOrb_Capacity` (300 enche os 52
  quadros); número no medalhão = `PowerOrb_Multiplier` (quantas vezes encheu).
- Rótulo dinâmico: `Unk014` = altura do texto [HIPÓTESE, 40 → escala 40/48]; avanço do glifo = largura × escala × 0,0982.
