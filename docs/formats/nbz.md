# Formato .nbz (DMC3 HD Collection)

- Arquivo: `data/dmc3/dmc3-0.nbz` (960.359.030 bytes, SHA-256 `dfdff00d4d3faaa810c0731278659677ec94c471c03f16914004e48430336da1`).
- Evidência: assinatura `50 4B 03 04` no offset 0 (ZIP); `zipfile` do Python abre sem erro.
- 4334 entradas, todas sob `GData.afs/` (o nome do AFS do PS2 virou nome de pasta).
  4333 com deflate (method 8) e 1 armazenada (a entrada de diretório).
- Extensões: pac 3725, txt 565, bin 24, tm2 6, mod 4, fon 4, ptx 2, bd/phd/tsb 1 cada.
- Dante: `pl000.pac` (1.335.280 bytes) e `pl000_00_0..31.pac`. Rebellion: `plwp_sword.pac`, `plwp_sword2.pac`, `plwp_sword3.pac`.
- Música fica fora do zip, em `data/dmc3/afs/sound/*.ogg`.
- **[HIPÓTESE]** O jogo aceita um .nbz reempacotado (ou arquivos soltos). Testar na Fase 1.
- Consequência: o `tools/afs.py` previsto no plano provavelmente não é necessário para o HD; o pipeline vira zip + pac.
