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
