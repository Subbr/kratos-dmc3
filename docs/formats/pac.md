# PAC / PNST (DMC3 HD)

## Estrutura (confirmada em 3725/3725 arquivos do nbz de 2018)
```
0x00  char[4]  magic        "PAC\0" (3513 arquivos) ou "PNST" (212)
0x04  u32      count
0x08  u32[count] offsets    0 = slot vazio
...   padding até o primeiro item (header_pad)
...   itens, cada um do seu offset até o próximo offset não nulo (ou EOF)
```
- Offsets crescentes; itens alinhados em 16 bytes, exceto 139 arquivos alinhados em 8.
- PACs aninhados são comuns (621 itens `PAC\0`, 517 `PNST`).
- Magics internos mais comuns: `MOD ` 4892, `PAC` 621, `PNST` 517, `HITS` 279, `VAGp` 249, `Head` 249, `SCM ` 195.

## Ferramenta
`tools/pac.py unpack|repack` — round-trip byte a byte em 100% dos arquivos (`tests/test_pac.py`).
O unpack grava `pac.json` (magic, header_pad, align, ordem dos itens).

## Conteúdo observado
| Arquivo | Itens |
|---|---|
| `pl000.pac` (Dante) | 000 sem magic (616.448 B, provável textura) · **001 `MOD` (216.544 B, modelo do Dante)** · 002–004 `PAC` aninhados · 005 · 006 · 007 · 008 `SHW` · 009–011 · **012 `MOD` (35.696 B)** · 013 · 014 `SHW` |
| `plwp_sword.pac` (Rebellion) | 000 sem magic (47.104 B) · 001 `MOD` · 002 `PNST` · 003 `SHW` · 004 `PAC` |
| `id100.pac` (HUD) | 58 itens: blocos de textura (69.632 / 20.480 / 12.288 B) intercalados com `MOD`s pequenos (elementos do HUD como modelos 2D) |
| `pl000_00_0.pac` (motions) | slots esparsos 000–058 com magic `P` → [HIPÓTESE] motions `.mot` do importador do Blender |

[HIPÓTESE] O item 000 sem magic é textura (TM2 sem cabeçalho ou bloco de pixels); confirmar com o `model.py` do addon.
