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

> **Revisão 1 (2026-10-20):** plano revisto após descobrir o layout real do HD Collection (sem AFS solto) e o
> projeto **DMC3 Crimson** (código aberto, zlib, ativo). Mudanças em §3, §4, §6, §8, §9 e decisões D7–D9.

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

- **Windows + WSL.** O Claude Code roda no WSL. O jogo está **na raiz do projeto**:
  `./Devil May Cry HD Collection/` (cópia trazida de outro HD; a pasta Steam está vazia). Caminhos de todas
  as ferramentas em `config/paths.env`; versões e hashes em `docs/ambiente.md`.
- **Dados do DMC3 no HD Collection** (confirmado, ver `docs/formats/nbz.md`): não existe `GData.afs` solto.
  `data/dmc3/dmc3-0.nbz` é um **ZIP** com a pasta `GData.afs/` (4334 arquivos já separados: `pl000.pac`,
  `pl000_00_*.pac`, `plwp_*.pac`...). Música fica em `data/dmc3/afs/sound/*.ogg`. Áudio do port usa FMOD
  (`fmod64.dll`, `fmodstudio64.dll`).
- **Pasta de override:** DDMK e Crimson leem `data/dmc3/GData.afs/<arquivo>` solto antes de recorrer ao
  `.nbz` (evidência: `vendor/ddmk/Mary/File.ixx`, `FileManager::Push`/`ExtractFile`;
  `vendor/DMC3-Crimson/src/CrimsonFileHandling.cpp`, `Paths::gameMods`). **Confirmado pelo T1:** vale para o
  modelo do jogador (`pl000.pac`). Missão 1 tem Dante sem camisa; testar modelo a partir da Missão 2.
- Executável: `dmc3.exe` (hash original em `docs/ambiente.md`).
- Programas Windows são chamados a partir do WSL pelo `.exe` direto ou via `powershell.exe -Command`.
- **Blender 5.2.2** headless: `"$BLENDER_EXE" -b -P blender/scripts/<script>.py -- <args>`.
- **Python 3.12** para as ferramentas (`tools/.venv`). Rodar scripts que leem arquivos extraídos com `python -I`.
- **C++ / MSVC 14.44 + CMake 3.31** (VS 2022 Build Tools), compilado do lado Windows.
- **Ghidra 12.1.4 + JDK 21** em `vendor/` (WSL) para o REA.
- **7-Zip** (Windows) para listar/extrair `.7z`, `.iso` e `.nbz`.
- **ISO do GoW1:** `iso/gow1.iso`, NTSC-U `SCUS_973.99` v1.00, DVD dupla camada.

---

## 4. Ferramentas externas

Baixar em `vendor/` (gitignored). Não copiar código de projetos sem licença para dentro do repositório.

| Ferramenta | Para quê | Origem / licença |
|---|---|---|
| Devil May Cry HD Collection | Base jogável | Steam |
| **DMC3 Crimson** (Berthrage & C-Team) | **Base do código do mod (D7).** Sucessor ativo do DDMK, mesmo núcleo (`src/` em C++/CMake). Já traz: troca de personagem/arma/estilo, **golpes novos**, **HUD próprio com pacotes em `Crimson\huds`**, sons próprios em `Crimson\sound`, roda de armas, leitura da pasta de override. `Research/` tem tabelas do Cheat Engine, ReClass, FakePDB e notas de RE (efeitos, sons, crazy combos) | github.com/berthrage/DMC3-Crimson — zlib. Release 0.5a (2026-05-27) |
| DDMK (serpentiem) | **Referência.** Parado; Crimson é o sucessor. Mantido para consulta (`Mary/Vars.ixx`, `Scripts/dmc3_create_data.js`, enums `MOTION_GROUP_DANTE::*`). Downpatch só se o Crimson exigir | github.com/serpentiem/ddmk — zlib |
| **god_of_war_browser** (mogaika) | Extrai o GoW1 direto da ISO: modelos (`mdl`, `mesh` → glTF/FBX), animações (`anm`), texturas (`txr`), UI/HUD (`flp`), som (`sbk`, a verificar). Uso: `-iso "<ISO>" -ps ps2 -gowversion 1`, web em `http://127.0.0.1:8000/`. Release beta4 em `vendor/gowb_release/`; se faltar algo, compilar do fonte (Go) | github.com/mogaika/god_of_war_browser — **sem licença**: só como ferramenta |
| **DMC3-Blender-Import-Addon** (HansLichtner) | Importa `.mod`, `.scm`, `.mot` (e texturas `tm2`→dds) no Blender. **Só importa.** Base do nosso exportador (`DMC3/model.py` 788 linhas, `DMC3/motion.py`) | github.com/HansLichtner/DMC3-Blender-Import-Addon — MIT (fork de deshayu/DMC3HDC-Import-Tools e igrbn/DMC1-3_Blender_Tools) |
| DMC-3-HDC .pac Unpacker | Referência de formato PAC (scripts Python 2 antigos com GUI) | Nexus Mods (DMC HD Collection, mod 438) |
| REA (morluto) | MCP de engenharia reversa no `dmc3.exe` com Ghidra. Usar os símbolos do FakePDB do Crimson | github.com/morluto/rea — MIT |
| ghidra-emotionengine-reloaded | Só se precisarmos ler o ELF do GoW1 (timings, alcance da corrente) | github.com/chaoticgd/ghidra-emotionengine-reloaded |
| PCSX2 | Rodar o GoW1 original para gravar referência de golpes, timings e HUD | pcsx2.net |
| xdelta3 | Patches por arquivo na distribuição | github.com/jmacd/xdelta-gpl |

