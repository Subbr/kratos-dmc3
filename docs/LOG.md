# LOG

## 2026-10-20
- Feito: estrutura do repositório, `.gitignore`, `config/paths.env`, permissões do agente em `.claude/settings.json`.
- Ambiente: WSL com git, python 3.12.3, node 22.23.2. Faltam: java/JDK 21, xdelta3, 7z, cmake (WSL), Blender, Ghidra, PCSX2.
- Instalação Steam em `D:\SteamLibrary\...\Devil May Cry HD Collection` está vazia (só `Installer`); o LG vai copiar o jogo de outro HD para a raiz do projeto.
- Próximo: receber cópia do DMC HD e a ISO do GoW1 em `iso/`; calcular hashes; DDMK + downpatch.
- Instalados: Blender 5.2.2, PCSX2, VS 2022 Build Tools (MSVC 14.44 + CMake 3.31.6) via winget; JDK 21 e Ghidra 12.1.4 no WSL em `vendor/` (sem sudo). Caminhos em `config/paths.env`.
- DMC HD copiado para a raiz. Hashes de `dmc3.exe`, `dmcLauncher.exe` e `dmc3-0.nbz` registrados em `docs/ambiente.md`.
- Achado: não existe `GData.afs` solto no HD; `data/dmc3/dmc3-0.nbz` é um ZIP com `GData.afs/` (4334 arquivos). Ver `docs/formats/nbz.md`.
- ISO do GoW1 veio em `God of War.7z` (7z legítimo: só `God of War.iso` + `readme.html`, sem executável). Instalado 7-Zip; ISO extraída para `iso/gow1.iso` (NTSC-U SCUS_973.99 v1.00). readme.html não extraído.
- Próximo: backup + downpatch/DDMK (pedir confirmação), god_of_war_browser na ISO, REA no dmc3.exe.
- Revisão 1 do plano: pesquisa mostrou que (1) DDMK/Crimson leem `data/dmc3/GData.afs/` solto antes do nbz; (2) Crimson (zlib, ativo) é base melhor que DDMK; (3) não existe exportador público de `.mod`. CLAUDE.md §3, §4, §6, §8, §9 reescritas; decisões D7–D9 em `docs/decisoes.md`. Crimson clonado em `vendor/DMC3-Crimson`.
- Backup de `dmc3.exe`, `dmcLauncher.exe`, `dmc3-0.nbz` em `work/backup/` (hashes em `work/backup/SHA256SUMS`, iguais aos de `docs/ambiente.md`).
- Crimson 0.5a extraído na pasta do jogo (1211 arquivos; 406 em `data/dmc3/GData.afs/`, incluindo `pl000.pac` próprio e `pl000_00_3.pac`). HUDs são `id100.pac`/`id100V.pac` em `Crimson/huds/<nome>/`.
- **Falha:** `apply_patch.bat` do Crimson não aplica. `xdelta3`: "target window checksum mismatch". O patch espera o `dmc3.exe` "original steam" (fonte ≥ 6.567.320 bytes); o nosso tem 6.790.632 bytes (update da Steam de set/2026). Mesmo problema com o downpatch do DDMK 2.7.3. Exe e launcher foram restaurados pelo script (hashes conferidos).
- Testado `hdc_patches_2026.zip` (fork ProjectXsent/ddmk, de terceiro): o launcher sai idêntico ao do DDMK 2.7.3 (adler32 BE2F9BE2 confere), mas o `dmc3.exe` sai com adler32 09BF3785 ≠ 97803703 do DDMK oficial → binário de origem não verificável. **Descartado** (arquivo apagado) e não executado. O script dele também altera `steam_api64.dll`.
- Caminho escolhido: baixar a build antiga oficial pela Steam (`download_depot 631510 631511 7469687047717691926`, manifest pré-update de 2023, fonte: discussão na Steam) e aplicar o patch do Crimson, que valida por checksum.
- Inventário do nbz: `tools/nbz_inventory.py` → `extracted/dmc3/inventory.csv` (4333 arquivos; .pac com magic `PAC` 3513 / `PNST` 212; HUD = `id100.pac`).
- god_of_war_browser compilado do fonte (beta4 não tem `-iso`). Kratos exportado do `R_HERO0.WAD` para glTF com 111 ossos, 7418 vértices e 251 animações com nome; importado no Blender 5.2 headless (`blender/scripts/inspect_gltf.py`). Ver `docs/formats/gow-wad.md`.
- REA adiado até o exe final (os endereços dependem do hash).
- Cutscenes: 30 .webm em `data/dmc3/Video` (12 de missão). O resto da história deve rodar no motor [HIPÓTESE]. Ver `docs/design/cutscenes.md`.
- `download_depot 631510 631511 7469687047717691926` (LG) baixa a build de **lançamento** (PE timestamp 2018-03-23): `dmc3.exe` 6.356.432 bytes, sha256 `4ae4bb5c…40c0a0`; `dmcLauncher.exe` 1.111.504 bytes. O patch do Crimson não aplica nela (a origem esperada tem 6.567.320 bytes, uma build intermediária).
- **Achado (evidência):** o `dmc3.exe` final do Crimson = exe de 2018 com `DllCharacteristics` 0x8160 → 0x8120 (bit DYNAMIC_BASE/ASLR desligado), checksum PE inalterado. Tamanho (6.356.432) e adler32 (0x7D3B3019) iguais ao alvo declarado em `__new_diff_dmc3.exe.bin`. Candidato em `work/exe_chain/dmc3_crimson_candidate.exe`.
- Launcher: o alvo do Crimson (1.115.776 bytes, adler32 BE2F9BE2) é igual ao launcher do DDMK 2.7.3; não deriva do launcher de 2018.
- Depot de 2018 completo (267 arquivos; vídeos .wmv em vez de .webm). `testzip` do nbz ok; dados iguais aos de 2026, exceto 5 `msg_*.pac`.
- Pasta do jogo trocada: 2026+Crimson → `work/backup/game_2026/`; build de 2018 → `./Devil May Cry HD Collection/`. Backup do exe/launcher de 2018 em `work/backup/game_2018/`. Exe com ASLR desligado gerado em `work/install/dmc3.exe` (confere com o alvo do Crimson).
- Pendente: escrever na pasta do jogo (Crimson + exe), bloqueado pela regra de proteção em `.claude/settings.json` → pedir ao LG.
- Crimson instalado pelo LG na build de 2018 (exe ASLR off conferido, `steam_appid.txt`). Aguardando teste de abertura.
- Fase 1: `tools/pac.py` + `tests/test_pac.py`. Round-trip byte a byte em 3725/3725 .pac (alinhamento 8 ou 16 por arquivo). Ver `docs/formats/pac.md`.
- Jogo abre com Crimson (tela de Game Mode). Escolha do LG: **Vanilla Mode**.
- Permissões (pelo LG, `tools/apply_settings_override.py`): liberada escrita só em `data/dmc3/GData.afs/` e `Crimson/`; resto da pasta do jogo continua bloqueado.
- Crimson tem `pl000.pac` próprio (552.496 B, sha256 `be0b5417…`) ≠ original (1.335.280 B). Backup em `work/backup/crimson_override/`.
- **T1 aplicado:** `pl015.pac` (Dante DMC1, versão do Crimson) copiado como `pl000.pac` no override. Aguardando teste in-game.
- **T1 PASSOU (2026-10-20):** com `pl015.pac` copiado como `pl000.pac` em `data/dmc3/GData.afs/`, o Dante aparece com o visual do DMC1 na Missão 2 (Vanilla Mode, Classic, Fixed Camera). Na Missão 1 o Dante fica sem camisa, então ela não serve para testar o modelo. `pl000.pac` do Crimson restaurado depois do teste (sha256 `be0b5417…`).
- Fase 2: `tools/mod.py` lê e reconstrói do zero 6474/6474 MODs do jogo + 2 do Crimson, byte a byte. Ver `docs/formats/mod.md`.
- **T2 aplicado:** `pl000.pac` do Crimson com cabeça e cabelo (objetos 10–16) escalados 1,5× a partir de (0, 169, 0), gerado por `mod.py` + `pac.py` (sha256 `fa385ce9…`). Aguardando teste in-game (Missão 2+).
- **T2 PASSOU (2026-10-20):** Dante com cabeça e cabelo 1,5× maiores in-game, sem crash e sem malha quebrada. Leve deformação, provavelmente nos vértices do pescoço com peso dividido. Conclusão: as posições do MOD estão em espaço do modelo (pose de bind) [INFERIDO: se fossem locais ao osso, a escala em torno de (0,169,0) teria deslocado a cabeça inteira]. **Gate da Fase 2 vencido.** `pl000.pac` do Crimson restaurado.
- Fase 3: `tools/tex.py` (bloco de texturas: round-trip em 5667/5667; descritor gerado = original), `tools/gltf.py`, `tools/kratos_fit.py` + `mapping/skeleton_kratos_dante.yaml`. O casaco do Dante é o `012.MOD` (33 ossos, física `pl000_02.clt`); o corpo é o `001.MOD` (24 ossos).
- Ajuste: cada osso do Kratos recebe uma transformação (translação, rotação de direção e esticamento) que leva o seu segmento ao osso equivalente do Dante (escala 4,8; giro de 180° em Y). Os 111 ossos viram 24. Triângulos gravados um a um (strip com reinício). Texturas 256×256 em DXT5 com 1 mip. Casaco colapsado num ponto.
- Prévia em `work/preview/fit_v1.png`: Kratos em pose T alinhado ao Dante.
- **T3 aplicado:** `work/install/kratos_v1/pl000.pac` no override. Aguardando teste in-game.
- **T3 FALHOU:** crash logo após a cutscene inicial da missão. Isolando: T3a = só texturas do Kratos (modelo do Crimson); T3b = só o corpo do Kratos dividido em malhas de ≤900 vértices (20 objetos), texturas do Crimson, casaco colapsado. T3a instalado.
- T3a PASSOU: texturas do Kratos (DXT5, 1 mip, descritor gerado) carregam sem crash no modelo do Dante. Causa do crash do T3 está na geometria. T3b instalado.
- **Causa provável do crash do T3:** a cauda do MOD não é lixo. É a área de trabalho onde o jogo converte strips em índices: tamanho = Σ align16(6 × (vértices − 2)) por malha (confirmado em 6474/6474 MODs). O T3 foi sem cauda e com 3× mais vértices. `Model.runtime_tail()` + teste. Variante B (sem cauda) pulada.
- **Kratos v2 instalado:** corpo em 20 objetos (≤900 vértices por malha), cauda correta, texturas do Kratos, casaco colapsado.
- **v2:** sem crash (a cauda resolveu), mas o corpo ficou invisível e o casaco apareceu como um pano flutuando.
- **Achado:** reserved[1] da malha (o antigo "uk") é o ponteiro relativo do cabeçalho da malha até o seu trecho de índices na cauda: `início da cauda + Σ align16(6 × (vc − 2)) anteriores − endereço do cabeçalho`. Recalculado pelo `mod.py` e conferido em 6474/6474 MODs (+ 2 do Crimson). Com 0, o jogo lê índices errados e não desenha.
- Casaco: colapsar posições não funciona (a física de tecido reposiciona). Agora todos os vértices do 012 recebem o bit de reinício → zero triângulos.
- **Kratos v3 instalado.**
- `mod.py`: o parse detecta se o arquivo segue a regra original do ponteiro de índices (o Crimson reserva mais espaço por malha) e preserva o valor lido quando não segue. Round-trip de novo 100% (jogo + Crimson). v3 regenerado: o casaco mantém os ponteiros do Crimson.
- **T3 / Kratos v3 PASSOU (2026-10-20):** Kratos visível in-game no lugar do Dante, com texturas corretas, animando com o esqueleto do Dante e sem crash. Polimentos pendentes (print do LG): peça da canela solta/deslocada numa perna, rosto com aparência estranha (sombra/normais?), revisar deformação nas animações.
- Fase 4: armas do GoW1 em `R_WPN{nível}_{roupa}.WAD`. `maiblade` = Blade of Chaos nível 1; `maigodblade` = nível máximo (textura de fogo). A Blade of Artemis ainda não foi localizada.
- Rebellion (`plwp_sword.pac` do Crimson): 4 objetos, 2 ossos, todos os vértices no osso 1, lâmina em +Z e cabo na origem. `tools/weapon_fit.py`: arma do GoW1 com escala 4,8, giro de 180° em Y e 90° no eixo da lâmina.
- **T4 aplicado:** Blade of Chaos no lugar da Rebellion (só a mão direita). Backup do `plwp_sword.pac` do Crimson em `work/backup/crimson_override/`.
- **T4 PASSOU (2026-10-21):** Blade of Chaos na mão direita, bem orientada, também nas costas quando guardada. Pendências: o rastro (trail) do golpe usa o comprimento da Rebellion e parece uma espada maior; Ebony & Ivory visíveis no quadril; dedos da mão esquerda parecem separados da palma.
- `lWeapIH` (osso da arma na mão esquerda do Kratos) fica na palma. `kratos_fit.py --left-weapon`: a lâmina vai no modelo do corpo, posicionada pela pose do `lWeapIH`, com o mesmo ajuste do osso, peso no osso 13 do Dante e textura no 4º slot. Prévia em `work/preview/fit_v4.png`.
- `tools/hide_models.py`: esconde todos os MODs de um PAC. Aplicado ao `plwp_gun.pac` (Ebony & Ivory), com backup do original do Crimson.
- **T5 aplicado:** Kratos v4 (com a lâmina esquerda) + pistolas escondidas.
- **T5 PASSOU (2026-10-21):** duas Blades of Chaos (direita = slot Rebellion; esquerda presa à mão no modelo do corpo) e pistolas invisíveis. A lâmina direita vai para as costas quando guardada; a esquerda fica sempre na mão.
- **Blade of Artemis localizada:** objeto `athenablade` em `ATHN08C.WAD` (espada grande com guarda em cruz; textura de rastro `Blade_swordtrailTex`). Os `sword1` de ATHN07/08 são espadas de cenário (estátuas). `maigodblade` = Blades of Chaos no nível máximo, não Artemis.
- Agni & Rudra (`plwp_2sword.pac`): 3 ossos; cada espada num osso (1 e 2), um por mão. O motor suporta arma com peça em cada mão.
- Artemis gerada para o slot Agni & Rudra no osso 1 (a outra espada some): `work/install/artemis_v1/plwp_2sword.pac`. Não instalada: a Agni & Rudra só é obtida no fim da Missão 3.
- R_PERM.WAD tem `MDL_HUD` e os orbs (health/magic/weapon) → fonte da Fase 7.
- **T6 aplicado (temporário):** Blade of Artemis no slot Rebellion, só para ver o modelo in-game. Depois volta `work/install/blades_v1/plwp_sword.pac`.
- **T6 PASSOU (2026-10-21):** Blade of Artemis no slot Rebellion aparece nas costas, é sacada e golpeia normalmente. Tamanho conferido nos modelos do GoW1: `athenablade` mede 38,5 unidades de comprimento e o Kratos 37,2 de altura (bounding box dos glb). Como os dois usam a mesma escala (4,8), a proporção in-game é a do GoW1. A lâmina esquerda das Blades continua na mão (esperado: está no modelo do corpo). `plwp_sword.pac` restaurado para `work/install/blades_v1/` (sha `d4b477e3…`).
- Próximo: prova de ponta a ponta da Fase 5 (uma animação do Kratos no lugar de uma motion do Dante), antes de mais polimento visual.
- Fase 5 iniciada. `tools/mot.py`: leitor/escritor de MOT, round-trip 12181/12181 (`tests/test_mot.py`). Formato em `docs/formats/mot.md` (máscara de canais por osso, 4 compressões, rotação em radianos, esqueleto do Dante sem rotação de repouso).
- `tools/anim_retarget.py`: animação do Kratos (glb) → motion do Dante. Cada osso do Dante gira para apontar onde o osso equivalente do Kratos aponta (usa a mesma rotação de ajuste do `kratos_fit`); quadril recebe a translação da pelve; duração da motion original mantida. Prévia `work/preview/anim_v1_idle.png`: malha do Kratos posada pela motion nova = guarda de combate do GoW1.
- **T7 aplicado:** `pl000_00_0.pac` #0 (idle do Dante, 105 frames) = `idleCombat` do Kratos esticado para 106 frames. Backup do original em `work/backup/crimson_override/pl000_00_0.pac`.
- **T7 FALHOU (2026-10-21):** a parada continuou a do Dante e a coxa direita do Kratos ficou invisível. Causa provável: usei compressão LINEAR_I16 com o bit 15 do tempo ligado. As motions do Dante usam só HERMITE_I16 (31689 tracks; as 21 LINEAR_I16 do jogo têm o bit 15 desligado), então o jogo deve ter lido tempos absurdos.
- `mot.Track.hermite`: track nova HERMITE_I16, uma chave por frame, tangentes por diferença central (unidade por frame, conferida com as tangentes do idle original), bit 15 ligado como no Dante. `anim_retarget.py` usa este tipo.
- Achado: deslocamento de golpe (root motion) fica no osso 0 (TX/TZ), ex.: `pl000_00_9.pac` #9 anda 183 unidades.
- **T7b aplicado:** `idleCombat` (HERMITE_I16) nos itens #0, #1, #10 e #58 do `pl000_00_0.pac` (candidatos a parada; cada um com a sua duração). sha `2609d04b…`.
- **T7b PASSOU em parte (2026-10-21):** o Kratos fica na guarda de combate do GoW1 quando parado → **gravar motion nova funciona** (HERMITE_I16). Problemas: a mão direita fica vazia (a arma do slot Rebellion vai para as costas na parada do DMC3) e a coxa direita continua invisível.
- Coxa direita: malha, pesos, orientação dos triângulos e transparência da textura iguais aos da coxa esquerda (conferido). Quase todos os triângulos dela estão no objeto 5 do `001.MOD`. [HIPÓTESE] o jogo liga/desliga objetos do corpo do Dante pelo índice (como a camisa na Missão 1); a "peça da canela solta" do v3 era o mesmo sintoma (joelheira sem a coxa). Descartado: limite de 8 ossos por objeto (modelos do jogo têm objetos com até 37).
- `kratos_fit.py`: os primeiros N objetos (N = objetos do modelo base, 20 no Crimson) viram objetos vazios e o Kratos começa no índice N. `--both-hands`: a lâmina também no `rWeapIH` (osso 9), no corpo.
- **T8 aplicado:** Kratos v5 (objetos reservados + lâmina nas duas mãos, sempre visíveis) e `plwp_sword.pac` com os modelos escondidos (a arma do slot Rebellion não aparece mais nas costas). Motion de parada do T7b mantida.
- **T8 PASSOU (2026-10-21):** coxa direita visível (os objetos 0–19 do Dante eram escondidos/ligados pelo jogo; reservar os índices resolveu), lâminas nas duas mãos, nada nas costas. Pistolas invisíveis (escondidas de propósito no T5).
- **Teste automático (2026-10-21):** `tools/win/` abre o jogo, carrega o save do slot 2 (Missão 3) e captura só a janela do jogo (`game.ps1`: SendInput com scancode, foco via AttachThreadInput, captura por área da janela, DPI por monitor). Teclas: Enter = Start, K = A (confirmar/pular), L = B (cancelar), I = ataque, A/D = esquerda/direita. `to_mission.sh` (≈75 s) verifica o slot e o diálogo pela imagem (`load_slot.py`). `burst.sh` + `zoom.py`: captura em sequência. Crimson: `skipIntro` e `skipCutscenes` ligados (backup da config em `work/backup/crimson_override/`).
- Rebellion (`pl000_00_3.pac`): combo 1 = motions 3→4→5 (`CrimsonFX.cpp:467`: COMBO_1_PART_1 usa a motion 3; combo 2 PART_2 = 6). Deslocamento do golpe no osso 0 (TZ acumulado no combo). O GoW1 não move a raiz (`main` parado).
- `anim_retarget.py --timing natural`: animação a 60 fps sem esticar, último quadro parado até o fim da motion do Dante; osso 0 copiado da motion original (mantém deslocamento e alcance).
- **T9 PASSOU (verificado por captura):** combo da Rebellion com `combo3A/B/C` do Kratos (3,4,5), combo 2 com `combo3D/E` (6,7), guarda com arma (0,1) = `idleCombat`. Os golpes aparecem com as poses do GoW1 e o rastro da arma; depois ele volta à guarda de combate. Prévia `work/preview/combo_v1_ingame.png`.
- `mapping/motions.yaml` + `tools/build_motions.py`: tabela motion do Dante → animação do Kratos, gera os `pl000_00_N.pac`. `tools/motion_sheet.py`: folha de quadros (motions do jogo ou do GoW1) para identificar golpes. Índices e evidências em `docs/formats/mot.md`.
- Corrigido: o item 10 da BASE é "levantar do chão" (tinha recebido a parada no T7b); voltou ao original.
- **T10 aplicado (teste do LG):** corrida (`walkBlend2`), aterrissagem (`land`), pose no ar (`jumpAir`), rolamentos com a mira travada (`evadeLeft/Right`), Stinger (`dash`), lançador (`blockLauncher`, índice inferido), mais o combo do T9. sha `0734635b…` (00_0) e `de83709d…` (00_3).
- **T10 (LG, 2026-10-21):** corrida ok; golpes acertam no tempo certo; lançador com a pose certa, mas não lança o inimigo e o dano parece estranho; desliza ao começar a andar devagar.
- Deslize: o item 1 da BASE é a **caminhada** (pés alternam, osso 0 TZ +214), não parada; recebia `idleCombat` desde o T7b → agora `walkBlend1`.
- Lançador: o golpe para cima do Dante (#13) é no quadro 24 e o do `blockLauncher` no 41 (maior velocidade da mão). [HIPÓTESE] o acerto segue a arma presa à mão, então golpe fora de tempo erra a janela de lançar. `anim_retarget --timing strike`: alinha o quadro de maior velocidade da mão do Kratos ao do Dante (antes dele o tempo é ajustado, depois segue a 60 fps). Aplicado ao lançador (#13) e ao Stinger (#16); combos mantidos em `natural` (aprovados no teste).
- **T11 aplicado:** caminhada + lançador e Stinger alinhados.
- **T11 (LG):** caminhada sem deslize; lançador funciona (visto em jogo). Dano: inimigos morrem mais rápido, alguns golpes acertam de longe, inimigo reage normalmente. [HIPÓTESE] o acerto segue a arma do slot (Rebellion, invisível mas presa à mão 9): os braços do Kratos abrem mais e a Rebellion é longa, então o alcance e o número de acertos sobem. Polir junto com as correntes (Fase 6).
- Correntes: nas 251 animações do glb as lâminas nunca saem da mão (`rWeapIH` a 1,5 do pulso em todos os golpes); `rWeapOH`/`rChainW` só giram; o WAD das armas não tem ANM. [HIPÓTESE] o voo das lâminas é procedural no GoW1 ou fica em dados do ANM que o gowb não exporta. Correntes no DMC3 = código (Fase 6).
- Fase 6 iniciada. Fork do Crimson em `dll/crimson` (clone da tag `V0.5a`, branch `kratos`; repositório próprio, fora do git principal até existir o fork no GitHub). Compila com `tools/win/build_crimson.bat` (MSVC 14.44, CMake 3.31) → `build/bin/Release/Crimson.dll`. REA não instalado: o Crimson já mapeia o necessário (`PlayerActorDataBase::modelData[3]` 0x200, `weaponDataAddr[5]` 0x64A0, `WeaponData::weaponCDraw` 0x130, `ModelData::bonesMatrixesPtr` 0x208; matriz 4×4 com a posição em [12..14]; gancho por quadro `TriggerOnTickFuncs` em `dmc3.exe+4F23B`).
- `KratosMode` (src/KratosMode.cpp): flags em `Crimson/configs/KratosConfig.json`. Teste T12: soma 60 ao Y do cabo da arma do slot Rebellion (só se o jogo recalculou a matriz) e grava `logs/kratos.txt` com as matrizes da mão (osso 9) e do cabo.
- Kratos v6: lâmina esquerda no corpo; a direita volta a ser a arma do slot (`blades_v1/plwp_sword.pac`, visível), para a DLL poder movê-la.
- **T12 preparado:** falta instalar o `Crimson.dll` do fork na raiz do jogo (fora da pasta liberada para escrita): `tools/win/install_crimson_dll.sh` (backup do original em `work/backup/crimson_override/`).
- **T12 (LG):** lâmina não flutuou, mas o acerto nos inimigos ficou estranho. Log (`logs/kratos.txt`): matrizes em espaço de mundo; o jogo recalcula a matriz da arma a cada quadro (101/116); a escrita no OnTick afeta o **acerto** mas não o **desenho** → o acerto usa a matriz do osso da arma, e o desenho é recalculado depois do OnTick. Confirma a hipótese do dano do T11.
- Com a arma na mão, arma = translação(-7.6, -3.0, -1.0) · mão (constante em todos os golpes). Essa translação está numa tabela em `.data` do `dmc3.exe` (gravável): 7 entradas com (-7.6, -3, -1), RVAs 0x5796B0, 0x58BF90, 0x58BFF0, 0x58D250, 0x58D910, 0x58D940, 0x58D970 (algumas com rotação −π). [HIPÓTESE] tabela de pontos de encaixe por arma/estado.
- **T13 aplicado:** a DLL soma 20·(k+1) ao Y de cada entrada k; o log mostra qual entrada move a lâmina e se a tabela é lida a cada quadro.
- **T13 (LG):** nada visível mudou. Log: o encaixe da arma passou a (-7.6, **37**, -1) = entrada 1 (RVA **0x58BF90**, +40) → o jogo lê a tabela a cada quadro para a matriz lógica da arma (a que o acerto usa), mas o **desenho da arma não usa essa matriz** (caminho de render ainda desconhecido).
- Nova estratégia para o visual das correntes: lâminas no modelo do corpo, em 2 ossos novos (24 = lâmina direita, filho da mão 9; 25 = esquerda, filho de 13), movidos pelas motions. Acerto: matriz lógica da arma pela DLL (T12/T13).
- Esqueleto: o 3º array (antes "children") marca a parte superior do corpo (1 no tronco e braços, 0 nas pernas). MOT: cabeçalho = align16(0x1E + 2·ossos) em todas as motions do jogo (até 118 ossos); 0x1A = 0 ou o número de ossos. `Motion.resize_bones`.
- `kratos_fit.py --blade-bones`: ossos 24 (lâmina direita, filho de 9) e 25 (esquerda, filho de 13) no encaixe do `rWeapIH`/`lWeapIH`; lâminas com peso total nesses ossos. Kratos v7 = 26 ossos, round-trip ok.
- **T14 aplicado:** Kratos v7 (26 ossos, as duas lâminas no corpo), arma do slot escondida, parada (#0 da BASE) com 26 ossos e as lâminas saindo 80 unidades da mão e voltando em loop (`tools/blade_test.py`). KratosMode desligado.
- **T14 (LG):** nos golpes as lâminas saíram da mão "como no GoW" (as motions de golpe não tinham trilha dos ossos novos e as lâminas ficaram onde a parada as deixou); parado/correndo a extensão não ficou boa. Conclusão: **motion move as lâminas no desenho** — base das correntes.
- `tools/blade_chain.py` + `build_motions.py --blades`: as 37 coleções de motion do jogador (pl000_00_*, new*, demo_*) ficam com 26 ossos; lâminas em repouso, exceto no grupo das Blades (00_3, 00_13, demo_00_3): cada lâmina sai até 120 unidades ao longo do antebraço quando a mão dela passa de 55% da velocidade máxima (rampa de 8 quadros).
- `kratos_fit.py`: corrente = tubo de 4 lados da mão até o encaixe, peso (1−t) na mão e t no osso da lâmina (estica junto). Kratos v8.
- DLL `chainHitbox`: soma à matriz lógica da arma do slot o deslocamento do osso 24 em relação ao repouso (offset · mão) → o acerto acompanha a lâmina direita.
- **T15 aplicado:** v8 + motions_v3 (37 arquivos) + DLL com chainHitbox + arma do slot escondida.
- **T15 FALHOU (2026-10-21):** crash ao carregar o save. Dump: escrita em 0xFA a partir de `dmc3.exe+0x30F902`. REA (Ghidra): `FUN_14030f850(esqueleto, modelo, nós)` monta um nó por osso até `modelo+0xEA` (número de ossos do MOD); a lista de nós vem de `FUN_1401ef040` e fica no ator em +0x1880/+0x1940/+0x1A00/+0x1AC0, espaçadas 0xC0 = **24 ponteiros por modelo**. Com 26 ossos os ossos 24/25 invadem a lista seguinte (no T14 funcionou por acaso, corrompendo os nós do modelo de DT). **Limite: 24 ossos no modelo do jogador.**
- Jogo restaurado ao estado seguro: Kratos v5 (24 ossos, lâminas no corpo), motions_v2 (00_0, 00_3), demais motions do Crimson, KratosMode desligado.
- Ossos reaproveitados (limite de 24): **23** (ponta da cabeça, 0 vértices) = lâmina direita, filho de 9; **4** (pescoço) = lâmina esquerda, filho de 13; cabeça (5) filha do peito (3) com offset = offset4 + offset5; pesos do pescoço → peito. Ordem do esqueleto refeita (pai antes do filho). `kratos_fit.blade_cfg` / `repurpose_blade_bones`. Kratos v9.
- Motions do Dante no esqueleto novo: R5' = R4·R5 e T5' = T4 + R4·T5 por quadro (`blade_chain.fold_neck_into_head`); conferido por FK em 5 motions: diferença máxima 0,0001 nos ossos (exceto 4/23). `build_motions.py --model` gera as 37 coleções (motions_v4).
- DLL: `chainHitbox` no osso 23.
- **T16 aplicado:** Kratos v9 + motions_v4 + DLL (chainHitbox).
- **T16 (LG):** carregou sem crash, nada solto, correntes saem e voltam (sutil), inimigos levam dano. Problemas: lâminas "invertidas" (aguardando print), parada pisca ao reiniciar o loop.
- Loop: último quadro ≠ primeiro (parada: quadril 0,66 e ~7° no braço; corrida: quadril 8,6). `anim_retarget.close_loop`: nos 20 quadros finais cada trilha converge (smoothstep) para o primeiro quadro; `loop: true` no motions.yaml (paradas, caminhada, corrida, guarda). Alcance: 120 → 200, limiar 0,55 → 0,40, rampa 8 → 12.
- **T17 aplicado:** motions_v5.
- **T17 (LG, 2026-10-22):** loop e correntes ok; o fio das lâminas está virado para cima; alguns golpes não acertam; o resto ok.
- Sessão encerrada com estado salvo em CLAUDE.md §12 e `docs/re/jogador.md`. Próximo: girar a lâmina 180° no eixo do comprimento; acerto dos golpes; testes automáticos pelo agente.

## 2026-10-22 — T18 (agente, testes automáticos)
- Fio das lâminas: `kratos_fit --flip-edge` gira cada lâmina 180° no eixo do comprimento (Z local do `maiblade.glb`;
  `ROT_Z180`). Kratos v10. Comparação v9 × v10 de frente: `work/shots/t18_fio_v9_v10.png` (v9: gancho largo para
  cima; v10: para baixo/fora). As motions não mudam com o v10 (offsets das lâminas iguais).
- Teste de acerto automático: `tools/win/combo_test.sh <nome>` (Missão 3, chama os inimigos, 8 combos) +
  `tools/win/damage_report.py`. DLL `logDamage`: registra troca de motion e cada queda de `hitPointsHells`.
  Para o Kratos não morrer: `playerReceivedDmgMult = 0` durante o teste (o `infiniteHP` do Crimson é "Disable All
  Damage" e zera o dano dos inimigos também). Config original restaurada no fim.
- Achado 1: só o 3/5 (combo 1, golpe 3) e o 3/7 não acertavam. Dante 3/5: 4 de 4 execuções com dano; Kratos com motions v5/v7: 5 danos em ~52 execuções (somando as variações de DLL).
  Teste cruzado (Kratos em tudo, 3/5 do Dante): 3/5 acerta 3/3 → a causa é a animação do 3/5.
- Achado 2: MOT 0x08 = `play_start`, o jogo começa a tocar ali (3/5 = 40, 3/7 = 75). O golpe do Kratos
  (`timing: natural`, quadros 20–38) nunca aparecia; a mão ficava parada na janela de acerto. Ver docs/formats/mot.md.
- Achado 3: volume de acerto = 3 esferas (raio 40) presas à matriz `ator + 0x80E40`, não à matriz de desenho da
  arma. Ver docs/re/jogador.md. Escrever a posição das esferas no gancho não muda o dano (teste do ímã).
- Correção: `timing: strike` começa em `play_start`, golpe do Kratos no quadro do golpe do Dante, preparação no
  máximo 2× mais rápida. Combo 3–7 passa para `strike`. motions_v8 (só `pl000_00_3` muda).
- Resultado (3/5): v8 acerta quando há inimigo a menos de ~60 da esfera (3 de 4 casos; v8_1 sem inimigo perto);
  3/7 acertou pela 1ª vez. Totais por rodada 13–20, faixa do Dante (16–23).
- `chainSpheres` (esferas ao longo da corrente): 10/19 contra 5/14 sem, dentro do ruído, e o ímã indica que a escrita
  não vale → **desligado**, [HIPÓTESE] não confirmada. `chainHitbox` agora orienta o cabo pela corrente (efeito no
  acerto não provado: as esferas seguem 0x80E40). `leftHitbox` liga a esquerda com margem de 20.
- Instalado: Kratos v10, motions_v8, Crimson.dll do fork (chainHitbox + leftHitbox).
- Próximo: alcance da corrente no acerto — repetir o ímã na matriz `ator + 0x80E40` com motions_v8 (mão em
  movimento); se o dano seguir, esticar as esferas pela corrente escrevendo nessa matriz.

## 2026-10-22 — T19 (agente): alcance da corrente no acerto
- Desmonte de `dmc3.exe+2CCB60`: a esfera = `matrix1 × files+0x10` (raio = `files+0x20 × [+0x1C]`). Modo 2 = esfera
  parada, grava o raio em `2CCC98` (onde fica o gancho do Crimson); modo 4 = cápsula do quadro anterior ao atual
  quando a esfera anda > 2× o raio, caminho **sem** gancho. Explica o T18: escrever a posição no gancho não muda
  golpes rápidos.
- Escrever a matriz de origem (`ator + 0x80E40`) no OnTick: ímã 19 danos, alcance pela corrente 14/28 com alcance
  igual ao da base (mediana 112–114) → não chega ao teste; código removido.
- **Raio devolvido pelo gancho** (mesmo caminho do High Time do Yamato no Crimson), flag `reachRadius`, só nas
  esferas de ataque e com a corrente estendida. Dose-resposta (2 rodadas cada, `combo_test.sh`, dano com distância
  jogador–inimigo):
  | raio | danos | alcance mediano | acertos > 200 |
  |---|---|---|---|
  | 1× | 15–17 | 112 | 1 |
  | 2,5× | 21, 21 | 113–140 | 1, 4 |
  | 4× | 28, 29 | 174–201 | 11, 15 |
- Instalado `reachRadius: 4` (p90 ~300 ≈ corrente 200 + braço). Verificação com a DLL limpa: 25 danos, mediana 190,
  3/7 com 4 danos. `chainSpheres` removido.
- Próximo: LG jogar e dizer se o alcance/dano ficou bom (pode ficar forte demais: ajustar `reachRadius`).

## 2026-10-22 — T20 (agente): golpe aéreo para baixo
- Pulo + ataque toca a motion **3/10** (log `play motion`, `combo_test.sh t20_air`): 82 f, começa no ar e termina em pé
  depois de um corte para baixo (folha `work/shots/t20_sheet_dante.png`).
- `anim_retarget.KratosAnim` aceita animações encadeadas com "+". 3/10 = `airImpale+airImpaleLand` (`timing: strike`):
  mergulho, impacto agachado, lâminas abrindo, levanta. motions_v9 (só `pl000_00_3` muda).
- Teste (`combo_test.sh t20_v9air` com 8× "pulo + ataque"): 3/10 tocou 7×, **13 danos**, alcance mediano 160;
  capturas sem pose quebrada (`work/shots/t20_air_zoom.png`).
- Aerial Rave (combo no ar) não saiu pelas teclas automáticas (pulo curto/tempo); fica para depois.

## 2026-10-22 — T21 (agente): rolamento no estilo Trickster
- O save está no estilo **Trickster**: L (botão B) toca a motion **23/0** (grupo 23 = TRICKSTER, `Vars.hpp`), o dash.
  Pelo §7.1 o Trickster é o rolamento do GoW1.
- `pl000_00_23` 0–3 (dash frente/trás/esquerda/direita, osso 0 com 400 de deslocamento) = `evadeFront/Back/Left/Right`
  (`timing: natural`; a 23/0 toca inteira: 117 ticks = 58 quadros). motions_v10 (só `pl000_00_23` muda).
- Captura a cada 40 ms (`work/shots/t21_d_zoom.png`): o Kratos rola para a frente (encolhido, pernas para cima,
  levanta) e volta à guarda; as duas camadas de motion (`motionData[0]` e `[1]`) tocam a 23/0.
- **Crash** (2×, `Crimson.dll+0x3084b1`, dumps em `%LOCALAPPDATA%\CrashDumps`): leitura de inimigo já liberado na
  varredura do `logDamage` quando a missão reinicia. Só acontecia com o log de teste ligado. Correção: `ReadEnemy` com
  SEH (`__try/__except`) em todas as varreduras; removido o diagnóstico de contagem do T18. Sem crash depois.
- Log de troca de motion agora traz a duração da anterior (`after`, ticks) e a camada 1.

## 2026-10-22 — T22 (agente): Devil Trigger com o Kratos
- Arquivos do DT do Dante (DDMK `devilFileIdsDante`): `pl005` Rebellion, `pl006` Cerberus, `pl007` Agni & Rudra,
  `pl008` Nevan, `pl009` Beowulf, `pl017` Sparda. As Blades estão no slot Rebellion (D1) → `pl005.pac`.
- `pl005.pac` do Crimson (override): 001 corpo (24 ossos, **mesmo esqueleto e hierarquia do `pl000`**), 002 asas
  (9 ossos), 004 membranas (27 ossos), 000 texturas, 006–008 sombras. Repack idêntico byte a byte.
- `kratos_fit.py` ganhou `--hide` (MODs a esconder; padrão `012.MOD`, o casaco) e `--tint r,g,b,força` (mistura cor
  nas texturas). v10 regerado com o código novo: idêntico byte a byte ao instalado.
  DT: `--hide 002.MOD,004.MOD --tint 1,0.75,0.2,0.35` (dourado, como o Rage of the Gods) → `work/install/kratos_dt_v1/pl005.pac`.
- Com o DT liberado o jogo troca `plwp_sword` por **`plwp_sword2`** (Crimson `Actor.cpp`, `sessionData.unlockDevilTrigger`):
  da Missão 8 em diante a Rebellion voltaria. `plwp_sword2.pac` com os modelos escondidos (`hide_models.py`).
- DLL: flag de teste `testDevilTrigger` (liga `sessionData.unlockDevilTrigger`, `dmc3.exe+C8F250+0xD1`, e mantém
  `magicPoints` = `maxMagicPoints` ≥ 3000 no ator). Tecla do DT no teclado = **U** (keybind 1 do Crimson).
- Teste na Missão 3 (com `playerReceivedDmgMult 0`): U ativa o DT (aura vermelha), o Kratos fica dourado com as lâminas,
  sem asas e sem resto do Dante (`work/shots/t22_dt_zoom.png`); combo em DT acerta (`work/shots/t22_dt_combo_sheet.png`);
  U de novo volta ao Kratos normal (`t22_dt_off_sheet.png`). Sem crash.
- Obs.: as teclas automáticas não chegam ao jogo quando o Input Director está com o teclado em outro PC.
- Config final: `testDevilTrigger: false`, `playerReceivedDmgMult` restaurado. `pl005`/`plwp_sword2` ficam instalados.

## 2026-10-22 — T23 (agente): Swordmaster — Aerial Rave e Prop
- No DMC3, pulo + ataque é o Helm Breaker (3/10, T20); o **Aerial Rave é Swordmaster** (DDMK `Actor.ixx`: estilo
  SWORDMASTER + no ar → `REBELLION_AERIAL_RAVE_PART_1`). O save é Trickster e o módulo Actor do Crimson está desligado.
- DLL: flag de teste `testStyle` (STYLE::*, 0 = Swordmaster; −1 = o do save) grava o estilo em `sessionData.style`
  (0xDC) e no ator (`style`, 0x6338). Funciona trocando ao vivo: L passa a tocar o grupo 13 (`pl000_00_13`,
  SWORDMASTER_REBELLION).
- Motions identificadas pelo log (`combo_test.sh t23_sm`): L no chão = **13/19** (Prop); pulo + L L L = **13/7 → 13/8 →
  13/9** (Aerial Rave 1–3; 13/10 = parte 4 pelo enum `REBELLION_AERIAL_RAVE_PART_4` e pela folha). Folha do Dante:
  `work/shots/t23_dante_sm.png`.
- `mapping/motions.yaml` → `pl000_00_13`: 7 `airH1`, 8 `airH2`, 9 `airH3`, 10 `airV1`, 19 `comboLR2` (todas `strike`).
  motions_v11 (só `pl000_00_13` muda). Folha: `work/shots/t23_kratos_sm.png` (correntes esticando).
- Teste igual antes/depois (3× L no chão, 3× pulo + 4 L): Dante retargetado 28 danos, alcance mediano 109;
  **Kratos 28 danos, mediano 154**. 13/7, 13/8 e 13/19 acertam; 13/9 e 13/10 não saíram com o tempo das teclas
  dessa rodada (13/9 saiu 1× na anterior). Capturas: `t23_air_sheet.png`, `t23_prop_sheet.png`.
- Config final: `testStyle: -1` (o jogo usa o estilo do save), `logDamage` desligado, dano recebido restaurado.

## 2026-10-22 — T24 (agente): Royalguard = bloqueio do GoW1
- `testStyle 3` (Royalguard). L segurado/tocado toca **24/0**, **24/2** (bloqueio atingido), **24/30** e **24/31**.
  `pl000_00_24` só tem 21 entradas (original e Crimson), então 30/31 não são entradas do PAC.
- Diagnóstico na DLL (`ScanMotionPointers`, só com `logDamage`): procura no ator (0–0x90000, fora da tabela
  `motionArchives` em +38A0) ponteiros que caem dentro de um PAC de motion. Os ponteiros por osso ficam a partir de
  **ator + 0x20128** e apontam para a entrada tocada. Resultado: **24/30 toca a entrada 0** e **24/31 a entrada 1**
  (24/0 → 0, 24/2 → 2). A duração em `ModelData.Motion.duration` (0x554) fica 0 com o Actor do Crimson desligado.
- Folhas: Dante `work/shots/t24_dante_rg_a.png`/`_b.png` (0 = entrar e segurar a guarda, 1 = soltar, 2 = atingido);
  GoW1 `t24_gow_block.png`, `t24_gow_ber.png` (`berBlockExit` termina na postura do Berserk, descartada).
- `mapping/motions.yaml` → `pl000_00_24`: 0 `block`, 1 `block+idleCombat`, 2 `blockReaction` (`stretch`). motions_v12
  (só `pl000_00_24` muda). Folha: `t24_kratos_rg.png`.
- No jogo: L segurado → Kratos de guarda alta com as lâminas à frente; soltar → volta à postura de combate
  (`work/shots/t24_block_zoom.png`). Log: 24/0 ×6, 24/2 ×1, 24/30 ×4, 24/31 ×6. Missão e ataques normais com a DLL final.
- Pendente: Release do Royalguard (contra-ataque) não testado; parry do GoW1 (`parry01/02`) é candidato.
- Config final: `testStyle -1`, `logDamage` desligado, dano recebido restaurado.

## 2026-10-22 — T25 (agente): testes em segundo plano (controle virtual + captura pela DLL)
- Pedido do LG: rodar os testes sem atrapalhar o uso do PC. Antes, `game.ps1` mandava teclas por `SendInput` e
  capturava a tela, e as duas coisas exigiam o jogo em primeiro plano.
- DLL (`KratosVirtualPad.cpp`, flag `virtualPad`): `game.ps1` grava `Crimson\kratos_script_<id>.txt`. A DLL lê no
  Present, aperta os botões num controle XInput virtual (controle 1) e captura o back buffer (BMP; o `game.ps1`
  converte para PNG). No fim grava `.done`. Cada arquivo é uma trilha própria, então segurar uma tecla e capturar ao
  mesmo tempo continua funcionando.
- Evidência do caminho do XInput: o jogo chama `XInputGetState` pelo salto `jmp [rip+x]` em **dmc3.exe+3453F6**
  (chamadas em +41AFA na abertura e em +41C40 a cada quadro). O byte em **+5D9070 + 0x2C·i** marca o controle i
  conectado quando a chamada devolve 0. O detour do Crimson nesse salto só é instalado com o módulo Actor ligado
  (`InitBindings`), por isso a entrada da tabela de importação é trocada direto (`InstallVirtualPad`, na inicialização
  do Crimson). O `Hook::XI::XInputGetState` do Crimson roda depois e sobrescreve o estado, então também consulta o
  controle virtual. O jogo segue rodando sem foco (`forceWindowFocus`).
- Menus com o controle (diferente do teclado): "Load Successful" fecha com A; o menu da missão anda só no direcional
  e confirma com Start. `to_mission.sh` usa essa sequência quando `virtualPad` está ligado.
- Resultado: `to_mission.sh` e `combo_test.sh t25_vpad` rodaram com o jogo fora de foco (`fg=False`): Missão 3,
  combo, **20 danos** (3/3 ×7, 3/4 ×6, 3/5 ×7). Folha: `work/shots/vp_combo_sheet.png`.
- Limites: ao abrir, o jogo ainda aparece na frente uma vez; o som toca; com `virtualPad` ligado o controle físico 1
  fica ignorado (o teclado continua valendo).

## 2026-10-22 — T26 (agente): Blade of Artemis no slot Agni & Rudra
- DLL: flag `testWeapons` equipa na sessão Rebellion + Agni & Rudra e Ebony & Ivory + Shotgun (ordem do Arcade do
  Crimson, `SessionData.weapons` 0x84) e libera Agni/Shotgun em `weaponAndStyleUnlocks`. Controle virtual: `q`/`e` =
  LT/RT (troca de arma de fogo/corpo a corpo; o jogo testa os gatilhos em dmc3.exe+41D04).
- Override: `plwp_2sword.pac` = `work/install/artemis_v1` (backup do original do Crimson em `crimson_override`).
- No jogo (em segundo plano): RT troca para a Artemis, que aparece dourada na mão direita e golpeia com as motions
  de Agni & Rudra (`work/shots/w_artemis_sheet.png`). As lâminas do Kratos continuam nas mãos (estão no corpo).

## 2026-10-22 — T27 (agente): barra de magia (MVP) com gasto e bloqueio do tiro
- DLL (flag `magic`, `magicShotCost`, `magicRegenPerSecond`): barra própria 0..100, desenhada em azul pelo ImGui
  abaixo da vida (provisória até o HUD do GoW1, Fase 7). Cada tiro gasta `magicShotCost`; sem magia o tiro é bloqueado.
  A recarga é provisória, por tempo (**D3 em aberto**: no GoW1 a magia volta com orbs azuis).
- Evidência (objdump do exe travado): **dmc3.exe+1EBCF0** preenche `ator+0x74E0` com os botões [segurado, anterior,
  apertado, solto] (leitura em +32CC70/+32CC80 do dispositivo em +D54A10). A ação é decidida depois (+1E6A62 testa o
  apertado em +0x74E4). Apagar o bit no `OnTick` chegava tarde: o tiro saía (8/7 depois de "bloqueado"). Com um detour
  em +1EBCF0, que roda o original e depois aplica a magia, os 3 tiros sem magia não geraram 8/7. Log:
  `tiro 75/52/28/5` → `bloqueado 7/8/10`, sem motion de disparo após os bloqueios.
- A captura do controle virtual passou para o fim do Present (depois do ImGui), então a barra aparece nas capturas
  (`work/shots/m_shoot_t.png`).

## 2026-10-22 — T28 (agente): magias por arma, recarga por dano (D3 provisória) e Medusa's Gaze
- Cada arma de fogo é uma magia (§7.1) com custo próprio: E&I = Zeus' Fury (`magicShotCost` 10), Shotgun = Poseidon
  (20), Spiral = Medusa (30), Artemis = Army of Hades (25). No Dante, `rangedWeaponIndex` (ator + 0x6494) guarda o
  próprio `WEAPON::*` da arma ativa (Actor.cpp põe 5 = E&I); o log confirmou 5/6/7/8 ao trocar com LT.
- D3 provisória: magia volta por dano tirado dos inimigos (`magicPerDamage` 0.05 por ponto de vida), sem recarga por tempo.
- `testWeapons` agora também escreve as armas da missão em fila (`[dmc3.exe+C90E30] + 0xC0`, `QueuedMissionActorData`):
  só a sessão não mudava a 2ª arma de fogo. LT percorre todas as armas de fogo liberadas (E&I → Shotgun → Artemis → Spiral).
- **Medusa's Gaze:** tiro da Spiral petrifica os inimigos até `medusaRange` (900) por `medusaSeconds` (5).
  Evidência: zerar só `speed` (+0x14) não parava; zerando também `speedMultiplier` (+0x18) os inimigos congelam no
  meio do golpe e voltam depois de 5 s (`work/shots/md_gaze_sheet.png`; log `pedra 0 speed 0 mult 0`, posição parada).
  O jogo não sobrescreve os dois campos (valor lido no quadro seguinte continua 0). Visual de pedra: pendente.
- Teste com `playerReceivedDmgMult 0` (o Kratos morreu numa rodada com dano normal).

## 2026-10-22 — T29 (agente): dano das magias
- O hook de dano do Crimson (Actor.cpp, ramo "Enemy", ativo mesmo com o módulo Actor desligado) chama
  `KratosMode::OnEnemyDamage`: durante as motions das armas de fogo multiplica o dano por `zeusDamage` (E&I, grupo 8),
  `poseidonDamage` (Shotgun, 9) e `hadesDamage` (Artemis, 10).
- Log: E&I `10 x2` (8/7) em 3 tiros; Shotgun `20 x3` (9/7, 5 bagos) e `5 x3` (9/8). Gasto de magia 9 (E&I) e 20 (Shotgun).

## 2026-10-22 — T30 (agente): HUD do GoW1 desenhado pela DLL (Fase 7, etapa provisória)
- Flag `gowHud`: esconde o HUD principal (`ToggleHideMainHUD`) e o medidor de estilo (`ToggleHideStyleRankHUD`) do
  Crimson e desenha pelo ImGui: vida verde (ator +0x411C/+0x40EC), magia azul (barra do modo Kratos), Rage dourada
  (barra de DT, +0x3EB8/+0x3EBC; só com DT liberado), orbs vermelhos (`[dmc3.exe+C90E30]` + 0x38) e contador de hits
  (cada dano a inimigo no hook do Crimson; zera depois de 2 s). Só aparece em jogo: some quando os botões do ator
  param de ser lidos (pausa, menus, cenas).
- No jogo: `work/shots/h_hud_t.png` (vida, magia, Rage, 6606 orbs, "6 HITS"; sem o "C" do estilo).
- Pendente: arte do GoW1 (molduras `flp`/`txr`) no lugar das barras lisas.

## 2026-10-22 — T31 (agente): sons do GoW1 (Fase 8, MVP)
- Extração (god_of_war_browser na ISO, servidor em 127.0.0.1:8000): `R_PERM.WAD` tag 81 **`Hero`** = 16 VAGs com as
  vozes originais do Kratos (`H_ATTKS1–4` ataque curto, `H_ATTKL1–2` longo, `H_DMG1–6` dano, `JUMPVOC1–2`,
  `DIEVOC1`, `LIFTVOC1`; `/action/R_PERM.WAD/81/wav?snd=<nome>`, PCM mono 14 kHz). Tag 69 **`GENERAL`** = banco SBK
  com 218 sons (whoosh, corrente, `SND_SWORDHIT_*`, `SND_ENEMY_GETHIT_*`, `SND_BLADEBLOCK`, `SND_MEDUSA_*`,
  `SND_BOLT_HIT`, orbs, passos): cada som aponta para amostras ADPCM (`SampleRef.AdpcmOffset/Size`), exportadas com
  `/action/R_PERM.WAD/69/smpd?offset=&size=` (134 WAVs). [HIPÓTESE] a taxa de 22050 Hz que o gowb grava no cabeçalho
  pode não ser a real de cada amostra (o banco tem campo de pitch); conferir de ouvido.
- `tools/install_sounds.sh` copia para `Crimson\sound\kratos\<evento>_<n>.wav` (fora do git). DLL (`KratosSound.cpp`,
  flag `sounds`, `soundVolume`): carrega pelo SDL_mixer do Crimson (`CrimsonSDL::KratosLoadWav/KratosPlay`, canais
  600–679) e sorteia uma variação por evento: golpe corpo a corpo (whoosh + grunhido 30%; 3/5 e 3/7 grunhido longo
  70%), acerto (espada ou raio, no máximo 1 a cada 60 ms), dano recebido, morte, pulo (40%), Medusa (raio, pedra,
  carne), bloqueio atingido (24/2).
- Voz do Dante: `snd_com0.pac` = "Common Dante Default" (Sound.cpp) no canal FMOD **COMMON** (1); com `sounds` o
  canal fica mudo (log do Crimson `SetVolume 1 0` ao entrar na missão). [HIPÓTESE] o canal 1 tem só voz/passos do
  Dante; confirmar de ouvido. Também cala os passos do Dante (trocar só as falas do banco fica para depois).
- Evidência no jogo (log `som <evento>`, sem ouvir): swing 6, hit 6, voice_long 2, voice_short 1, gun_hit 1,
  medusa_shot 1, stone 1, flesh 3. Um "die" falso (vida a 0 ao recriar o ator) → só conta queda < 90% da vida máxima.
- **Pendente (LG, de ouvido):** volume, taxa das amostras, se a voz do Dante sumiu.

## 2026-10-22 — T32 (agente): DT do Kratos em todas as armas
- `pl006` (Cerberus), `pl007` (Agni & Rudra), `pl008` (Nevan), `pl009` (Beowulf) e `pl017` (Sparda) do override do
  Crimson: backup em `crimson_override` (+SHA256SUMS), unpack em `extracted/dmc3/unpacked/crimson_plNNN`, round-trip
  idêntico nos cinco. Extras de cada DT: pl006 002.MOD, pl008 002/004.MOD, pl009 002.MOD; pl007 e pl017 só têm o corpo.
- `kratos_fit.py` com `--hide` = todos os MOD menos o 001 e `--tint 1,0.75,0.2,0.35` → `work/install/kratos_dt_v2/`
  (pl005 copiado do v1). `--hide ""` agora vale (antes caía no padrão 012.MOD, que não existe nesses PACs).
- No jogo: RT para Agni & Rudra (Artemis) + DT → Kratos dourado com a Artemis, combo em DT
  (`work/shots/dt_a1_t.png`, `dt_agni_sheet.png`). Cerberus, Nevan, Beowulf e Sparda instalados, não vistos no jogo
  (armas ainda não equipáveis no save).

## 2026-10-23 — T33 (agente): agarrão do GoW1 no taunt
- O taunt (Back) toca 2/0 ou 2/1; `mapping/motions.yaml` → `pl000_00_2` 0 e 1 = `grab+idleCombat` (`natural`),
  motions_v13 (só `pl000_00_2` muda).
- DLL (flag `grab`, `grabRange` 400, `grabDelay` 0.25, `grabKillFraction` 0.35, `grabDamage` 150): `grabDelay` s
  depois do início do taunt pega o Hell mais perto até `grabRange`; com até 35% da vida ele é finalizado, senão
  perde `grabDamage`.
- Morte (REA, `FUN_140088190` = dano do jogo; o Crimson intercepta em +88512): a função tira a vida em
  `[p1+0x10]+8` e, se ela chega a 0, chama a morte do alvo (`vtable+0x38`). Escrever 0 de fora deixava o inimigo na
  lista (zumbi). Agora um detour na entrada (+88190) guarda por inimigo a estrutura de dano e o último ataque do
  Kratos (atacante = **ator + 0x60**, visto no log). O agarrão deixa a vida em 0.01 e chama a função original com
  esse ataque: a morte sai pelo caminho do jogo (orb vermelho no quadro do agarrão, `work/shots/g_pair.png`).
- Log: `agarrao golpe` (dano) várias vezes, `agarrao finalizou mais perto 3`.

## 2026-10-23 — T34 (agente): magia, Medusa e agarrão valem para qualquer inimigo
- Antes só os Hells (vida em `hitPointsHells`). Agora a vida de cada inimigo vem do detour de dano (T33): o endereço
  que o jogo usa fica dentro do ator (Hells + 0x2E5C), e a maior vida vista antes de um golpe serve de vida máxima
  para o agarrão. A magia volta pelo dano causado (hook de dano do Crimson, depois do multiplicador das magias), sem
  ler vida. A Medusa pega qualquer inimigo pela posição (vida desconhecida conta como vivo).
- Regressão (Missão 3, em segundo plano): Medusa petrificou 6; agarrão finalizou 3 e golpeou 1; a magia voltou a
  100 entre os dois tiros da Spiral; 46 sons; a onda foi limpa.

## 2026-10-23 — T35 (agente): passos e aterrissagem do GoW1
- Com o canal COMMON mudo (T31) os passos do Dante sumiram. A DLL toca `SND_FOOTSTEP_STONEWALK/RUN` do GoW1 a cada
  0,5 s na caminhada (0/1) e 0,32 s na corrida (0/2, 0/51), e `SND_FOOTSTEP_STONELAND` na aterrissagem: **0/6**
  parado e **0/31** depois de pular correndo (log: pulo correndo = 0/4 → 0/31 → 3/0).
- Log: 6 passos de corrida em 2,5 s; 2 aterrissagens em 2 pulos. (O 1º avanço da missão dispara a cena dos inimigos
  e corta o teste: medir depois dela.)

## 2026-10-23 — T36 (agente): arte do GoW1 no HUD
- `R_PERM.WAD` tem o HUD inteiro: `TXR_HUD000–192` (+GFX/PAL) e `FLP_HUD` (layout, não usado ainda). O JSON de cada
  TXR no god_of_war_browser já traz o PNG (base64); 193 exportadas para `extracted/gow1/hud`, folha
  `work/shots/gow_hud_sheet.png`. Peças: **029** = lâmina da Blade of Chaos 256x96 com o medalhão (moldura de vida e
  magia), **014–017** = ícones Poseidon, Medusa, Zeus e Army of Hades, 032–035 = placas do Ω, 163–169 = outros ícones.
- `tools/install_hud.sh` → `Crimson\huds\kratos` (fora do git). DLL: `CreateTexture` do Crimson (stb_image) e
  ImGui: moldura em 2,2× (1080p), vida e magia dentro da lâmina, Rage enchendo o medalhão de dourado, ícone da magia
  da arma de fogo ativa ao lado. Sem os arquivos volta às barras lisas.
- No jogo: `work/shots/hud2_crop.png`. Posição das barras pelo olho; o `FLP_HUD` pode dar o layout exato.

## 2026-10-23 — T37 (agente): efeito de pedra da Medusa (parcial)
- Sem campo de cor por modelo conhecido (nada em `ModelData`/ator no Vars.hpp). Tentativa com o Effekseer do Crimson:
  aura `jdc_charge.efkefc` e explosão `risingstar.efkefc` tingidas de cinza (`SetAllColor`) em cada inimigo
  petrificado; a aura para quando ele volta.
- No jogo (`work/shots/md_stone_sheet.png`): os inimigos congelam, mas o efeito quase não aparece (faíscas azuladas
  nos primeiros quadros). **Resultado fraco**: pedra de verdade pede tingir o modelo (RE do render: constantes de
  cor do material do inimigo). Fica pendente; o código fica (inofensivo).

## 2026-10-23 — T38 (agente): nomes do GoW1 nos textos (Fase 8)
- Textos do jogo: `msg_eng.pac` (interface, itens, ajuda; texto puro com tags `<PS>`, `<BR>`…; comentários em
  Shift-JIS). O override **já tinha o `msg_eng.pac` do Crimson** (68712 bytes, diferente do `.nbz`): sobrescrevi sem
  backup por engano e recuperei o original do pacote `vendor/crimson_release/Crimson-0.5a-pack.rar` (backup em
  `crimson_override` + SHA256SUMS). O round-trip dele não era idêntico (byte 0x14 do preenchimento do cabeçalho = 0x20);
  `tools/pac.py` agora guarda esse preenchimento (`pad_bytes` no pac.json) → idêntico; pytest 10/10.
- `tools/build_text.py`: Dante → Kratos (20) e Devil Trigger → Rage of the Gods (1) em `msg_eng.pac` →
  `work/install/text_v1`. Diálogos da história (`mNN_*_msg_*`) ficam para a Fase 9. Os nomes das armas não aparecem
  nesse arquivo (os menus nativos usam textura).
- A loja/Customize é do Crimson (ImGui, strings no C++). Flag `renameUi`: filtro no texto do ImGui
  (`GImKratosTextFilter` em `ImFont::CalcTextSizeA` e `ImFont::RenderText`, mesma troca para medir e desenhar; os IDs
  não mudam) troca Dante, Rebellion → Blades of Chaos, Agni & Rudra → Blade of Artemis, Ebony & Ivory → Zeus' Fury,
  Shotgun → Poseidon's Rage, Spiral → Medusa's Gaze, Artemis → Army of Hades, Devil Trigger → Rage of the Gods.
  No jogo: `work/shots/cu2_crop.png` (Customize com os nomes do GoW1).
- `to_mission.sh`: `STOP_AT_MENU=1` para no menu da missão (testes de menu).

## 2026-10-23 — T39 (agente): Release do Royalguard e tentativa de tingir os petrificados
- **Release:** com `testStyle 3`, **trava (RB) + trás + L** depois de carregar a guarda bloqueando golpes toca **24/15 →
  24/16** ou **24/15 → 24/45** (45 ≥ 21 entradas: pelo padrão do T24, 30 → 0, 31 → 1, deve ser a entrada 15). Sem
  carga sai só 24/0 + 24/31. `mapping/motions.yaml` → `pl000_00_24` 15 `parry01`, 16 `parry02` (`strike`), motions_v14
  (só `pl000_00_24` muda; `demo_pl000_00_3` difere 1 byte do v13 porque o `pac.py` do T38 agora preserva o
  preenchimento do cabeçalho, igual ao original). No jogo: explosão da Release, Kratos na pose de parry, 6 danos e o
  inimigo morre (`work/shots/rg_rel_sheet.png`).
- **Tingir o modelo (REA):** o clone do Doppelganger usa `FUN_1402f69c0(ModelData + 0x80, RGBA, 1.0)` (flag
  0x10000 em +0xE0, modo 10 em +0xB0, cor em +0xC0..+0xCC; `FUN_140089de0` = +0x80). O ModelData dos inimigos fica
  num offset por tipo (`lea rcx,[reg+X]` antes de +89DE0: 0x80, 0xF80, 0x1EC0, 0x800, 0x1040…). Procurar pelo
  ponteiro de funções do ModelData do jogador (+8 e +0x88) casa com objetos menores espaçados 0x120 (não são
  ModelData): tingir o 1º deixou a foice do Hell cinza; tingir os 8 **derrubou o jogo**. Código de tingimento
  removido; a Medusa fica com congelamento + explosão cinza. Para retomar: achar o ModelData por tipo de inimigo
  (tabela de offsets por id do inimigo).

## 2026-10-23 — T40 (agente): Aerial Rave completo (Swordmaster)
- `testStyle 0`, pulo + L ×4 com intervalos de 180/250/320 ms: o log tem as quatro partes (13/7 ×3, 13/8 ×3,
  **13/9 ×2, 13/10 ×1**) e o Prop (13/19 ×2). Todas usam as motions do Kratos do T23. A captura
  (`work/shots/ar_rave_sheet.png`) pegou o Prop no chão, com as correntes acertando; o quadro aéreo da 13/9 e 13/10
  não foi capturado (o pulo do script em segundo plano não entrou nessa rodada).

## 2026-10-23 — T41 (agente): playtest automático das 20 missões
- `tools/win/playtest.sh <missão>`: o **Arcade do Crimson** (`CrimsonConfig.json` → `Arcade.enable/mission`, armas
  0/2/5/8) abre o jogo direto na missão, sem menus (~30 s). Rotina de combate em 8 fases (andar, combo, pulo + ataque e
  Aerial Rave, bloqueio + agarrão, magias, DT), captura por fase, confere se o processo responde e resume o log. O
  CrimsonConfig volta ao original no fim (backup `crimson_override/CrimsonConfig.json.pre_t41`).
- **Resultado (M1–M20): nenhuma queda nem travamento.** Folhas `work/shots/playtest_sheet_0.png`/`_1.png`; resumo
  em `work/shots/playtest/resumo.txt`. Dano 0 na maioria porque a sala inicial não tem inimigos perto.
- **Achado:** da M8 em diante aparecia o **Dante**. As roupas usam arquivos próprios (`costumeFileIdsDante`: pl000
  padrão, pl011 sem casaco, pl013 rasgada, pl015 DMC1, pl016 DMC1 sem casaco, pl018 Sparda) e as missões seguintes usam
  a rasgada (pl013). Os cinco do override do Crimson: backup + round-trip idêntico, mesma estrutura do pl000.
  `kratos_fit` → `work/install/kratos_costumes_v1/pl011.pac` e `pl013.pac` instalados; M10, M15 e M17 agora com o
  Kratos (`work/shots/pt_zoom3.png`). **pl015/pl016/pl018 falham** no parse do MOD ("seções sobrepostas") — roupas
  opcionais, pendente.

## 2026-10-23 — T42 (agente): Kratos em todas as roupas do Dante
- pl015/pl016/pl018 têm malhas que **compartilham dados** (offset de uma seção antes do fim da anterior); `mod.py`
  agora lê esses MOD sem as lacunas (sem round-trip idêntico, que o `kratos_fit` não usa: ele zera `gaps`). pytest 10/10.
- `work/install/kratos_costumes_v1/pl015.pac`, `pl016.pac`, `pl018.pac` instalados (backups dos originais do Crimson em
  `crimson_override`). Flag de teste `testCostume` (COSTUME::*) na sessão. Arcade M5 com as roupas 3, 4 e 5: Kratos nas três, sem
  queda (`work/shots/costumes.png`). Com o T41, **todas as 6 roupas do Dante** são o Kratos.

## 2026-10-23 — T43 (agente): playtest dos chefes
- `BOSS=1 tools/win/playtest.sh <missão>`: liga o **Boss Rush** do Crimson junto com o Arcade (nasce na sala do chefe);
  rotina de chefe com Stinger (trava + frente + ataque) para fechar a distância, combos, Spiral, agarrão, DT e ataque
  aéreo. O script liga `logDamage` e `playerReceivedDmgMult 0` e devolve os três configs no fim.
- **Achado 1:** o dano dos chefes **não passa pelo hook de dano do Crimson** (Cerberus: 0 acertos no hook, mas a
  barra do chefe cai). Magia (D3), contador de hits, som de impacto e log passaram a usar a **queda de vida** de cada
  inimigo por quadro, com a tabela de vida por tipo do Crimson (`EnemyHp`, igual à vida do alvo travado em
  CrimsonGameplay.cpp: Hells, Cerberus 7200, Gigapede por parte, Geryon/carruagem, Vergil…). O multiplicador das
  magias continua no hook (não vale nos chefes).
- Resultado (M3, 4, 5, 7, 8, 9, 11, 12, 13, 16, 17, 18, 19, 20): **nenhuma queda**; dano em 13 das 14 lutas
  (`work/shots/playtest/chefes.txt`). M8 (coração do Leviathan), M4 (Gigapede na parede) e M16: rotina não alcança o
  alvo (`work/shots/chefes_fracos.png`) — limite do teste, não do mod.
- **Achado 2:** a Medusa petrificava chefes (10 de 14) e o agarrão tirava vida deles. No GoW1 nenhum dos dois pega
  chefe → `IsBoss` exclui Cerberus, Gigapede, Agni & Rudra, Nevan, Geryon, Beowulf, Doppelganger, Arkham, Lady,
  Vergil, Jester e o coração do Leviathan. Reteste M3/M12: `medusa petrificou 0`, `agarrao nada`, dano normal.

## 2026-10-23 — T44 (agente): dano das magias nos chefes
- O dano dos chefes não passa pelo hook (T43). Na queda de vida por quadro (`UpdateSpells`), se o alvo é chefe e a
  motion do Kratos é de arma de fogo, o extra (`mult − 1` × dano) sai direto da vida (`EnemyHp`), sem passar de 1 (a
  morte continua sendo do jogo). Log `magia chefe x2.0 extra 30.0` (Agni & Rudra, M7) e `extra 16.2` ×3 (M11).
  Na fase de gelo do Cerberus os tiros não ferem (sem extra, como deve ser).
- `playtest.sh` (chefe): a fase 0 agora dá 4 tiros de E&I travado.

## 2026-10-23 — T45 (agente): Cerberus, Nevan e Beowulf com o Kratos
- `tools/win/motion_probe.sh <arma>`: Missão 3 com testWeapons; o RT percorre **todas** as armas liberadas
  (Rebellion → Cerberus → Agni → Nevan → Beowulf), então aperta RT N vezes; roda cada comando separado e lista as
  motions. Flag nova `testMeleeWeapon` (e testWeapons libera as cinco).
- Índices: **Cerberus (grupo 4)** combo 3→4→5, pausa 8/10, ar 11, trava + trás 19/24/25; **Nevan (6)** 3/6/9/8/10,
  4, 5, 16 (trás), 15 (ar); **Beowulf (7)** 3→4→5, 25 (ar). `mapping/motions.yaml` → `pl000_00_4/6/7` com os golpes do
  Kratos (`strike`), motions_v15 (só esses três mudam). `plwp_nunchaku/guitar/fight` com os modelos escondidos
  (`work/install/weapons_hidden_v1`, backups em `crimson_override`): o Kratos luta com as lâminas do corpo em qualquer
  arma.
- No jogo: acertos 4 (Cerberus), 7 (Nevan), 3 (Beowulf) num combo; folha `work/shots/t45_weapons.png`. Os raios roxos
  da Nevan continuam (efeito da arma).

## 2026-10-23 — T46 (agente): Blade of Artemis com os golpes "ber*" do GoW1
- As animações `ber*` do glb (berComboH1–H4, V1–V4, Stab, AirH1/H2, berserkEnter/Exit/Idle, berwalk) são de espada a
  duas mãos com a arma no ombro (`work/shots/ber_sheet.png`) — o conjunto da Blade of Artemis. Grupo 5 (Agni & Rudra =
  Artemis, §7.1), índices pela sonda: combo 3→4→5→6→7, trava + frente/trás 20→21, ar 17, parado 0/1.
  `pl000_00_5` → berserkIdle, berComboH1–H4, V1, Stab, V2, AirH1 (`strike`), motions_v16 (só `pl000_00_5` muda).
- No jogo: 6 acertos no combo, golpes largos com a Artemis (`work/shots/probe_w2_sheet.png`). As lâminas continuam
  nas mãos (estão no corpo); no GoW1 iriam para as costas.

## 2026-10-23 — T47 (agente): levantamento das texturas com o Dante nos menus
- Os menus nativos usam texturas DDS dentro dos `id*.pac` (2698 arquivos; sufixos F/G/I/J/S/C/Z = idiomas). Varredura
  das texturas ≥ 256 px dos `idNNNN.pac` (1287) filtrando o vermelho do casaco: `work/shots/id_red.png`. Com o Dante:
  cartas de golpe da loja (`id741`–`id760`, "ACTION" + Dante executando o golpe), título (`id900`: "VERGIL / DANTE" e o
  logo), fim de missão secreta / Dante na poltrona (`id7168`), `id200` (arte do Vergil). O retrato da tela STATUS não
  apareceu no filtro (pode ser o modelo 3D ao vivo).
- Pendente: renderizar o Kratos (glb do GoW1, Blender headless) para cada arte e regravar com `tex.py`
  (`make_texture`), com round-trip primeiro.

## 2026-10-23 — T48 (agente): Swordmaster de Cerberus, Artemis, Nevan e Beowulf
- Sonda com `testStyle 0` (`motion_probe.sh <arma> 0`): Cerberus = grupo 14 (L no chão 0/1, ar 7/8, segurar 10),
  Agni & Rudra/Artemis = 15 (0; ar 4/5), Nevan = 16 (0; ar 7/8), Beowulf = 17 (0; ar 6; segurar 8).
- `pl000_00_14–17` com especiais do Kratos (`comboLR3/4`, `dashMultiStab`, `impaleSlamCharge`, `airH1–3`, `airV1`,
  `airImpale+airImpaleLand`; Artemis: `berComboV3`, `berAirH1/H2`), `strike`; motions_v17 (só esses quatro mudam;
  14/10 não é motion do esqueleto do jogador). No jogo: as motions tocam (log), sem queda.

## 2026-10-23 — T49 (agente): as armas de fogo viram as magias do GoW1 (gestos)
- `tools/win/gun_probe.sh`: um tiro de cada arma no chão, travado e no ar. Disparos: E&I **8/8** (mira travada 8/2,
  recuo 8/5; ar 8/32), Shotgun **9/8** (9/5 antes e depois; ar 9/39), Artemis **10/4** (10/3; ar 10/13), Spiral **11/8**
  (recuo 11/5).
- `mapping/motions.yaml`: só os disparos trocam — Zeus `boltThrow`/`airBoltThrow`, Poseidon `LightningExit`/
  `airLightningStart`, Hades `raiseTheDead`/`airRaiseTheDead`, Medusa `psentHead` (`strike`); motions_v18 (só
  `pl000_00_8–11` mudam). Mira e recuo continuam do Dante.
- Armas de fogo escondidas como a E&I (T7): `plwp_shotgun`, `plwp_laser` (Artemis), `plwp_rifle` (Spiral)
  (`work/install/weapons_hidden_v1`, backups em `crimson_override`). No jogo: gestos das magias sem armas na mão
  (`work/shots/t49_zoom.png`), sem queda. Os projéteis/efeitos continuam os do DMC3.

## 2026-10-23 — T50 (agente): render do Kratos para menus; Kalina Ann e Sparda escondidas
- `blender/scripts/render_kratos.py`: Kratos do glb numa pose de animação (ações "grupo nome" no glb, casadas pelo
  fim do nome), câmera do lado +Y, textura como emissão (as normais do PS2 são facetadas), fundo transparente
  (`work/shots/kr_idle.png`). 12 poses em `work/install/menu_art/renders/` (fora do git).
- Menus: as cartas de golpe (`id741`–`id760`) são da loja nativa, que o Crimson troca pela dele (provavelmente não
  aparecem). O retrato da tela STATUS não foi achado por comparação de imagem (candidatas `id300`/`id271` são outras
  artes); pode ser o modelo 3D ao vivo. Troca das artes adiada.
- Escondidas também `plwp_grenade` (Kalina Ann) e `plwp_sword3` (Sparda): nenhuma arma do Dante fica visível.

## 2026-10-23 — T51 (agente): regressão completa depois de T44–T50
- 20 missões + 14 chefes com `playtest.sh`: **34/34 sem queda** (`work/shots/playtest/regressao.txt`); configs
  devolvidos. Dano onde há inimigo perto (M1–3, 5, 13, 19, 20 e 12 de 14 chefes).

## 2026-10-23 — T52 (agente): instalador único do override
- `tools/install_all.sh`: manifesto do que o modo Kratos usa (motions_v18, pl000 v10, roupas, DTs, Rebellion/
  sword2 escondidas, Artemis, armas escondidas, msg_eng). `--check` compara o override com as fontes (só
  `demo_pl000_00_3` diferia: versão anterior à correção do cabeçalho do T38; reinstalado → 0 diferenças);
  `--restore` devolve os originais do Crimson (backups em `crimson_override`). Antes de copiar, guarda backup de
  qualquer arquivo do override que ainda não tenha.

## 2026-10-23 — T53 (agente): locomoção travada sem a pose de mira
- Sonda no slot das Blades (`motion_probe.sh 0`): todos os golpes que saem já estão mapeados. Com a trava (RB) e a
  E&I, o Dante anda mirando as pistolas (grupo 8: parado 0/2/4/5, andar 11/12/18/19, correr 25/26) — o Kratos fazia
  isso com as armas escondidas. `pl000_00_8` → `idleCombat`/`walkBlend1`/`walkBlend2` (`stretch`, loop); o disparo
  8/8 e o ar 8/32 seguem como no T49. motions_v19 (só `pl000_00_8` muda); `install_all.sh` aponta para v19.
- No jogo: travado e andando para os lados em postura de combate (`work/shots/lock_walk_sheet.png`).
- Pendente: a mesma troca nos grupos 9–11 (Shotgun, Artemis, Spiral) quando estão equipados.

## 2026-10-23 — T54 (agente): locomoção travada sem mira em todas as armas de fogo
- `gun_probe.sh` ganhou o modo "andar" (travado, para os lados, para trás e para frente). Os índices variam com o
  estado da trava; três rodadas levantaram: E&I também 9/16/41/44/48/50/51; Shotgun 0/2/4/5/9/11/12/16/18/19/23/25/26 e
  disparo travado **9/7**; Artemis 0/2/3/5–9/11/12; Spiral 0/2/4/9/11–13/15–17/19/21/23/24 e disparo travado **11/7**.
- Tudo vira `idleCombat`/`walkBlend1`/`walkBlend2`; os disparos travados 9/7 e 11/7 viram Poseidon e Medusa como os do
  chão. motions_v20 (só `pl000_00_8–11` mudam); `install_all.sh --check` = 0 diferenças; sonda final sem queda.

## 2026-10-23 — T55 (agente): pedra da Medusa, 2ª tentativa (descartada)
- Hipótese: as correspondências espaçadas 0x120 (+0x148…+0x5C8) seriam as partes do modelo do inimigo. Tingindo só
  essa sequência (5 partes no Hell), **o jogo caiu de novo**. Causa provável: o tingimento escreve até
  `+0x80 + 0xE0 = +0x160`, além do fim de objetos de 0x120 bytes — não são ModelData, e a foice cinza do T39 foi
  corrupção do objeto vizinho. Código revertido.
- Para retomar: achar o ModelData real dos inimigos pela função de desenho do tipo (vtable do ator → função que faz
  `lea rcx,[reg+X]; call dmc3.exe+89DE0`), por tipo de inimigo.

## 2026-10-23 — T56 (agente): pedra da Medusa, 3ª tentativa (o tingimento não vale para inimigos)
- ModelData real do Hell achado pela vtable do ator (`1404C9AF8`, tipo 0): as entradas 20–22 passam `+0x840`,
  `+0xFC0` e `+0x1EC0` para `FUN_140089de0` (`add rcx,0x840` / `lea rcx,[rbx+X]`); o 1º qword de cada um é a vtable do
  modelo (`call [rax+0x140]`). Busca automática em tempo de execução (padrão antes do `call 89DE0` nas 32 primeiras
  entradas da vtable, validando a vtable em .rdata) achou exatamente esses três, **sem queda**.
- Mas `FUN_1402f69c0` nesses modelos **não muda nada na tela**, nem com vermelho opaco (`work/shots/stone7_t.png`): o
  efeito de cor só vale no caminho de desenho do jogador. Código revertido. Para retomar: procurar onde o desenho do
  inimigo lê cor/material (ex.: o brilho de dano) — fora do escopo por ora.

## 2026-10-23 — T57 (agente): build reproduzível (Fase 10, base)
- `tools/export_gow1.sh [saída]`: sobe o god_of_war_browser na ISO do usuário (se não estiver rodando), acha cada
  tag pelo nome e exporta Kratos (`R_HERO0/hero`), Blade of Chaos (`R_WPN0_0/maiblade`), Blade of Artemis
  (`ATHN08C/athenablade`), as 16 vozes do banco `Hero`, 134 sons do `GENERAL` e as 193 texturas `TXR_HUD*`. Rodado do
  zero numa pasta de checagem (3,5 min): armas e sons **idênticos** ao extraído; HUD com os **mesmos pixels**
  (antes regravado pelo PIL); `hero_obj.glb` difere 4 bytes, mas gera um `pl000.pac` **idêntico**.
- `tools/build_all.sh <saída>`: regera os 62 arquivos do override a partir dos originais do Crimson
  (`crimson_override`) e do `extracted/gow1` — corpo e 5 roupas, 6 DTs, Artemis, 11 armas escondidas, 37 motions e o
  msg_eng. Rodado em ~1 min: 60/62 idênticos ao instalado (os 2 diferentes: o 11/20 novo e o `plwp_sword` escondido
  a partir da base original em vez da do T8). Saída oficial `work/install/release`; `install_all.sh` instala só
  dela (0 diferenças). Fumaça: M3 e chefe da M7 sem queda.
- Mapeado também o 11/20 (Spiral travado).

## 2026-10-23 — T58 (agente): sons da Rage e de Poseidon
- Os WADs das magias (`R_LGHTN*`, `R_MEDHD*`, `R_RDEAD*`, `R_BRSRK*`) não têm banco de som. Entre os 617 VAG/VPK soltos,
  pelo nome: `RAGEMIME.VAG` (3,5 s; o `GENERAL2` cita `SND_MI_RAGEMIME`) e `POSMAG06.VAG` (5,8 s), exportados por
  `/dump/pack/<arquivo>/wav` (também no `export_gow1.sh`). [HIPÓTESE] pelo nome — conferir de ouvido.
- DLL: som `rage` ao ativar o DT (`ator.devil`, +0x3E9B) e `poseidon` no disparo da Shotgun. Playtest M3: os dois
  tocaram (log), sem queda.
- `export_gow1.sh` encerra o servidor pelo nome do processo (`pgrep -x`; o `pkill -f` casava com o próprio shell).

## 2026-10-23 — T59 (agente): arte de menu com o Kratos (pipeline de textura)
- `tools/build_menu_art.py`: lê o `id*.pac` do `.nbz`, confere o round-trip do PAC e do bloco de textura, troca a
  textura por fundo da própria arte (bordas esticadas + vinheta, sem a figura) + render do Kratos com brilho vermelho,
  grava DXT5 com `tex.make_texture`. 1º alvo: `id7168` (fim de missão secreta, Dante na poltrona; não existe no
  override do Crimson → o `--restore` apaga). Prévia `work/install/menu_art/out/id7168.pac.preview.png`.
- Entra no `build_all.sh` (passo 6, se os renders existirem); release com 63 arquivos; `install_all --check` = 0.
  Playtest M5 sem queda. **Não visto no jogo** (tela difícil de alcançar no teste automático).

## 2026-10-23 — T60 (agente): Rage of the Gods com as Blades em brasa
- Os seis DTs (`pl005–pl009`, `pl017`) agora usam `maigodblade.glb` (Blades of Chaos no nível máximo, textura de fogo)
  nas duas mãos, no `build_all.sh`. No jogo: Kratos dourado com as lâminas em brasa (`work/shots/dt_god_zoom.png`).
  Release regerada e instalada (`--check` = 0).

## 2026-10-23 — T61 (agente): HUD com mais peças do GoW1
- Peças (`work/shots/hud_pieces.png`): `TXR_HUD019` gradiente branco (preenchimento), `013` orb, `004` voluta e
  `003` barra de ouro (medidor de Rage do GoW1). `install_hud.sh` copia como fill/orb/rage_cap/rage_bar.
- DLL: vida e magia com o gradiente tingido (recorte de UV conforme enche), medidor de Rage dourado abaixo da lâmina
  (fundo escurecido + barra cheia até a fração, voluta na ponta) além do brilho do medalhão, orb do GoW1 tingido de
  vermelho no contador. Sem os arquivos, volta ao desenho liso. No jogo: `work/shots/hud3_crop.png`.

## 2026-10-23 — T62 (agente): efeitos visuais das magias
- DLL: cada magia toca um efeito do Effekseer do Crimson no lançamento (na matriz da mão direita, osso 9 do corpo,
  como os efeitos do Crimson em `CrimsonFX.cpp`) e no acerto (na posição do inimigo, no máximo 1 a cada 0,1 s).
  Configurável no KratosConfig sem recompilar: `fx<Zeus|Poseidon|Hades|Medusa><Cast|Hit|Scale|Color>` (cor em hex
  AARRGGBB). `Read` da config passou a aceitar texto e hex.
- Padrões (pelo que aparece nas capturas `work/shots/t62_fx.png`): Zeus `drive_level1` + impacto `risingstar` (clarão
  na mão, faíscas no alvo); Poseidon `risingstar`; Hades `jdc_charge_dt` roxo (o mais visível); Medusa
  `jdc_charge_dt`. `SetAllColor` **multiplica** a cor do efeito: azul/verde sobre o roxo do jdc somem, então o Poseidon
  não fica azul. Sem queda na sonda das quatro armas.
- Pendente: efeitos próprios (raio de Zeus, almas do Hades) exigiriam efeitos Effekseer novos.

## 2026-10-23 — T63 (agente): sons do Crimson que destoam do GoW1
- Com `sounds`, a DLL zera em memória (`activeCrimsonConfig.SFX`, sem gravar o CrimsonConfig) o anunciador de rank de
  estilo, a voz do Dante na troca de estilo ("Trickster!") e os dois sons de ativação do DT (a Rage toca o som do
  GoW1, T58). Playtest M3 sem queda; o CrimsonConfig no disco continua com 100.

## 2026-10-23 — T64 (agente): resto dos golpes das Blades e efeito da Medusa
- `pl000_00_3`: as 11 motions do esqueleto ainda do Dante (8, 9, 11, 14, 15, 17, 18, 19, 29, 31, 32) identificadas pelas
  poses (`work/shots/reb_unmapped.png`: estocadas rápidas, corte para cima, partes do Stinger, golpes agachados,
  chute, giro e descida aérea) e trocadas por `dashMultiStab`, `combo4D`, `blockLauncherB`, `dash`, `combo4B`,
  `comboLR3/4`, `KickBox1`, `air360`, `berAirV2Land` (`strike`). Agora todo o `pl000_00_3` é do Kratos. Release
  regerada (63) e instalada; regressão curta (M3, chefe M3, sondas) sem queda. A maioria desses golpes não sai na
  rotina do teste: não vistos no jogo.
- Medusa: efeito padrão `risingstar` (branco) × verde no lançamento.

## 2026-10-23 — T65 (agente): reações de dano e o resto da base com o Kratos
- Levantamento das motions do esqueleto ainda do Dante em cada coleção (base 13, dano 14, armas e estilos dezenas).
- `pl000_00_1` (DAMAGE, nova no mapeamento): golpe leve/lados, golpe forte, derrubada, arremesso, levantar, colapso,
  golpe no ar e cambaleios → `hitFront/Left/Right`, `hitSpin`, `hitKnockdown`, `hitBounce`, `hitGetupGround`,
  `hitGetup`, `death01`, `hitAir` (`stretch`: mantém duração e deslocamento do Dante). Pelas poses
  (`work/shots/dmg_unmapped.png`).
- `pl000_00_0`: início do pulo (0/3), pulo com giro (0/4–5, 14), aterrissagem agachada (0/10), variações de parado
  (0/11, 19, 18, 50), rolamentos no chão (0/12–13) (`work/shots/base_unmapped.png`; escolhas aproximadas).
- Playtest M3 e chefe M5 sem queda; tocaram 1/0, 1/15, 1/6 (reações) e 0/3, 0/4 (pulo).
- Ainda do Dante: partes das coleções de armas (Cerberus 6, Artemis 10, Nevan 26, Beowulf 20, guns 8/9), estilos
  (Trickster 23, Royalguard 24, Swordmaster 13), Gunslinger (18–22) e Kalina (12).

## 2026-10-23 — T66 (agente): o resto dos estilos com o Kratos
- Pelas poses (`work/shots/trick_unmapped.png`, `rg_unmapped.png`, `sm_unmapped.png`):
  - Trickster (`pl000_00_23`): dash no ar e Sky Star → `airDash`; parede/piruetas → `airForwardFlip`/`air360`; dashes
    curtos → `evadeFront`; aterrissagem → `land`.
  - Royalguard (`pl000_00_24`, agora as 21 entradas): guarda no ar → `airBlock`; variações no chão → `block`/
    `blockReaction`; Releases → `parry01/02`.
  - Swordmaster da Rebellion (`pl000_00_13`): 0/11/12/13/17 → `comboLR3`, `combo4A`, `combo4C`, `comboLR2`,
    `combo5A`; aéreos 4/5 → `airH1`/`airV1`; posturas → `idleCombat`. 18 e 20 (deitar/levantar) não identificados,
    ficam do Dante.
- Sonda dos três estilos sem queda; Swordmaster no chão agora encadeia 13/19 → 13/12 → 13/13.

## 2026-10-23 — T67 (agente): o resto das armas de corpo a corpo com o Kratos
- Cerberus (`pl000_00_4`, pelas poses `work/shots/cer_un.png`): sequências longas com giro 6/7/22/23/26 → `combo4A–D`,
  `comboLR3`; 27 → `combo3A`. Artemis (`pl000_00_5`, `agn_un.png`): golpes largos → `berComboH1–H4/V2–V4/Stab`; 18/19 no
  ar → `berAirH2`/`berAirStab`.
- Nevan (26 entradas) e Beowulf (20) sem folha por índice: ciclo de combos do Kratos na Nevan e de `KickBox1–3`/
  `brutal1/3` no Beowulf (socos e chutes) — **aproximado**.
- Release regerada e instalada (`--check` = 0); sonda das quatro armas sem queda (acertos 6/8/9/2 num combo).

## 2026-10-23 — T68 (agente): todas as coleções de motion do jogador com o Kratos
- Grupos (enum `MOTION_GROUP_DANTE`): 18–22 Gunslinger (E&I, Shotgun, Artemis, Spiral, Kalina), 25 Quicksilver, 26
  Doppelganger. Mapeados por arma: variações de tiro e Gunslinger viram os gestos da magia daquela arma (Zeus
  `boltThrow`/`boltThrowL`/`airBoltThrow`, Poseidon `LightningExit`/`airLightningStart`, Hades `raiseTheDead`/
  `airRaiseTheDead`, Medusa `psentHead`/`headNukeStart`; 11/5, recuo da Spiral, fica do Dante); Kalina (sem magia no
  GoW1) = gesto do raio; taunts 2/2–3 = agarrão; Quicksilver/Doppelganger = `berserkEnter`; resto dos Swordmaster das
  armas em ciclo (aproximado). Só ficam do Dante 13/18, 13/20 e 11/5.
- Release regerada e instalada; regressão completa em andamento.
- Regressão completa depois do T68: **34/34 sem queda** (20 missões + 14 chefes) e as sondas das quatro armas de fogo e
  dos estilos Trickster/Swordmaster/Royalguard sem queda (`work/shots/playtest/regressao2.txt`); configs devolvidos.

## 2026-10-23 — T69 (agente): barra de vida dos chefes no estilo do GoW1
- HUD: a barra do chefe do DMC3/Crimson fica escondida (`hideBossHUD` + `ToggleHideBossHUD`) e a DLL desenha a do GoW1
  embaixo, no centro: barra de pedra (`TXR_HUD037`), ponta de lança dourada (`036`) e o gradiente tingido de vermelho,
  com a vida do 1º chefe vivo na lista (`EnemyHp`/`IsBoss`, máximo da tabela). `install_hud.sh` copia boss_cap/boss_bar.
- No jogo (chefes da M3 e da M7): `work/shots/boss_bar.png`, a barra desce com o dano; sem queda.

## 2026-10-23 — T70 (agente): Rage of the Gods invulnerável
- Flag `rageInvulnerable` (padrão ligado): no hook de dano do Crimson (ramo do jogador, Actor.cpp) a DLL zera o dano
  enquanto `ator.devil` (+0x3E9B) estiver ativo, como a Rage do GoW1. Teste com dano normal e DT liberado: 5 golpes
  bloqueados (`rage bloqueou`); o Kratos ainda faz a reação de golpe (1/x), só não perde vida.

## 2026-10-23 — T71 (agente): Poseidon's Rage em área e só as armas do GoW1
- **Poseidon's Rage:** no disparo da Shotgun, todo inimigo até `poseidonRadius` (450) perde `poseidonAreaDamage` (150):
  se o golpe mata e o inimigo já foi golpeado antes, morre pela função de dano do jogo (`Kill`, T33); senão a vida para
  em 1. A queda conta como golpe no quadro seguinte (magia, hits, som, efeito). Sonda: `poseidon atingiu 1/2/3`
  (chão, travado, ar); Medusa segue `petrificou 3`.
- **`gowWeaponsOnly`** (padrão ligado): desmarca na sessão o desbloqueio de Cerberus, Nevan, Beowulf e Kalina Ann e
  troca essas armas, se equipadas, por Rebellion/Agni & Rudra/E&I. Sonda: um RT agora vai das Blades direto para a
  Artemis (grupo 5), antes ia para o Cerberus. `gun_probe.sh` registra as linhas de Poseidon/Medusa por modo.

## 2026-10-23 — T72 (agente): esconder as Blades com a Artemis — os objetos reservados não servem
- Teste: `kratos_fit.py --mark-reserved` põe um cubo em cada objeto 0–21 (reservados, que o jogo liga/desliga) numa
  fileira ~50 acima da cabeça (eixo Y para cima: pelve y 116, cabeça 166, topo do corpo 181,6). No jogo (M3, testWeapons),
  **nenhum cubo aparece**, nem com as Blades nem com a Artemis (`work/shots/mark_pair.png`): nesse estado todos ficam
  escondidos, nenhum alterna com a arma. Esconder as lâminas por objeto do corpo não funciona por esse caminho.
- Para retomar: (a) pôr as lâminas no PAC da arma do slot Rebellion (`plwp_sword`, que o jogo só mostra com ela) —
  exige o modelo da arma acompanhar os ossos 23/4 do corpo; ou (b) achar no código onde a visibilidade por objeto é
  decidida (REA). O `pl000` de teste foi revertido (`install_all --check` = 0).

## 2026-10-23 — T73 (agente): as Blades somem quando a Artemis está em uso
- O formato MOT tem canais de escala (`sx/sy/sz`) e o jogo os aplica nos ossos do jogador. `build_motions.py`: nas
  coleções da Artemis (`pl000_00_5` e o Swordmaster `pl000_00_15`) os ossos das lâminas (23/4) ganham escala 0,001 →
  as Blades encolhem até sumir na mão enquanto a Artemis é usada; nas outras coleções voltam (sem trilha de escala =
  1). No jogo: Kratos com a Artemis no ombro e a mão esquerda livre (`work/shots/artemis_noblades.png`).
- Obs.: com `gowWeaponsOnly`, o RT alterna Blades ↔ Artemis (1 RT = Artemis).
- Escala explícita em **toda** motion (1 nas outras coleções, 0,001 nas da Artemis): sem trilha o osso guardaria a
  escala da motion anterior. Ida e volta (Blades → Artemis → Blades): as lâminas voltam (`work/shots/blades_back.png`).
  `motion_probe.sh` com `PROBE_BACK=1` volta para a arma inicial e captura um combo. Regressão curta sem queda.

## 2026-10-23 — T74 (agente): níveis das magias
- Cada magia sobe com o nível da arma de fogo comprado na loja (`SessionData.rangedWeaponLevels`, índice
  `WEAPON::* − 5`, 0–2, o mesmo que o Crimson usa em Config.cpp): `magicLevelBonus` (0,5) de dano por nível em Zeus,
  Poseidon (inclusive a área) e Hades — também nos chefes, pelo `MagicMultiplier` — e +1,5 s de pedra por nível na
  Medusa. `OnEnemyDamage` passou a usar o mesmo `MagicMultiplier`. Sonda das quatro armas sem queda (save de teste no
  nível 0: multiplicador igual ao de antes). [Não testado com níveis 1–2: exige comprar na loja.]
