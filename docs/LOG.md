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
