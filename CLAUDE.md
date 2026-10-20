# Projeto Kratos × DMC3 — CLAUDE.md

> Arquivo de instruções do projeto para o Claude Code. Leia inteiro no início de cada sessão.
> Atualize a seção **Estado atual** (no fim) sempre que concluir uma tarefa ou tomar uma decisão.

---

## 1. Objetivo

Mod para **Devil May Cry 3: Special Edition** na versão **Devil May Cry HD Collection (Steam, PC)** em que o
**Kratos do God of War 1 (PS2, 2005)** substitui o Dante na campanha inteira, com:

- modelo, texturas e Devil Trigger reaproveitando o visual do Kratos (Rage of the Gods);
- as **mesmas armas** do GoW1 (Blades of Chaos, Blade of Artemis);
- os **mesmos golpes** (combos, especiais, agarrão, bloqueio, rolamento);
- as **mesmas magias** (Poseidon's Rage, Medusa's Gaze, Zeus' Fury, Army of Hades);
- o **HUD** do GoW1 (vida, magia, Rage, contador de orbs e de hits);
- sons de combate e falas do Kratos.

Fases, inimigos, chefes, missões e história do DMC3 permanecem.

**Princípio central: não portamos nada.** O DMC3 HD roda nativo no Windows. O GoW1 serve apenas como
**fonte de assets**, extraídos da ISO do próprio usuário. Não emulamos nem recompilamos o GoW1.

---

## 2. Regras invioláveis

1. **Nunca altere originais.** Nada de escrever na pasta do jogo instalada nem na ISO do GoW1. Trabalhe em
   cópias dentro de `work/`. Antes do primeiro teste in-game, faça backup de `GData.afs` e do executável
   (com hash SHA-256 registrado em `docs/ambiente.md`).
2. **Nenhum asset da Sony ou da Capcom entra no git.** O repositório guarda apenas código, scripts,
   mapeamentos, configs e documentação. O `.gitignore` deve cobrir: `extracted/`, `work/`, `build/out/`,
   `vendor/`, `*.iso`, `*.afs`, `*.pac`, `*.mod`, `*.mot`, `*.scm`, `*.wad`, `*.pak`, `*.toc`, `*.wmv`,
   `*.dds`, `*.png` em pastas de assets, `*.wav`/`*.vag`/`*.ogg` extraídos.
3. **Distribuição** (se um dia houver) = patch `xdelta3` + scripts que extraem tudo do jogo e da ISO do
   próprio usuário. Nunca hospedar modelo, textura ou áudio extraído.
4. **Evidência antes de afirmação.** Toda conclusão sobre formato de arquivo, offset, estrutura ou endereço
   do executável precisa de evidência registrada em `docs/` (hex dump, trecho do código do DDMK/addon,
   função no Ghidra via REA, teste in-game). O que não foi provado vai marcado como **[HIPÓTESE]**.
5. **Voz:** usar só falas e grunhidos **originais extraídos do GoW1**. Não gerar falas novas por clonagem
   de voz do dublador.
6. **Passos pequenos e testáveis.** Cada fase tem critério de aceite. Resultado de cada teste vai para
   `docs/LOG.md` (data, o que foi feito, o que aconteceu, próximo passo).
7. **Round-trip primeiro.** Nenhuma ferramenta de escrita (repack, exportador) é usada com conteúdo novo
   antes de provar que reescreve o original de forma idêntica ou que o jogo carrega igual.
8. **Versão travada.** Os endereços do DDMK valem para o executável com downpatch. Registre o hash do
   executável usado; se mudar, todo endereço reverso precisa ser revalidado.
9. Antes de ações destrutivas ou demoradas (repack do AFS inteiro, sobrescrever arquivos na cópia de
   trabalho), confirme com o LG.

---

## 3. Ambiente

- **Windows + WSL.** O Claude Code roda no WSL. O jogo fica no lado Windows, por padrão em
  `C:\Program Files (x86)\Steam\steamapps\common\Devil May Cry HD Collection`
  (no WSL: `/mnt/c/Program Files (x86)/Steam/steamapps/common/Devil May Cry HD Collection`).
  Confirmar o caminho real e gravar em `config/paths.env`.
- Arquivo de dados do DMC3: `data/dmc3/GData.afs` (dentro da pasta do HD Collection).
- Executável do DMC3: confirmar nome e caminho na Fase 0 (registrar em `docs/ambiente.md`).
- Programas Windows são chamados a partir do WSL pelo `.exe` direto ou via `powershell.exe -Command`.
- **Blender** (3.6+ ou 4.x) em modo headless: `blender.exe -b -P blender/scripts/<script>.py -- <args>`.
- **Python 3.11+** para as ferramentas (`tools/.venv`). Rodar scripts que leem arquivos extraídos com `python -I`.
- **C++ / MSVC** (Visual Studio Build Tools) para a DLL, compilada do lado Windows. Usar CMake.
- **Ghidra + JDK 21** para o REA.

---

## 4. Ferramentas externas

Baixar em `vendor/` (gitignored). Não copiar código de projetos sem licença para dentro do repositório.

| Ferramenta | Para quê | Origem / licença |
|---|---|---|
| Devil May Cry HD Collection | Base jogável | Steam |
| **DDMK** (serpentiem) | Carregador de mods e hooks. O módulo `Mary/` (DMC3) tem estruturas do ator já mapeadas: `Mary/Actor.ixx`, `Mary/File.ixx`, `Mary/Vars.ixx`, `Scripts/dmc3_create_data.js` (offsets de structs), enums `MOTION_GROUP_DANTE::*`. Exige downpatch (`hdc_patches` + `xdelta3`, ver README do DDMK) | github.com/serpentiem/ddmk — zlib |
| Crimson (Berthrage & C-Team) | Overhaul de gameplay, referência e alternativa ao DDMK | Nexus Mods |
| **god_of_war_browser** (mogaika) | Extrai o GoW1 direto da ISO: modelos (`mdl`, `mesh` → glTF/FBX), animações (`anm`), texturas (`txr`), UI/HUD (`flp`), banco de som (`sbk`, a verificar), objetos (`obj`). Uso: `-iso "<ISO>" -ps ps2 -gowversion 1`, interface web em `http://127.0.0.1:8000/` | github.com/mogaika/god_of_war_browser — **sem arquivo de licença**: usar só como ferramenta |
| **DMC3-Blender-Import-Addon** (HansLichtner) | Importa `.mod` (modelos), `.scm` (cenário) e `.mot` (animações) no Blender. **Só importa.** Código (`DMC3/model.py`, `DMC3/motion.py`, `common/io.py`) é a base para escrevermos o exportador | github.com/HansLichtner/DMC3-Blender-Import-Addon — MIT |
| **REA** (morluto) | MCP de engenharia reversa. Usar **somente no executável do DMC3** (PE x86_64) com Ghidra. **Não aceita ELF de PS2** (R5900 é recusado). Instalação: `npx rea-agents setup` no WSL | github.com/morluto/rea — MIT |
| ghidra-emotionengine-reloaded | Só se precisarmos ler o ELF do GoW1 como referência de comportamento (timings, alcance da corrente) | github.com/chaoticgd/ghidra-emotionengine-reloaded |
| PCSX2 | Rodar o GoW1 original para gravar referência de golpes, timings e HUD | pcsx2.net |
| xdelta3 | Downpatch do DDMK e nossos patches | romhacking.net |
| Ferramentas da comunidade DMC3 (fórum Infernal Warks, créditos ao modder "Che") | Possível exportador/injetor de modelos já existente — **investigar na Fase 0** | — |

---

## 5. Estrutura do repositório

```
kratos-dmc3/
├── CLAUDE.md
├── .gitignore
├── config/
│   └── paths.env              # caminhos do jogo, ISO, Blender, Ghidra
├── docs/
│   ├── ambiente.md            # versões, hashes, caminhos confirmados
│   ├── LOG.md                 # diário de testes
│   ├── decisoes.md            # registro de decisões (D1, D2...)
│   ├── formats/               # um .md por formato: afs.md, pac.md, mod.md, mot.md, gow-*.md
│   ├── re/                    # achados de engenharia reversa do executável (endereço + evidência)
│   └── design/
│       ├── moveset-gow1.md    # levantamento completo dos golpes do Kratos
│       ├── controles.md       # esquema de controles GoW1 x DMC3 e decisão final
│       └── hud.md             # elementos do HUD do GoW1 e plano de implementação
├── mapping/
│   ├── moveset.yaml           # golpe GoW1 -> slot/motion do DMC3
│   ├── weapons.yaml           # arma/magia GoW1 -> arma/estilo do DMC3
│   └── files.yaml             # arquivo do DMC3 -> substituto
├── tools/                     # Python: afs.py, pac.py, mod_export.py, mot_export.py, inventory.py
├── blender/
│   └── scripts/               # retarget, re-skin, export headless
├── dll/                       # C++ (CMake): hooks de gameplay e HUD
├── build/
│   └── make_patch.py          # gera patches xdelta a partir de work/
├── tests/                     # testes de round-trip e de parsers
├── vendor/        (gitignored)
├── extracted/     (gitignored) # gow1/, dmc3/
└── work/          (gitignored) # cópias de trabalho do jogo
```

---

## 6. Arquitetura do mod

O Kratos entra no jogo por três camadas independentes:

1. **Dados (assets)** — substituição de arquivos dentro de `GData.afs`: modelo do Dante (arquivos `pl000*`),
   modelo de Devil Trigger, armas (`plwp_*.pac`, ex.: `plwp_sword.pac` = Rebellion), animações (`.mot`),
   texturas, texturas do HUD e sons. Exige: unpack/repack de AFS e PAC, exportador `.mod` e `.mot`.
2. **Código (DLL)** — DLL própria carregada junto ao DDMK (ou fork do módulo `Mary`), com hooks para o que
   dados não resolvem: barra de magia, magias com efeito próprio (petrificação, almas teleguiadas),
   agarrão, alcance da corrente, regras do Rage, HUD desenhado por cima, ajustes de hitbox.
3. **Cutscenes (vídeo)** — no HD Collection grande parte das cutscenes são vídeos pré-renderizados (WMV).
   Trocar o modelo não muda os vídeos. Tratadas à parte na Fase 9.

---

## 7. Mapeamento de design GoW1 → DMC3

Proposta inicial. Cada linha vira decisão registrada em `docs/decisoes.md` antes de ser implementada.

### 7.1 Armas e magias

| GoW1 | Slot no DMC3 | Motivo | Observação |
|---|---|---|---|
| **Blades of Chaos** | Agni & Rudra | Já é arma dupla, presa às duas mãos | Alternativa: slot Rebellion (mais golpes, mas só uma mão) — **D1** |
| **Blade of Artemis** | Rebellion | Espada grande de uma lâmina | Arquivo `plwp_sword.pac` / `plwp_sword2.pac` |
| Corrente das Blades (alcance) | DLL | Esticar a corrente não existe no motor do DMC3 | MVP: lâminas fixas nas mãos |
| **Zeus' Fury** | Ebony & Ivory | Projétil à distância | Consome magia (DLL) |
| **Poseidon's Rage** | Shotgun | Golpe em área próxima | Efeito visual novo |
| **Medusa's Gaze** | Spiral | Disparo único em alvo | Petrificação exige DLL |
| **Army of Hades** | Artemis (arma de fogo) | Disparos teleguiados múltiplos | Almas no lugar dos lasers |
| **Rage of the Gods** | Devil Trigger | Ambos enchem batendo e dão um modo de poder | Modelo de DT = Kratos brilhando |
| Bloqueio / parry (GoW) | Estilo Royalguard | Mecânica quase igual | — |
| Rolamento (GoW) | Estilo Trickster | Esquiva com direção | — |
| Golpes especiais | Estilo Swordmaster | Concentra os especiais da arma | — |
| Agarrão + finalizações | DLL | Não existe no DMC3 | QTE fica para depois do MVP |
| Estilos Gunslinger, Quicksilver, Doppelganger | Desabilitar ou reaproveitar | GoW não tem estilos | **D2** |

### 7.2 Recursos e progressão

| GoW1 | DMC3 | Plano |
|---|---|---|
| Orbs vermelhos (upgrade) | Orbs vermelhos (loja) | Mantém; renomear itens da loja para upgrades do GoW1 |
| Orbs verdes (vida) | Orbs verdes | Mantém |
| Orbs azuis (magia) | — | Barra de magia nova via DLL; definir como recarrega — **D3** |
| Barra de Rage | Barra de Devil Trigger | Reaproveitar a lógica nativa |
| Níveis de arma | Compras na Divinity Statue | Mapear níveis das Blades para compras — **D4** |

### 7.3 Golpes

- Fase 5 começa com o **levantamento completo** em `docs/design/moveset-gow1.md`: nome, comando, nível
  em que libera, ID da animação no god_of_war_browser, duração em frames, notas de dano e alcance.
  Exemplos a confirmar no jogo: Plume of Prometheus, Cyclone of Chaos, Orion's Harpoon, Hyperion Charge,
  Spirit of Hercules. **Não confiar em listas de memória; validar no PCSX2 e no manual.**
- Cada golpe vira uma entrada em `mapping/moveset.yaml`:

```yaml
- gow_move: "Plume of Prometheus"
  gow_input: "a confirmar"
  gow_anim: "<id no god_of_war_browser>"
  dmc3_target:
    weapon: AGNI_RUDRA            # slot escolhido em D1
    motion_group: "MOTION_GROUP_DANTE::<...>"   # ver Mary/Actor.ixx do DDMK
    motion_index: null
  strategy: replace_motion        # replace_motion | new_move_dll
  keep_duration: true             # manter a duração da animação original para não quebrar hitbox
  status: todo                    # todo | extracted | retargeted | in_game | tuned
```

- Regra: **substituir animação mantendo a duração original** primeiro (hitboxes continuam sincronizadas).
  Golpe sem equivalente no DMC3 vira `new_move_dll` e só entra na Fase 6.

### 7.4 Controles

Levantar o esquema do GoW1 e do DMC3 em `docs/design/controles.md` e escolher entre (a) manter os botões
do DMC3 com golpes do Kratos ou (b) reproduzir o layout do GoW1 via DLL — **D5**. Recomendação inicial: (a)
no MVP, (b) como opção depois.

### 7.5 HUD

Elementos do GoW1: barra de vida (verde), barra de magia (azul), barra de Rage, contador de orbs vermelhos,
contador de hits. Duas etapas:
1. **Troca de textura** dos elementos do HUD do DMC3 (ganho rápido).
2. **Overlay pela DLL** (hook de renderização, como o DDMK faz para a própria interface): esconder o HUD
   original e desenhar o do GoW1 com texturas extraídas dos recursos `flp`/`txr`. O medidor de estilo
   ("Smokin' Sick Style") vira o contador de hits.

### 7.6 Áudio e texto

- Sons das Blades, impactos e grunhidos do Kratos extraídos do GoW1 (formato `sbk` — a verificar).
- Falas de combate do Dante substituídas por grunhidos/falas originais do Kratos.
- Música do DMC3 mantida.
- Textos de interface e loja: "Dante" → "Kratos", armas e itens renomeados. Diálogos da história ficam
  para a Fase 9.

---

## 8. Fases

Cada fase tem **entregável** e **critério de aceite**. Não avance sem cumprir o critério ou sem registrar
por que foi aceito diferente.

### Fase 0 — Setup e reconhecimento
- Criar repositório, `.gitignore`, `config/paths.env`, estrutura de pastas e `docs/`.
- Confirmar caminhos e versões; calcular SHA-256 do executável e de `GData.afs`; registrar em `docs/ambiente.md`.
- Instalar DDMK com downpatch; confirmar que o jogo abre e roda com ele.
- Copiar `GData.afs` para `work/`.
- Inventário: listar todo o conteúdo do AFS (nomes, tamanhos, tipos) → `docs/formats/afs.md` e
  `extracted/dmc3/inventory.csv`. Identificar arquivos do Dante, das armas, das animações e do HUD.
- Contar cutscenes que são vídeo versus em motor → `docs/design/cutscenes.md`.
- Rodar o god_of_war_browser na ISO do GoW1; exportar o Kratos (modelo com esqueleto) e 3 animações para
  glTF/FBX em `extracted/gow1/`; abrir no Blender.
- Pesquisar ferramentas existentes de exportação/injeção de modelos para DMC3 (fórum Infernal Warks,
  créditos "Che", mods como "Jin Kazama Tekken 4 outfit", "DMC 2 Mod pack", "DMC4 Rebellion").
- Instalar REA + Ghidra; abrir o executável do DMC3 e confirmar que a análise funciona.
- **Aceite:** ambiente documentado com hashes; inventário do AFS; Kratos aberto no Blender com esqueleto;
  REA analisando o executável; relatório sobre ferramentas existentes de exportação.

### Fase 1 — Pipeline de arquivos
- `tools/afs.py` (unpack/repack) e `tools/pac.py` (unpack/repack), com testes em `tests/`.
- **Aceite:** repack sem alterações gera arquivo idêntico byte a byte (ou, se o formato não permitir, o jogo
  carrega a cópia reempacotada e roda uma missão sem diferença). Documentado em `docs/formats/`.

### Fase 2 — Exportador de modelo `.mod` — **GATE CRÍTICO**
- Usar ferramenta existente encontrada na Fase 0 **ou** escrever `tools/mod_export.py` / exportador Blender
  a partir do importador (`DMC3/model.py`).
- **Aceite:** importar o modelo do Dante, exportar sem mudanças, reinjetar e o jogo exibir o Dante igual;
  depois, uma alteração simples (ex.: mover vértices) aparecer in-game.
- Se falhar: parar e reavaliar o projeto com o LG antes de seguir.

### Fase 3 — Kratos visual (MVP)
- Script Blender: re-skin da malha do Kratos no **esqueleto do Dante** (nomes, contagem e ordem de ossos do
  `.mod` original). Ossos do casaco do Dante: deixar sem pesos ou usar em detalhes (saiote, correntes).
- Respeitar limites do formato (ossos por vértice, vértices por malha, texturas) descobertos na Fase 2.
- Substituir modelo de jogo do Dante e modelo de Devil Trigger (Kratos com efeito de Rage).
- **Aceite:** jogar as Missões 1 a 3 com o Kratos, animações do Dante funcionando, sem crash e sem
  deformação grave.

### Fase 4 — Armas visuais
- Blades of Chaos no slot decidido em D1; Blade of Artemis no slot Rebellion; texturas.
- **Aceite:** as duas armas aparecem corretas nas mãos em idle, combo e troca de arma.

### Fase 5 — Animações e golpes
- Levantamento do moveset (seção 7.3) e gravação de referência no PCSX2.
- Exportador `.mot` (a partir de `DMC3/motion.py`), com round-trip igual ao da Fase 2.
- Retarget das animações do GoW1 para o esqueleto do Dante, mantendo a duração de cada motion substituída.
- Substituir primeiro: idle, corrida, pulo, combo básico das Blades; depois os especiais.
- **Aceite:** combo básico e 3 especiais com animação do Kratos, acertando inimigos no tempo certo.

### Fase 6 — Gameplay via DLL (REA)
- Estudar o executável com REA + Ghidra, partindo das estruturas do DDMK. Cada achado em `docs/re/`
  com endereço, evidência e hash do executável.
- Implementar na DLL: barra de magia e consumo; efeitos de Medusa's Gaze e Army of Hades; agarrão;
  alcance da corrente das Blades; ajustes do Rage; ajustes de hitbox dos golpes novos.
- **Aceite:** cada mecânica testada isoladamente numa missão, com flag para ligar/desligar na DLL.

### Fase 7 — HUD
- Etapa 1: troca de texturas. Etapa 2: overlay pela DLL (seção 7.5).
- **Aceite:** HUD do GoW1 completo (vida, magia, Rage, orbs, hits) sem restos do HUD do DMC3.

### Fase 8 — Áudio e texto
- Extrair e converter sons do GoW1; descobrir o formato de áudio do DMC3 HD; substituir SFX e vozes de
  combate; renomear textos de interface e loja.
- **Aceite:** combate soa como GoW1; nenhum "Dante" em menus, loja ou HUD.

### Fase 9 — Cutscenes
Escolha registrada como **D6**:
- (a) manter as cutscenes originais com o Dante;
- (b) troca de personagem nos vídeos com IA, cena a cena (risco: consistência entre cenas);
- (c) re-renderizar no Blender, se os dados de animação das cenas existirem nos arquivos (o jogo traz
  modelos e motions de "demo", ex.: `demo_pl000_00_3.pac`) — verificar.
- **Aceite:** definido junto com a decisão.

### Fase 10 — Empacotamento e campanha completa
- `build/make_patch.py` gera patches `xdelta3` + script de instalação que extrai assets da ISO do usuário.
- Playtest das 20 missões, checklist em `docs/playtest.md` (crash, animação, HUD, áudio, progressão).
- **Aceite:** campanha completa jogável do início ao fim com o Kratos.

---

## 9. Riscos e pontos de decisão

| Risco | Impacto | Mitigação |
|---|---|---|
| Não existir forma de exportar `.mod` | Bloqueia o projeto | Fase 2 é gate; escrever exportador a partir do importador |
| Limites de ossos/vértices do formato | Kratos simplificado | Descobrir limites na Fase 2; decimar malha |
| Animações do GoW quebrarem hitboxes | Golpes não acertam | Manter duração original; ajustes finos via DLL |
| Endereços mudarem com update da Steam | DLL quebra | Hash travado; downpatch do DDMK |
| Cutscenes em vídeo | Dante continua na história | Decisão D6 na Fase 9 |
| Formato de som desconhecido | Atraso na Fase 8 | Investigar cedo, em paralelo |
| Questões legais | Derrubada do mod | Regras 2 e 3 da seção 2 |

**Decisões pendentes:** D1 (slot das Blades), D2 (estilos), D3 (recarga da magia), D4 (níveis de arma),
D5 (controles), D6 (cutscenes).

---

## 10. Uso do REA

- Alvo: **apenas** o executável do DMC3 (PE x86_64). Não tente abrir ELFs de PS2 no REA.
- Fluxo: `open_binary` com caminho absoluto e `provider_id: "ghidra"` → localizar funções a partir de
  strings, das estruturas/offsets do DDMK (`Mary/Vars.ixx`, `Scripts/dmc3_create_data.js`) e de referências
  cruzadas → registrar em `docs/re/<tema>.md`:

```
## <nome da função/estrutura>
- endereço: 0x...
- hash do executável: <sha256>
- evidência: <pseudocódigo resumido / xref / string / teste>
- status: confirmado | [HIPÓTESE]
```

- CLI equivalente: `rea analyze <exe> --provider ghidra --json` e `rea function <exe> <nome|endereço> --provider ghidra --json`.
- No Windows o Ghidra do REA não aceita MIPS; rode tudo pelo WSL.

---

## 11. Convenções

- Python: tipagem, `pathlib`, sem caminhos fixos no código (ler de `config/paths.env`); testes com `pytest`.
- Scripts do Blender rodam headless e recebem argumentos depois de `--`.
- C++: C++20, CMake, MSVC; toda funcionalidade da DLL com flag de ligar/desligar em arquivo `.ini`.
- Commits pequenos, em português, no formato `tipo(escopo): descrição` (ex.: `feat(afs): repack com round-trip`).
- Documente formatos enquanto descobre, não depois.
- Ao final de cada sessão: atualizar `docs/LOG.md` e a seção **Estado atual**.

---

## 12. Estado atual

- **Fase:** 0 — em andamento
- **Último passo concluído:** estrutura do repo, `.gitignore`, `config/paths.env`, permissões do agente; `vendor/` com DDMK 2.7.3 (+ hdc_patches), god_of_war_browser beta4 (win32), DMC3-Blender-Import-Addon, xdelta3 3.1.0 (exe)
- **Próxima tarefa:** backup do dmc3.exe/dmcLauncher.exe em `work/backup/` + downpatch e DDMK (com confirmação do LG); inventário do `dmc3-0.nbz`; god_of_war_browser na ISO; REA no dmc3.exe
- **Nota:** o jogo fica na raiz do projeto (não na pasta Steam); tratar como somente leitura (deny em `.claude/settings.json`)
- **Decisões tomadas:** nenhuma
- **Decisões pendentes:** D1, D2, D3, D4, D5, D6
- **Achado:** no HD, `GData.afs` é uma pasta dentro do ZIP `data/dmc3/dmc3-0.nbz` (ver `docs/formats/nbz.md`); a Fase 1 deve tratar zip + pac, não AFS.
- **Bloqueios:** nenhum. Ferramentas instaladas; REA (`npx rea-agents setup`) fica para quando o `dmc3.exe` estiver disponível
