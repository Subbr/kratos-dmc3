# Teste do LG — versão de 2026-10-24 (T76–T78)

Antes de jogar: `virtualPad` está **desligado** no `KratosConfig.json` (controle físico volta a funcionar). Para os
testes automáticos do agente, religar.

## O que mudou nesta versão
- Kratos com as Blades no **título**, na tela **LOAD/SAVE** (rótulo do slot "KRATOS") e nos fundos dos menus.
- Sprint, troca de estilo parado, taunt sorteado (agarrão), Drive, Quick Drive e Backslide do Crimson agora tocam
  animações do Kratos (antes mostravam o Dante).
- Sem o estalo de dedos do Dante na troca de estilo.
- Medusa: aura cinza no inimigo enquanto ele está petrificado.

## Checklist (marcar ok / problema)
| # | O quê | Onde | Resultado |
|---|---|---|---|
| 1 | Título e LOAD com o Kratos, sem corte feio | abertura | |
| 2 | Correr ~3 s (sprint): Kratos corre, não o Dante | qualquer missão | |
| 3 | Trocar de estilo parado (direcional): gesto do Kratos, sem estalo | qualquer missão | |
| 4 | Taunt (Back) várias vezes: sempre agarrão | perto de um Hell | |
| 5 | Drive (Stinger/combo + trás→frente + ataque, se liberado) | Blades | |
| 6 | Medusa (Spiral): inimigo para e fica com aura cinza | M3+ | |
| 7 | Volume e taxa das vozes (22050 Hz [HIPÓTESE]); voz do Dante sumiu? | combate | |
| 8 | Sons da Rage e de Poseidon (escolhidos pelo nome, [HIPÓTESE]) | DT / Shotgun | |
| 9 | Alcance e dano das Blades (`reachRadius 4`) | combate | |
| 10 | HUD do GoW1 (vida, magia, Rage, orbs, hits, barra do chefe) | combate / chefe | |

## Pendências conhecidas (não precisa reportar)
- Cutscenes em vídeo (12 `.webm`) ainda com o Dante — D6.
- Diálogos da história com "Dante" — Fase 9.
- Retrato da tela STATUS e cartas de golpe da loja nativa (a loja usada é a do Crimson).
- Almas do Army of Hades: usa o efeito roxo do Crimson, não as almas do GoW1.
- D2–D5 provisórias (`docs/decisoes.md`).
