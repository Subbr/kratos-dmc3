# GoW1 — dados de combate (TWK) — em andamento (D11, 2026-10-24)

Fonte: ISO NTSC-U `SCUS_973.99`, lidos pelo god_of_war_browser (`/json/pack/<WAD>/<tag>`), exportados em
`extracted/gow1/twk/*.json` (fora do git). Hashes de nome: `hash = hash*127 + byte` (gowb `utils/hash.go`); dicionário
`vendor/god_of_war_browser/hashes.dump.txt` (nomes de animação em MAIÚSCULAS, ex.: `8d8b1258` = `COMBO7A`).

## Onde estão
| Tag | WAD | O que é |
|---|---|---|
| `TWK_CombatFileSet_000` | R_PERM 2649 | conjunto "Hero": `File 0`…`File N`, escalas de impulso, `Invulnerable`, `Physics` |
| `TWK_CombatFile_000…006` | R_PERM 2616/2620/2631/2636/2643/2644/2648 | tabelas de golpes (binário, tipo 0x72) |
| `TWK_Player` | R_PERM 2666 | parâmetros nomeados: magias por nível (Lightning, MedusaHead, RaiseTheDead, Thunderbolt), BerserkBlade (Rage: dano ×1,75/2,25/3,0), alcance de mira, lâminas |
| `TWK_goHero` | R_HERO0 66 | `Animation/goHero/@hash(...)`: tempos de transição por animação (0–0,2 s) |

## CombatFile (binário) — o que já se sabe
- Cabeçalho: `u16 n_golpes` (0x25 = 37 no 000), `u16` (0x11), `u16 u16` (0x0ae8 0x0ae8).
- A partir de 0x08: `n_golpes` registros de **24 bytes**: `u32 hash_animação`, `u16 id`, `u16 A1`, `u16 A2`, `u16 A3`,
  `u16 0x3C00` (meio-float 1,0: velocidade [HIPÓTESE]), `u16 flags`, `u16`, `u16`, `u16`, `u16` (3–36: duração? [HIPÓTESE]).
- `A1/A2/A3` são deslocamentos **relativos ao início do registro** (golpe 0: 8 + 888 = 896 = fim da tabela).
- `A1` → lista de pares `(u16 ponteiro, u16 chave)`; chaves 0–0x0B, 0x1E–0x27, 0x3C (entradas/eventos? [HIPÓTESE]);
  os ponteiros levam a registros de 32 bytes. `A2` → registros de 28 bytes; `A3` → de 16 bytes. Formato interno ainda
  não decodificado.

## Executável (Ghidra + ghidra-emotionengine-reloaded v2.1.38, processador `r5900:LE:32:default`)
- Projeto em `work/ghidra/gow1` (fora do git). Script `tools/ghidra/DecompRefs.java` (descompila por referência ou
  função; cria a função se a análise não criou).
- `FUN_00201b70`: registra o tipo de recurso "CombatFile" (string 0x2B7A18), métodos em `0x2BA0B0`.
- `FUN_00201cc0`: registra "CombatFileSet" (0x2B7A28), métodos em `0x2BA050`, campos por hash e `File %d` × 8.
- Os métodos de `0x2BA0B0` (`FUN_00237228`, `FUN_00243500`, `FUN_0024cab8`, `FUN_0024cc20`, `FUN_0024cd58`) são de
  carga/referência do recurso, não o interpretador. **Próximo passo:** achar quem consome o ponteiro dos dados (a
  máquina de estados do herói).

## Transições e eventos — semântica (T92, ELF do GoW1 no Ghidra)
- **Gatilho → botão**: tabela de bytes em `0x2C0AE8` do ELF (`FUN_002072a0`): `[-1, 6, 7, 4, 5, 2, 0, 9, 3, 1, 10, -1…]`.
  Pelo uso na tabela: 0x01 ✕ (COMBO4D → COMBOJUMP, L1+✕ → BLOCKLAUNCHER, pulos de parede), 0x02 □, 0x03 △, 0x04 ○
  (GRAB), 0x05 L1 (bloqueio), 0x06 R2 (magia), 0x08 R1 [HIPÓTESE] (DASH, AIRDASH, BRUTAL3). Sem botão: 0x0B fim da
  animação (com destino EVADE* = analógico direito), 0x0C/0x13 analógico esquerdo > 0,5 (cancela andando), 0x0E vida
  ≤ 0, 0x10 golpe recebido no bloqueio, 0x11 agarrão pegou (destino por tipo de inimigo, `+0xA4`), 0x12/0x14/0x16.
- **Modo do botão** (`+0x1D`): 1 apertou, 2 soltou, 3/4 segurando, 5 solto.
- **Máscara** (`+0`, `FUN_002079d8` com o estado de `FUN_00207220`): bit 0 = janela que executa (sem ele o botão fica
  guardado); 0x2 chão, 0x4 ar; 0x200 qualquer arma, 0x100 sem 0x200 = só Artemis, nenhum = só Blades; 0x400 exige
  alvo; 0x2000 exige Rage, 0x8000 ignora Rage (sem os dois = fora da Rage); 0x80000/0x100000 bit 0x10 do herói.
- **Nível** (`+0x21`, "dif" no `gow_combat.py`): comparado com o byte global `0x302D3D` = nível da arma. Ex.: L1+□
  BLOCK360 nível 2, L1+△ BLOCKFORWARDFLIP 3, L1+✕ BLOCKLAUNCHER 1, L1+○ IMPALESLAMCHARGE 4, BRUTAL3 3, AIRDASH 1.
- **Ação 28** dos eventos (`FUN_00205488`, caso 0x1B): liga o bit 4 em `herói+0xC` (`FUN_00243160`). Aparece nas
  esquivas (0–0,598), nas magias (inteiras), PARRY02, COMBO7A/COMBO4D/AIRIMPALE e nas finalizações → invulnerável
  [HIPÓTESE pelo padrão; não achamos o leitor do bit].
- O parado com □ não está na tabela: a de COMBATLAND2 (97) serve de raiz no chão e a de COMBOJUMP (10) no ar.
- `zeroJoint` do glb também leva a altura: blockLauncher sobe 83 (× 4,8), comboJump sobe e cai, airImpale desce 191.
