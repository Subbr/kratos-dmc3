#!/usr/bin/env bash
# REA (CLI) com o Ghidra/JDK do projeto. Uso: tools/rea.sh <comando> [args]  (ex.: tools/rea.sh analyze <exe> --provider ghidra --json)
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export GHIDRA_INSTALL_DIR="$ROOT/vendor/ghidra_12.1.4_PUBLIC" JAVA_HOME="$ROOT/vendor/jdk21" REA_ANALYSIS_PROVIDER=ghidra
# dmc3.exe (3,4 MB de código) passa dos 5,5 min padrão de auto-análise
export REA_GHIDRA_STARTUP_TIMEOUT_MS="${REA_GHIDRA_STARTUP_TIMEOUT_MS:-3600000}" GHIDRA_HEADLESS_MAXMEM="${GHIDRA_HEADLESS_MAXMEM:-6G}"
exec "$ROOT/vendor/rea_cli/node_modules/.bin/rea" "$@"
