# Instalador do Kratos x DMC3 para Windows. Rode no PowerShell (não precisa ser administrador):
#   irm https://raw.githubusercontent.com/Subbr/kratos-dmc3/main/setup.ps1 | iex
# Acha o Devil May Cry HD Collection na Steam, instala o Crimson 0.5a se faltar, pede a ISO do God of War e
# roda tools/bootstrap.sh no WSL (que gera tudo a partir dos SEUS arquivos e instala no jogo).
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
function Say($t) { Write-Host "`n== $t" -ForegroundColor Red }

Say 'Kratos x Devil May Cry 3 - instalador'

# 1. WSL
$hasWsl = $false
try { wsl.exe -e true 2>$null; $hasWsl = ($LASTEXITCODE -eq 0) } catch {}
if (-not $hasWsl) {
  Write-Host 'O WSL (Linux do Windows) não está instalado. Abra o PowerShell como administrador, rode:'
  Write-Host '    wsl --install' -ForegroundColor Yellow
  Write-Host 'reinicie o PC, abra o "Ubuntu" uma vez para criar o usuário e rode este instalador de novo.'
  return
}

# 2. Jogo (bibliotecas da Steam)
Say 'Procurando o Devil May Cry HD Collection'
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
Write-Host "Jogo: $game"

# 3. Crimson 0.5a
if (-not (Test-Path (Join-Path $game 'Crimson.dll'))) {
  Say 'Instalando o DMC3 Crimson 0.5a (base do mod)'
  $inst = Join-Path $env:TEMP 'crimsoninstall-0.5a.exe'
  if (-not (Test-Path $inst)) {
    Write-Host 'Baixando o instalador do Crimson (~320 MB)...'
    Invoke-WebRequest 'https://github.com/berthrage/DMC3-Crimson/releases/download/V0.5a/crimsoninstall-0.5a-windows-x64-x86.exe' -OutFile $inst -UseBasicParsing
  }
  Write-Host "Siga o instalador do Crimson e escolha a pasta: $game"
  Start-Process $inst -Wait
  if (-not (Test-Path (Join-Path $game 'Crimson.dll'))) { Write-Host 'Crimson não encontrado na pasta do jogo. Instale-o e rode de novo.'; return }
  Write-Host 'Abra o jogo uma vez pela Steam (com o Crimson), feche, e aperte Enter para continuar.'
  Read-Host | Out-Null
}

# 4. ISO do God of War
Say 'ISO do God of War (PS2, NTSC-U SCUS_973.99) feita do seu disco'
$f = New-Object System.Windows.Forms.OpenFileDialog
$f.Title = 'Escolha a ISO do God of War (PS2)'; $f.Filter = 'ISO (*.iso)|*.iso|Todos|*.*'
if ($f.ShowDialog() -ne 'OK') { return }
$iso = $f.FileName

# 5. WSL faz o resto
Say 'Gerando e instalando o mod (10-15 min na primeira vez)'
$url = 'https://raw.githubusercontent.com/Subbr/kratos-dmc3/main/tools/bootstrap.sh'
wsl.exe -e bash -c "curl -fsSL $url | bash -s -- '$game' '$iso'"
if ($LASTEXITCODE -eq 0) {
  Say 'Pronto! Abra o Devil May Cry 3 pela Steam e comece da Missão 2 ou mais.'
  Write-Host 'Desinstalar: wsl -e bash -c "cd ~/kratos-dmc3 && ./install.sh --restore"'
} else { Write-Host 'Algo falhou (veja a mensagem acima). Relate em https://github.com/Subbr/kratos-dmc3/issues' -ForegroundColor Yellow }