**Pesquisa feita (2026-10-20):** não existe ferramenta pública que **exporte** `.mod` do DMC3. Trocas de
modelo da comunidade (tutorial "Model Swapping" do Infernal Warks) só trocam modelos que já estão no jogo, ou
são de mods cujo processo não é público. O exportador continua sendo o gate crítico (Fase 2).

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
│   ├── formats/               # um .md por formato: nbz.md, pac.md, mod.md, mot.md, gow-*.md
│   ├── re/                    # achados de engenharia reversa do executável (endereço + evidência)
│   └── design/
│       ├── moveset-gow1.md    # levantamento completo dos golpes do Kratos
│       ├── controles.md       # esquema de controles GoW1 x DMC3 e decisão final
│       └── hud.md             # elementos do HUD do GoW1 e plano de implementação
├── mapping/
│   ├── moveset.yaml           # golpe GoW1 -> slot/motion do DMC3
│   ├── weapons.yaml           # arma/magia GoW1 -> arma/estilo do DMC3
│   └── files.yaml             # arquivo do DMC3 -> substituto
├── tools/                     # Python: pac.py, nbz_inventory.py, mod_export.py, mot_export.py
├── blender/
│   └── scripts/               # retarget, re-skin, export headless
├── dll/crimson/               # submódulo: nosso fork do DMC3 Crimson (modo Kratos)
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

1. **Dados (assets) — pasta de override (D8).** Os `.pac` substitutos (modelo `pl000*`, Devil Trigger,
   armas `plwp_*.pac`, motions `pl000_00_*.pac`, texturas, HUD, sons) vão soltos em
   `data/dmc3/GData.afs/`. **Não reempacotamos o `.nbz`**, e o jogo volta ao original apagando a pasta.
   Plano B, se T1 falhar: gerar um `.nbz` novo (ZIP) com os arquivos trocados, numa cópia. Ferramentas
   necessárias: `pac.py` (unpack/repack de PAC), exportador `.mod` e `.mot`. AFS sai do escopo.
2. **Código — fork do Crimson (D7).** Branch própria do Crimson com um "modo Kratos" de flags
   ligáveis em config. Aproveitamos o que ele já tem: sistema de golpes novos, HUD customizável, sons
   próprios, troca de arma/estilo, roda de armas, ImGui. Escrevemos só o que falta: barra de magia,
   magias (petrificação, almas teleguiadas), agarrão, alcance da corrente, regras do Rage.
   O fork mora em `dll/crimson/` como submódulo git apontando para o nosso fork (não copiamos o código para
   dentro do repo principal).
3. **Cutscenes (vídeo)** — muitas cutscenes do HD são vídeos (`data/dmc3/Video`?). Trocar modelo não muda
   os vídeos. Fase 9.

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
por que foi aceito diferente. Ordem pensada para provar cedo os dois riscos que podem matar o projeto:
carregar arquivos trocados (T1) e exportar `.mod` (Fase 2).

### Fase 0 — Setup e reconhecimento (em andamento)
- ✅ Estrutura do repo, `.gitignore`, `config/paths.env`, ferramentas instaladas, hashes do jogo e da ISO.
- Backup de `dmc3.exe`, `dmcLauncher.exe` e `dmc3-0.nbz` em `work/backup/` com hash.
- Instalar o **Crimson 0.5a** e confirmar que o jogo abre (registrar se exigiu downpatch e o hash do exe
  resultante — esse hash passa a ser o "travado").
