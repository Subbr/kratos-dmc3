# Instalador do Kratos x DMC3 para Windows (sem WSL, sem administrador). Rode no PowerShell:
#   irm https://raw.githubusercontent.com/Subbr/kratos-dmc3/main/setup.ps1 | iex
# Acha o Devil May Cry HD Collection na Steam, instala o Crimson 0.5a se faltar, pede a ISO do God of War, baixa as
# ferramentas (Python pelo uv, Go) para %LOCALAPPDATA%\KratosDMC3 e gera tudo a partir dos SEUS arquivos.
# Rodar de novo atualiza. Desinstalar: rodar de novo e escolher "Desinstalar".
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest fica muito lento com a barra de progresso
Add-Type -AssemblyName System.Windows.Forms
function Say($t) { Write-Host "`n== $t" -ForegroundColor Red }
function Fail($t) { Write-Host "`nERRO: $t" -ForegroundColor Yellow; Write-Host 'Relate em https://github.com/Subbr/kratos-dmc3/issues'; throw $t }

$Repo = 'Subbr/kratos-dmc3'
$Dir = Join-Path $env:LOCALAPPDATA 'KratosDMC3'
$Tools = Join-Path $Dir 'bin'
New-Item -ItemType Directory -Force -Path $Dir, $Tools | Out-Null

Say 'Kratos x Devil May Cry 3 - instalador'

