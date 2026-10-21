@echo off
rem Configura e compila o fork do Crimson (dll\crimson) em Release x64. Uso: build_crimson.bat [configure]
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set CMAKE="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
cd /d "%~dp0..\..\dll\crimson" || exit /b 1
if "%1"=="configure" %CMAKE% -S . -B build -G "Visual Studio 17 2022" -A x64 || exit /b 1
%CMAKE% --build build --config Release --target Crimson -- /m /v:minimal || exit /b 1