- **Teste T1 (override):** copiar um `.pac` de outro modelo que já existe no jogo (ex.: outra roupa do
  Dante) com o nome `pl000.pac` para `data/dmc3/GData.afs/` → Dante aparece trocado na Missão 1.
  Testar também com uma motion (`pl000_00_*.pac`) e uma arma (`plwp_sword.pac`). Resultado em `docs/LOG.md`.
- Inventário do `.nbz` → `extracted/dmc3/inventory.csv` + `docs/formats/nbz.md` (nomes, tamanhos, tipo pela
  assinatura). Identificar arquivos do Dante, armas, motions, HUD, efeitos e sons.
- god_of_war_browser na ISO: exportar o Kratos (modelo + esqueleto + texturas) e 3 animações para glTF em
  `extracted/gow1/`; abrir no Blender headless e contar ossos/vértices.
- Contar cutscenes em vídeo vs. em motor → `docs/design/cutscenes.md`.
- REA + Ghidra no `dmc3.exe`, carregando os símbolos do FakePDB do Crimson.
- **Aceite:** T1 com resultado registrado; inventário; Kratos aberto no Blender com esqueleto; REA analisando
  o exe com símbolos.

### Fase 1 — PAC
- `tools/pac.py` (unpack/repack) com testes em `tests/`, documentado em `docs/formats/pac.md`.
- Mapear o conteúdo de `pl000.pac` (modelo, texturas `tm2/ptx`, física do casaco etc.) e de `plwp_*.pac`.
- **Aceite:** repack sem alterações idêntico byte a byte; o mesmo arquivo reempacotado carrega pela pasta
  de override sem diferença.

### Fase 2 — Exportador `.mod` — **GATE CRÍTICO**
- Exportador Blender a partir de `DMC3/model.py` (MIT). Começar pelo round-trip do Dante.
- **Aceite:** importar o Dante, exportar sem mudanças → arquivo idêntico (ou equivalente provado in-game);
  depois mover vértices e ver a mudança in-game. Descobrir e documentar limites (ossos por vértice,
  vértices por malha, número de texturas).
- Se falhar: parar e reavaliar com o LG.

### Fase 3 — Kratos visual (MVP)
- Re-skin da malha do Kratos no **esqueleto do Dante** (nomes, contagem e ordem de ossos do `.mod`). Ossos
  do casaco: sem pesos ou usados no saiote. Texturas do Kratos convertidas para o formato do DMC3.
- Substituir modelo do Dante e modelo de Devil Trigger (Kratos com efeito de Rage), pela pasta de override.
- **Aceite:** Missões 1 a 3 com o Kratos, animações do Dante funcionando, sem crash e sem deformação grave.

### Fase 4 — Armas visuais
- Blades of Chaos no slot de D1; Blade of Artemis no slot Rebellion; texturas.
- **Aceite:** as duas armas corretas nas mãos em idle, combo e troca de arma.

### Fase 5 — Animações e golpes
- Levantamento do moveset (seção 7.3) e gravação de referência no PCSX2.
- Exportador `.mot` (a partir de `DMC3/motion.py`), com round-trip.
- Retarget GoW1 → esqueleto do Dante mantendo a duração de cada motion substituída.
- Ordem: idle, corrida, pulo, combo básico das Blades; depois especiais.
- Golpes sem slot equivalente: estudar como o Crimson adiciona "New Moves" e reaproveitar esse caminho.
- **Aceite:** combo básico e 3 especiais com animação do Kratos, acertando no tempo certo.

### Fase 6 — Gameplay no fork do Crimson
- Partir do `Research/` e do código do Crimson; REA só para o que não estiver mapeado. Achados em `docs/re/`.
- Implementar com flag cada uma: barra de magia e consumo; Medusa's Gaze; Army of Hades; agarrão; alcance da
  corrente; regras do Rage; hitboxes dos golpes novos.
- **Aceite:** cada mecânica testada isoladamente numa missão, ligável/desligável.

### Fase 7 — HUD
- Etapa 1: **pacote de HUD do Crimson** (`Crimson\huds`) com a arte do GoW1 extraída dos `flp/txr`
  — verificar o formato dos pacotes. Etapa 2: elementos que não existem (barra de magia, contador de hits)
  no `CrimsonHUD` do fork.
