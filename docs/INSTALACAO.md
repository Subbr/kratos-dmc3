# Instalação — testar a versão atual

Nenhum arquivo da Sony ou da Capcom vem no repositório. O `install.sh` **gera tudo na sua máquina**, a partir do
**seu** Devil May Cry HD Collection e da **sua** ISO do God of War. Tempo total: ~10 min depois dos pré-requisitos.

## Jeito rápido (recomendado)

1. **WSL**, uma vez só: PowerShell **como administrador** → `wsl --install` → reiniciar → abrir "Ubuntu" no menu
   Iniciar e criar usuário/senha.
2. **PowerShell normal** → colar:
   ```powershell
   irm https://raw.githubusercontent.com/Subbr/kratos-dmc3/main/setup.ps1 | iex
   ```
3. Siga as janelas: o instalador do Crimson (se faltar; escolha a pasta do jogo e abra o jogo uma vez) e o
   seletor da ISO. O resto é automático: Python, Go e ffmpeg são baixados sem `sudo` para dentro de
   `~/kratos-dmc3`, o mod é gerado e instalado **na pasta do jogo da Steam** (originais guardados em
   `~/kratos-dmc3/work/backup`).
4. Abra o DMC3 pela Steam. Rodar o comando de novo **atualiza** o mod.

Já tem WSL e prefere o terminal? `curl -fsSL https://raw.githubusercontent.com/Subbr/kratos-dmc3/main/tools/bootstrap.sh | bash -s -- "C:\caminho\Devil May Cry HD Collection" "C:\caminho\gow1.iso"`

O resto deste documento é a instalação **manual / de desenvolvedor** (cópia do jogo dentro do repo, DLL compilada
localmente).

## 1. Pré-requisitos

| O quê | Detalhe |
|---|---|
| Windows 10/11 + **WSL 2** (Ubuntu) | os scripts rodam no WSL; o jogo roda no Windows |
| **Devil May Cry HD Collection** (Steam) | build de 2018 (a atual da Steam) |
| **DMC3 Crimson 0.5a** | [releases do Crimson](https://github.com/berthrage/DMC3-Crimson/releases) — instalar e abrir o jogo uma vez antes. O instalador do Crimson já troca o `dmc3.exe` pelo exe sem ASLR que o mod exige (hash em `docs/ambiente.md`) |
| ISO do **God of War** (PS2, NTSC-U `SCUS_973.99`) | feita do seu disco |
| `git` e `curl` no WSL | já vêm no Ubuntu; Python 3.12, Go e ffmpeg o `install.sh` baixa sozinho (sem sudo) |
| (opcional) VS 2022 Build Tools + CMake | só para compilar a DLL; senão use a DLL pronta da página de Releases |
| (opcional) Blender 5.x | só para regerar as artes dos menus; sem ele o build pula essa parte |

## 2. Clonar e posicionar o jogo e a ISO

```bash
git clone --recursive https://github.com/Subbr/kratos-dmc3.git
cd kratos-dmc3
# cópia do jogo DENTRO do repo (o mod nunca escreve na pasta da Steam)
cp -r "/mnt/c/Program Files (x86)/Steam/steamapps/common/Devil May Cry HD Collection" .
mkdir -p iso && cp /caminho/da/sua/gow1.iso iso/gow1.iso
```

Instale o Crimson 0.5a **nessa cópia** (`./Devil May Cry HD Collection`). Outros caminhos (Blender, CMake) ficam
em `config/paths.env`.

## 3. Compilar o god_of_war_browser (extrator do GoW1)

Usamos um fork com duas mudanças (animações das finalizações). Ele não tem licença, então não distribuímos
binário. O `install.sh` clona e compila sozinho (baixa o Go se faltar); à mão seria:

```bash
git clone -b kratos https://github.com/Subbr/god_of_war_browser.git vendor/god_of_war_browser
(cd vendor/god_of_war_browser && go build -o ../gowb_bin/god_of_war_browser .)
```

## 4. Instalar

```bash
./install.sh                                   # baixa a DLL da página de Releases
KRATOS_BUILD_DLL=1 ./install.sh                # ou compila com o MSVC (precisa do submódulo dll/crimson)
KRATOS_DLL=~/Downloads/Crimson.dll ./install.sh   # ou usa a DLL baixada da página de Releases
```

Etapas: venv Python → bases do DMC3/Crimson (`tools/prepare_bases.sh`, conferidas por `config/bases.sha256`) →
extração do GoW1 (`tools/export_gow1.sh`) → build (`tools/build_all.sh`) → cópia para
`data/dmc3/GData.afs/` e `Crimson/` → `Crimson.dll` do fork. Backups em `work/backup/crimson_override/`.

## 5. Jogar

Abra `dmc3.exe` (ou o launcher) da cópia. Comece pela **Missão 2** ou mais (na Missão 1 o Dante está sem camisa e
algumas trocas não valem). Controles = **GoW1** (`"controls": "gow"`; `"dmc3"` volta ao esquema do DMC3):

| Botão (Xbox / PS) | Ação |
|---|---|
| X / Y (□ / △) | ataque leve / pesado — combos e especiais da tabela do GoW1 |
| A (✕) | pulo (golpes aéreos no ar) |
| B (○) | agarrão e finalizações |
| LB (L1) | bloqueio; no tempo certo = parry; combinações L1 + botão |
| RB (R1) | Hermes Rush / Stomp / Fury |
| RT (R2) | magia; direcional escolhe a magia, LT troca em ciclo |
| analógico direito | esquiva |
| L3 + R3 | Rage of the Gods |

Fonte: decisão D5 em `docs/decisoes.md`.

Ajustes em `Devil May Cry HD Collection/Crimson/configs/KratosConfig.json` (cada recurso tem uma flag;
`"enabled": false` desliga o modo Kratos inteiro). Referência das flags: `dll/crimson/src/KratosMode.hpp`.

## Conferir / desinstalar

```bash
./install.sh --check     # 0 arquivo(s) diferente(s) = instalação igual ao build
./install.sh --restore   # devolve os originais do Crimson e a DLL original
```

## Problemas comuns

- **`bases: N com problema`** — o override já tem arquivos de outro mod, ou o Crimson não é o 0.5a. Reinstale o
  Crimson 0.5a numa cópia limpa do jogo.
- **Jogo fecha ao abrir** — confira o hash do `dmc3.exe` (`docs/ambiente.md`); os endereços valem só para ele.
- **Kratos em pose T / golpes sem animação** — rode `./install.sh --check`; algum arquivo ficou de fora.
- Relate o resto em *Issues*, com `docs/LOG.md` como referência do que já foi testado.
