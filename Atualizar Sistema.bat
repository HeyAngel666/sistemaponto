@echo off
REM ============================================================
REM  Baixa a versao mais recente do sistema.
REM  O programa ja faz isso sozinho ao abrir; use este arquivo
REM  so quando quiser forcar a atualizacao.
REM ============================================================
cd /d "%~dp0"

python atualizador.py

echo.
pause