- **Aceite:** HUD do GoW1 completo (vida, magia, Rage, orbs, hits) sem restos do HUD do DMC3.

### Fase 8 — Áudio e texto
- Extrair sons do GoW1; descobrir como o port toca SFX (FMOD + `snd_*.pac`?) e como o Crimson injeta sons
  (`Crimson\sound`); trocar SFX e vozes de combate; renomear textos de interface e loja.
- **Aceite:** combate soa como GoW1; nenhum "Dante" em menus, loja ou HUD.

### Fase 9 — Cutscenes
Igual à proposta anterior: **D6** entre (a) manter, (b) troca por IA nos vídeos, (c) re-render no Blender
a partir de `demo_pl000_*.pac` — verificar se os dados de cena existem.

### Fase 10 — Empacotamento e campanha completa
- Distribuição = build do fork do Crimson + script que lê o `.nbz` e a ISO **do usuário** e gera os
  arquivos da pasta de override (patches `xdelta3` por arquivo onde houver base no DMC3; conversão direta
  da ISO para o que vier do GoW1). Nenhum asset hospedado.
- Playtest das 20 missões, checklist em `docs/playtest.md`.
- **Aceite:** campanha completa jogável do início ao fim com o Kratos.

---

## 9. Riscos e pontos de decisão

| Risco | Impacto | Mitigação |
|---|---|---|
| Não existir forma de exportar `.mod` (confirmado: não há ferramenta pública) | Bloqueia o projeto | Fase 2 é gate; escrever a partir do importador MIT |
| Pasta de override não valer para os arquivos do jogador | Volta a precisar reempacotar | T1 na Fase 0; plano B = novo `.nbz` (ZIP) |
| Crimson já trazer `pl000.pac`/arquivos próprios na pasta de override (há relatos de conflito pl000 × Crimson) | Nossos arquivos colidem com os dele | Listar o que o Crimson instala; mesclar ou desligar a opção que usa o arquivo |
| Crimson mudar muito o gameplay | Kratos com mecânicas de DMC4/5 | Usar Game Mode "Vanilla" como base; desligar recursos sem relação |
| Atualização do Crimson quebrar o fork | Retrabalho | Fork travado numa tag; rebase só quando valer a pena |
| Limites de ossos/vértices do formato | Kratos simplificado | Descobrir na Fase 2; decimar malha |
| Animações do GoW quebrarem hitboxes | Golpes não acertam | Manter duração original; ajustes no fork |
| Update da Steam mudar o exe | Endereços quebram | Hash travado; cópia do jogo fora da Steam |
| Cutscenes em vídeo | Dante na história | D6 na Fase 9 |
| Questões legais | Derrubada do mod | Regras 2 e 3 |

**Decisões pendentes:** D1 (slot das Blades), D2 (estilos), D3 (recarga da magia), D4 (níveis de arma),
D5 (controles), D6 (cutscenes). **Tomadas:** D7, D8, D9 (ver `docs/decisoes.md`).

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
- C++: segue o estilo do Crimson no fork (C++20, CMake, MSVC); toda funcionalidade do modo Kratos com flag de ligar/desligar na config.
- Commits pequenos, em português, no formato `tipo(escopo): descrição` (ex.: `feat(pac): repack com round-trip`).
- Documente formatos enquanto descobre, não depois.
- Ao final de cada sessão: atualizar `docs/LOG.md` e a seção **Estado atual**.

---

## 12. Estado atual

- **Data:** 2026-10-23. **Fases:** 0–2 concluídas; 3 (visual) e 4 (armas) funcionais com polimento pendente;
  5 (animações) e 6 (código, fork do Crimson) em andamento. Detalhe de cada teste em `docs/LOG.md` (T1…T53).
- **Build travada:** Steam 2018 + Crimson 0.5a, exe ASLR off `e454272e…dd082` (D10). Crimson.dll do jogo = **nosso
  fork** (`dll/crimson`, branch `kratos`, tag base V0.5a); original em `work/backup/crimson_override/Crimson.dll.release-0.5a`.
