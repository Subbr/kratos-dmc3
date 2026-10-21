# Controle do DMC3 para testes automáticos: abrir, apertar teclas (SendInput com scancode) e capturar a tela.
# Uso: powershell.exe -ExecutionPolicy Bypass -File game.ps1 <start|stop|shot <png>|keys <seq>|click "x y">
#   seq: nomes separados por espaço, opcional ":ms" de pressão e "wait:ms". Ex.: "enter wait:1500 down enter"
param([string]$Action, [string]$Arg = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$GameDir = Join-Path $Root "Devil May Cry HD Collection"

Add-Type -AssemblyName System.Drawing, System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Inp {
  [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT { public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr extra; }
  [StructLayout(LayoutKind.Explicit, Size=40)] public struct INPUT { [FieldOffset(0)] public uint type; [FieldOffset(8)] public KEYBDINPUT ki; }
  [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] i, int size);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, IntPtr p);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  public static void Force(IntPtr h) {
    uint fg = GetWindowThreadProcessId(GetForegroundWindow(), IntPtr.Zero), me = GetCurrentThreadId();
    AttachThreadInput(me, fg, true); BringWindowToTop(h); SetForegroundWindow(h); AttachThreadInput(me, fg, false);
  }
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr ctx);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
  public static void Key(ushort scan, bool ext, bool up) {
    var i = new INPUT[1]; i[0].type = 1; i[0].ki.wScan = scan;
    i[0].ki.dwFlags = 0x0008u | (ext ? 0x0001u : 0) | (up ? 0x0002u : 0);
    SendInput(1, i, Marshal.SizeOf(typeof(INPUT)));
  }
}
"@

[Inp]::SetProcessDpiAwarenessContext([IntPtr]-4) | Out-Null  # pixels reais por monitor (há 2 telas)
$Scan = @{ enter=@(0x1C,$false); esc=@(0x01,$false); space=@(0x39,$false);
  up=@(0x48,$true); down=@(0x50,$true); left=@(0x4B,$true); right=@(0x4D,$true);
  w=@(0x11,$false); a=@(0x1E,$false); s=@(0x1F,$false); d=@(0x20,$false);
  i=@(0x17,$false); j=@(0x24,$false); k=@(0x25,$false); l=@(0x26,$false);
  q=@(0x10,$false); e=@(0x12,$false); f1=@(0x3B,$false); tab=@(0x0F,$false) }

function Focus {
  $p = Get-Process dmc3 -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { throw "dmc3 não está rodando" }
  $already = [Inp]::GetForegroundWindow() -eq $p.MainWindowHandle
  for ($try = 0; $try -lt 5 -and -not $already; $try++) {
    [Inp]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
    # o Windows só deixa trocar o primeiro plano depois de uma entrada de teclado: Alt solto antes
    [Inp]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero); [Inp]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
    [Inp]::Force($p.MainWindowHandle)
    Start-Sleep -Milliseconds 400
    if ([Inp]::GetForegroundWindow() -eq $p.MainWindowHandle) { break }
  }
  if ([Inp]::GetForegroundWindow() -ne $p.MainWindowHandle) { throw "nao consegui trazer o jogo para frente" }
  if (-not $already) { Start-Sleep -Milliseconds 1200 }  # o jogo precisa readquirir o teclado (DirectInput)
  $script:Handle = $p.MainWindowHandle; return $p.MainWindowHandle
}

switch ($Action) {
  "start" {
    if (Get-Process dmc3 -ErrorAction SilentlyContinue) { "já rodando"; break }
    Start-Process -FilePath (Join-Path $GameDir "dmc3.exe") -WorkingDirectory $GameDir
    "iniciado"
  }
  "stop" { Get-Process dmc3 -ErrorAction SilentlyContinue | Stop-Process; "parado" }
  "shot" {
    # só a área da janela do jogo, e só com ela em primeiro plano (nunca captura outras janelas)
    $h = Focus | Select-Object -Last 1
    $r = New-Object Inp+RECT; [Inp]::GetClientRect($h, [ref]$r) | Out-Null
    $pt = New-Object Inp+POINT; [Inp]::ClientToScreen($h, [ref]$pt) | Out-Null
    $w = $r.R - $r.L; $ht = $r.B - $r.T
    $bmp = New-Object System.Drawing.Bitmap $w, $ht
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($pt.X, $pt.Y, 0, 0, (New-Object System.Drawing.Size $w, $ht))
    $bmp.Save($Arg, [System.Drawing.Imaging.ImageFormat]::Png)
    "${w}x${ht} -> $Arg"
  }
  "keys" {
    Focus | Out-Null
    foreach ($tok in $Arg.Split(" ", [StringSplitOptions]::RemoveEmptyEntries)) {
      $name, $ms = $tok.Split(":")
      if ($name -eq "wait") { Start-Sleep -Milliseconds ([int]$ms); continue }
      $hold = if ($ms) { [int]$ms } else { 80 }
      $k = $Scan[$name]; if (-not $k) { throw "tecla desconhecida: $name" }
      [Inp]::Key([uint16]$k[0], $k[1], $false); Start-Sleep -Milliseconds $hold
      [Inp]::Key([uint16]$k[0], $k[1], $true); Start-Sleep -Milliseconds 150
    }
    "ok"
  }
  "click" {
    # clique em posição relativa da área do jogo (0..1, o tamanho da janela muda): "fx fy"
    $h = Focus | Select-Object -Last 1
    $fx, $fy = $Arg.Split(" ")
    $r = New-Object Inp+RECT; [Inp]::GetClientRect($h, [ref]$r) | Out-Null
    $pt = New-Object Inp+POINT
    $pt.X = [int]([double]$fx * ($r.R - $r.L)); $pt.Y = [int]([double]$fy * ($r.B - $r.T))
    [Inp]::ClientToScreen($h, [ref]$pt) | Out-Null
    [Inp]::SetCursorPos($pt.X, $pt.Y) | Out-Null; Start-Sleep -Milliseconds 150
    [Inp]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 80
    [Inp]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero)
    "ok"
  }
  default { throw "ação desconhecida: $Action" }
}
