# Estágio do desenvolvimento e pendências

Atualizado em 2026-10-28 (último teste registrado: T98). Histórico completo de cada teste: `docs/LOG.md`.
Decisões: `docs/decisoes.md`. Formatos descobertos: `docs/formats/`. Engenharia reversa: `docs/re/`.

## Fases

| Fase | O quê | Estado |
|---|---|---|
| 0 | Setup, override, inventário | ✅ |
| 1 | `pac.py` (unpack/repack idêntico) | ✅ |
| 2 | Exportador `.mod` (gate crítico) | ✅ |
| 3 | Kratos visual (corpo, roupas, Devil Trigger = Rage) | ✅ funcional, polimento pendente |
| 4 | Armas (Blades of Chaos, Blade of Artemis) | ✅ funcional |
| 5 | Animações e golpes do GoW1 | 🟡 motor Kratos (D11) executa a tabela de golpes original |
| 6 | Gameplay no fork do Crimson (magias, agarrão, bloqueio, Rage) | 🟡 maior parte feita |
| 7 | HUD do GoW1 (filme `FLP_HUD` original tocado pela DLL) | ✅ |
| 8 | Áudio (sons dos golpes, vozes) e textos | 🟡 combate feito; diálogos não |
| 9 | Cutscenes | ⬜ não iniciado (D6) |
| 10 | Pacote público / campanha completa | 🟡 `install.sh` pronto; M1–M20 sem queda (T41) |

## O que funciona hoje

- Kratos do GoW1 no lugar do Dante na campanha inteira, todas as roupas; Rage of the Gods no Devil Trigger.
- Motor de combate do GoW1 (`kratosEngine`): tabela de golpes original, combos no chão e no ar, bloqueio/parry,
  esquivas, agarrão com finalizações do legionário, acerto pelas lâminas com reação em qualquer inimigo.
- Magias Poseidon's Rage, Medusa's Gaze (petrifica, textura de pedra do GoW1), Zeus' Fury, Army of Hades, com os
  efeitos originais do GoW1 e barra de magia.
- HUD original do GoW1, sons dos golpes e vozes do Kratos, textos de menu/loja renomeados, artes de menu.

## Pendências (por prioridade)

1. **Combate:** finalizações dos outros inimigos do GoW1 (R_MIN, R_SIR, R_HAR, R_CY*) e pose do inimigo preso;
   prioridade das transições do GoW1; ordem do direcional das magias ([HIPÓTESE] em D5).
2. **Regras do GoW1:** Rage (dano ×1,75–3 da `TWK_Player`, como enche); golpes por nível de arma (D4); magia por
   orbs azuis (D3).
3. **Visual:** foices dos inimigos não viram pedra; tempo dos efeitos pelos eventos da tabela (hoje a olho); rastro e
   partículas das lâminas (`FXC_*`/`PTC_*`, a decodificar); testar motor/pedra em outros inimigos e chefes (só Hells
   da M3 testados a fundo).
4. **Sensação:** combo, pulo, esquiva e magias precisam de playtest humano; vozes; decisões D2–D4 e D6.
5. **Fora do combate:** cartas da loja nativa (`id741`–`id760`) e retrato do STATUS; diálogos (`mNN_*_msg_*`);
   cutscenes (Fase 9).

## Bom primeiro passo para um colaborador

Instale (`docs/INSTALACAO.md`), jogue a Missão 3 e abra uma *issue* com o que estranhou. Para código: pegue um item
de "Pendências", leia a seção correspondente em `CLAUDE.md` §12 e o teste mais recente em `docs/LOG.md` sobre o tema.