- **Instalado no override (`data/dmc3/GData.afs/`):** `pl000.pac` = `work/install/kratos_v10` (24 ossos; lâminas e
  correntes no corpo nos ossos 23/4, fio girado com `--flip-edge`), `plwp_sword.pac` = `kratos_v5` (Rebellion
  escondida), `plwp_sword2.pac` escondido (versão pós-Missão 7), `pl005.pac` = `work/install/kratos_dt_v1` (DT da
  Rebellion = Kratos dourado, asas escondidas), `plwp_gun/shotgun/laser/rifle/nunchaku/guitar/fight.pac` escondidos (`work/install/weapons_hidden_v1`), 37 coleções de motion = `work/install/motions_v19`. Config
  `Crimson/configs/KratosConfig.json`: enabled, chainHitbox, leftHitbox, reachRadius 4 (raio das esferas de ataque com a corrente estendida), virtualPad (testes em segundo plano).
  Crimson: skipIntro e skipCutscenes ligados. Backups de tudo em `work/backup/crimson_override/`.
- **Instalar tudo de uma vez (T52):** `tools/install_all.sh` (override), `--check` compara, `--restore` devolve os
  originais do Crimson; mais `tools/install_sounds.sh`, `tools/install_hud.sh` e `tools/win/install_crimson_dll.sh`.
- **Pipeline (regerar tudo):**
  1. `python -I tools/kratos_fit.py extracted/gow1/hero0/hero_obj.glb extracted/dmc3/unpacked/crimson_pl000 work/install/kratos_vN/pl000.pac --left-weapon extracted/gow1/weapons/maiblade.glb --both-hands --blade-bones --flip-edge`
     DT: mesmo comando com base `extracted/dmc3/unpacked/crimson_pl005`, saída `pl005.pac` e `--hide 002.MOD,004.MOD --tint 1,0.75,0.2,0.35`
  2. `python -I tools/build_motions.py work/backup/crimson_override work/install/motions_vN --model work/install/kratos_vN/pl000.pac` (tabela em `mapping/motions.yaml`)
  3. DLL: editar `dll/crimson/src/KratosMode.cpp`, `cmd.exe /c tools\win\build_crimson.bat`, `tools/win/install_crimson_dll.sh` (jogo fechado)
  4. Teste automático: `tools/win/to_mission.sh` (abre o jogo, carrega o slot 2 = início da Missão 3, ~75 s) e
     `tools/win/burst.sh "<teclas>" <n> <ms> <nome>` + `tools/win/zoom.py` (I = ataque, K = pulo/confirmar,
     L = cancelar, Enter = Start, WASD = mover; o 1º avanço dispara a cena de entrada dos inimigos).
     **Em segundo plano (padrão, T25):** `"virtualPad": true` no KratosConfig → teclas viram controle virtual e as
     capturas saem do back buffer pela DLL; o LG usa o PC normalmente. Desligar para o LG jogar com controle.
  5. Teste de acerto: `tools/win/combo_test.sh <nome>` + `python -I tools/win/damage_report.py work/shots/<nome>_kratos.txt`
     (exige `logDamage: true` no KratosConfig e, para não morrer, `playerReceivedDmgMult: 0` no
     CrimsonConfigGameplay — **não** usar `infiniteHP`, que zera o dano dos inimigos; restaurar depois).
- **Regras descobertas (não violar):** jogador = no máximo **24 ossos** por modelo (docs/re/jogador.md); objetos
  0–19 do corpo são ligados/desligados pelo jogo → reservados vazios; MOD precisa da cauda e do ponteiro de índices
  (docs/formats/mod.md); motions novas em HERMITE_I16 com bit 15 no tempo (docs/formats/mot.md); osso 0 = deslocamento
  do golpe (copiar do Dante); toda motion precisa das trilhas das lâminas (ossos 23/4), senão o osso fica parado onde
  a anterior deixou; **o jogo começa a tocar a motion no `play_start` (MOT 0x08)** — golpe trocado usa
  `timing: strike` (golpe do Kratos no quadro do golpe do Dante), senão o golpe some e não acerta; o acerto são 3
  esferas presas à matriz `ator + 0x80E40` e só dá dano com a mão varrendo na janela do golpe; golpe rápido usa
  cápsula (modo 4) fora do gancho do Crimson, então mexer na posição não adianta — o alcance vem do **raio**
  devolvido por `InterceptingCollisions` (`reachRadius`).
- **Fase 6/7 (T26–T30):** Artemis no slot Agni & Rudra; magia = barra da DLL (`magic`), cada arma de fogo é uma magia
  (E&I Zeus, Shotgun Poseidon, Spiral Medusa = petrifica com `speedMultiplier` 0, Artemis Hades) com custo e dano
  próprios; tiro bloqueado sem magia (detour em dmc3.exe+1EBCF0); magia volta por dano (D3 provisória); HUD do GoW1
  desenhado (`gowHud`). Flags de teste: `testWeapons`, `testRangedWeapon`, `testDevilTrigger`, `testStyle`.
