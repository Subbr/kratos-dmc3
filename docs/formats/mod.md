# MOD (modelo do DMC3 HD)

Ferramenta: `tools/mod.py` (`Model.parse` / `Model.build`). `build()` reconstrói o arquivo do zero e
recalcula todos os offsets. **Round-trip byte a byte em 6474/6474 MODs do jogo** (`tests/test_mod.py`) e nos
2 MODs do `pl000.pac` do Crimson. Campos baseados no DMC3-Blender-Import-Addon (MIT).

## Layout (little-endian)
```
0x00 "MOD "  0x04 f32 versão (1.01 em 6137 arquivos; também 1.0, 0.9, 0.84...)
0x10 u8 objCount  0x11 u8 boneCount  0x12 u8 texCount  0x13 u8 ?   0x20 i64 offset do esqueleto
0x40 Object[objCount], 0x40 bytes cada:
     u8 meshCount, u8 ? (128), i16 numVerts (normalmente a soma das malhas; no Crimson nem sempre),
     4 bytes, i64 offset dos cabeçalhos de malha, u32 flags, 28 bytes, f32[4] esfera (x, y, z, raio)
Para cada objeto, nesta ordem, cada seção alinhada em 16:
     Mesh[meshCount] (0x50 cada): i16 vertCount, i16 texIdx, 12 bytes,
          i64 pos, i64 nrm, i64 uv, i64 boneIdx, i64 weights, i64 0, i64 uk, i64 0
     posições f32[3] de TODAS as malhas do objeto, depois normais f32[3], UV s16[2] (/4096, v invertido),
     ossos 4 bytes [?, b0*4, b1*4, b2*4], pesos u16 (3×5 bits + bit15 = reinício da triangle strip)
Esqueleto (alinhado em 16): i32 offsets relativos (hier, order, child, transforms);
     arrays de boneCount bytes alinhados em 4; transforms alinhado em 16, 32 bytes por osso
Cauda: preenchimento (0x12 repetido no pl000 original).
```
- `uk` aponta para dados de outras malhas: offset obsoleto (PS2?), preservado sem uso [HIPÓTESE].
- Faces: triangle strips; o bit 15 do peso marca o vértice que não fecha triângulo.
- Até 3 ossos por vértice (pesos de 5 bits).
- Exceções preservadas como bytes crus (`gaps`): 12 modelos de menu (`id430*`, `id470`) e os MODs do Crimson,
  gerados por outra ferramenta, com bytes não nulos no alinhamento.

## Dante (`pl000.pac`, item 001)
- Original: 17 objetos, **24 ossos**, 3 texturas.
- Crimson: 20 objetos, 24 ossos (modelo customizado: cabeça com 946 vértices contra 431). Prova que o jogo
  aceita um MOD com mais objetos e vértices que o original.
- Objetos 10–16 = cabeça e cabelo (esferas com y ≈ 164–175).