# 1. Jogo (bibliotecas da Steam)
$game = $null
$steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
if ($steam) {
  $libs = @($steam)
  $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
  if (Test-Path $vdf) { $libs += (Select-String -Path $vdf -Pattern '"path"\s+"([^"]+)"').Matches | ForEach-Object { $_.Groups[1].Value -replace '\\\\', '\' } }
  foreach ($l in $libs) {
    $p = Join-Path $l 'steamapps\common\Devil May Cry HD Collection'
    if (Test-Path (Join-Path $p 'dmc3.exe')) { $game = $p; break }
  }
}
if (-not $game) {
  $d = New-Object System.Windows.Forms.FolderBrowserDialog
  $d.Description = 'Escolha a pasta "Devil May Cry HD Collection" (a que tem o dmc3.exe)'
  if ($d.ShowDialog() -ne 'OK') { return }
  $game = $d.SelectedPath
}
if (-not (Test-Path (Join-Path $game 'dmc3.exe'))) { Fail "dmc3.exe não encontrado em $game" }
Write-Host "Jogo: $game"

# já instalado? oferece atualizar ou desinstalar
$py = Join-Path $Dir 'tools\.venv\Scripts\python.exe'
if ((Test-Path $py) -and (Test-Path (Join-Path $game 'Crimson\kratos_body'))) {
  $r = [System.Windows.Forms.MessageBox]::Show("O modo Kratos já está instalado.`n`nSim = atualizar`nNão = desinstalar (volta ao Crimson original)",
    'Kratos x DMC3', 'YesNoCancel')
  if ($r -eq 'Cancel') { return }
  if ($r -eq 'No') {
    $env:DMC_HD_DIR = $game
    & $py -X utf8 (Join-Path $Dir 'tools\kratos_install.py') restore
    return
  }
}

# 2. Crimson 0.5a
if (-not (Test-Path (Join-Path $game 'Crimson.dll'))) {
  Say 'Instalando o DMC3 Crimson 0.5a (base do mod)'
  $inst = Join-Path $env:TEMP 'crimsoninstall-0.5a.exe'
  if (-not (Test-Path $inst)) {
    Write-Host 'Baixando o instalador do Crimson (~320 MB)...'
    Invoke-WebRequest 'https://github.com/berthrage/DMC3-Crimson/releases/download/V0.5a/crimsoninstall-0.5a-windows-x64-x86.exe' -OutFile $inst -UseBasicParsing
  }
  Write-Host "Siga o instalador do Crimson e escolha a pasta: $game"
  Start-Process $inst -Wait
  if (-not (Test-Path (Join-Path $game 'Crimson.dll'))) { Fail 'Crimson não encontrado na pasta do jogo. Instale-o e rode de novo.' }
  [System.Windows.Forms.MessageBox]::Show('Abra o Devil May Cry 3 uma vez pela Steam (com o Crimson), feche o jogo e clique OK.', 'Kratos x DMC3') | Out-Null
}

# 3. ISO do God of War
Say 'ISO do God of War (PS2, NTSC-U SCUS_973.99) feita do seu disco'
$f = New-Object System.Windows.Forms.OpenFileDialog
$f.Title = 'Escolha a ISO do God of War (PS2)'; $f.Filter = 'ISO (*.iso)|*.iso|Todos|*.*'
if ($f.ShowDialog() -ne 'OK') { return }
$iso = $f.FileName

# 4. Código do mod (zip do GitHub; work\, extracted\ e tools\.venv ficam entre atualizações)
Say 'Baixando o mod'
function Get-Zip($url, $dest) {
  $zip = Join-Path $env:TEMP ('k' + [guid]::NewGuid() + '.zip'); $tmp = $zip + '.d'
  Invoke-WebRequest $url -OutFile $zip -UseBasicParsing
  Expand-Archive $zip $tmp -Force
  $top = Get-ChildItem $tmp | Select-Object -First 1
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item (Join-Path $top.FullName '*') $dest -Recurse -Force
  Remove-Item $zip, $tmp -Recurse -Force
}
Get-Zip "https://github.com/$Repo/archive/refs/heads/main.zip" $Dir

# 5. Ferramentas: uv (Python 3.12) e Go (para compilar o extrator do GoW1, que não tem binário público)
Say 'Ferramentas (só na primeira vez)'
$uv = Join-Path $Tools 'uv.exe'
if (-not (Test-Path $uv)) {
  $z = Join-Path $env:TEMP 'uv.zip'
  Invoke-WebRequest 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' -OutFile $z -UseBasicParsing
  Expand-Archive $z $Tools -Force; Remove-Item $z
}
Push-Location $Dir
try {
  if (-not (Test-Path $py)) { & $uv venv -q --python 3.12 tools\.venv; if ($LASTEXITCODE) { Fail 'uv venv' } }
  & $uv pip install -q --python $py -r requirements.txt; if ($LASTEXITCODE) { Fail 'pip install' }
  $gowb = Join-Path $Dir 'vendor\gowb_bin\god_of_war_browser.exe'
  if (-not (Test-Path $gowb)) {
    $go = Join-Path $Tools 'go\bin\go.exe'
    if (-not (Test-Path $go)) {
      Write-Host 'Baixando o Go (~70 MB)...'
      $z = Join-Path $env:TEMP 'go.zip'
      Invoke-WebRequest 'https://go.dev/dl/go1.22.12.windows-amd64.zip' -OutFile $z -UseBasicParsing
      Expand-Archive $z $Tools -Force; Remove-Item $z
    }
    $src = Join-Path $Dir 'vendor\god_of_war_browser'
    if (-not (Test-Path $src)) { Get-Zip 'https://github.com/Subbr/god_of_war_browser/archive/refs/heads/kratos.zip' $src }
    Push-Location $src
    $env:GOTOOLCHAIN = 'local'
    & $go build -o $gowb .; $rc = $LASTEXITCODE
    Pop-Location
    if ($rc) { Fail 'compilação do god_of_war_browser' }
  }

  # 6. Gerar e instalar
  Say 'Gerando e instalando o mod (10-15 min na primeira vez)'
  $env:DMC_HD_DIR = $game
  $env:GOW1_ISO = $iso
  & $py -X utf8 tools\kratos_install.py all
  if ($LASTEXITCODE) { Fail 'instalação (veja a mensagem acima)' }
} finally { Pop-Location }

Say 'Pronto! Abra o Devil May Cry 3 pela Steam e comece da Missão 2 ou mais.'
Write-Host 'Para atualizar ou desinstalar, rode o mesmo comando de novo.'