- **T31–T34:** sons do GoW1 (`sounds`; `tools/install_sounds.sh` → `Crimson\sound\kratos`; voz do Dante = canal FMOD
  COMMON mudo); DT do Kratos em todas as armas (`work/install/kratos_dt_v2`); agarrão no taunt (`grab`, motion 2/0–1 =
  `grab`, motions_v13; mata pelo dano do jogo, detour em dmc3.exe+88190, atacante = ator + 0x60); magia, Medusa e
  agarrão valem para qualquer inimigo (vida pelo detour de dano).
- **T35–T38:** passos do GoW1; HUD com a arte do GoW1 (`tools/install_hud.sh`, TXR_HUD029 = lâmina); pedra da Medusa só
  com efeito fraco (pendente: tingir o modelo); textos: `msg_eng.pac` = `work/install/text_v1` (`tools/build_text.py`,
  base = msg do Crimson) e `renameUi` troca os nomes na interface ImGui do Crimson. **Antes de copiar para o override,
  conferir se o arquivo já existe lá (o Crimson instala vários) e fazer backup.**
- **T41–T42:** `tools/win/playtest.sh <missão>` (Arcade do Crimson, direto na missão): M1–M20 sem queda. Roupas do
  Dante = arquivos próprios (pl011 sem casaco, pl013 rasgada — usada da M8 em diante —, pl015/pl016 DMC1, pl018
  Sparda): todas com o Kratos (`work/install/kratos_costumes_v1`).
- **Config ao fechar a sessão de 2026-10-23:** flags de teste desligadas (`logDamage`, `testWeapons`,
  `testDevilTrigger`, `testStyle -1`, `testCostume -1`), dano recebido restaurado, Arcade desligado. Ligados:
  enabled, chainHitbox, leftHitbox, reachRadius 4, magic, gowHud, sounds, grab, renameUi, **virtualPad** (o controle
  físico 1 fica ignorado; desligar para jogar com controle).
- **Pendências (por prioridade):**
  1. **LG, de ouvido/olho:** volume e taxa das vozes do GoW1 (22050 Hz é [HIPÓTESE]); se a voz do Dante sumiu
     (canal COMMON mudo); alcance/dano com `reachRadius 4`; tom do HUD e do DT dourado.
  2. **Playtest:** feito para as 20 missões e 14 chefes (T41, T43; `BOSS=1 tools/win/playtest.sh`), sem queda. Falta:
     multiplicador das magias nos chefes (o dano deles não passa pelo hook) e rotina que alcance M4/M8/M16.
  3. **Visual das magias:** pedra da Medusa (tingir o ModelData: precisa do offset por tipo de inimigo, T39); almas do
     Army of Hades; efeito do Poseidon.
  4. **Golpes:** Aerial Rave 13/9–13/10 ainda não visto no ar; mais golpes do Swordmaster com trava + direção; outras
     armas (Cerberus, Nevan, Beowulf) ainda com as motions do Dante; DT de Cerberus/Nevan/Beowulf/Sparda não visto.
  5. **HUD:** layout exato pelo `FLP_HUD`; retrato do Dante na tela STATUS da pausa e outros menus nativos (texturas).
  6. **Texto:** diálogos da história (`mNN_*_msg_*`, Fase 9).
  7. **Decisões abertas:** D2 (estilos; provisório: Trickster rolamento, Royalguard bloqueio, Swordmaster especiais,
     Gunslinger magias), D3 (recarga da magia; provisório: por dano), D4 (níveis de arma = loja), D5 (botões do DMC3),
     D6 (cutscenes) — registrar em `docs/decisoes.md` quando o LG confirmar.
  8. **Fase 9 (cutscenes) e Fase 10 (distribuição: patches xdelta + scripts que extraem da ISO do usuário).**
- **Como trabalhar (LG, 2026-10-22):** o agente implementa **e roda os testes sozinho** com `tools/win/`, em segundo
  plano (`virtualPad`, T25), sem tomar o teclado nem a tela do LG; pedir teste ao LG só quando a automação não
  alcançar. Juntar mudanças por teste.
- **Decisões tomadas:** D1 (Blades no slot Rebellion), D7, D8, D9, D10. **Pendentes:** D2–D6.
- **REA:** instalado (`vendor/rea_cli`, CLI 6.7.0) e usado via ponte stdio (docs/re/jogador.md).
