@echo off
REM ============================================================
REM  Abre o Sistema de Cartao Ponto.
REM  Antes de abrir, busca atualizacoes (se houver internet).
REM ============================================================
cd /d "%~dp0"

REM ---------- atualizacao automatica (silenciosa) ----------
if exist ".git" (
    where git >nul 2>&1
    if not errorlevel 1 (
        echo Verificando atualizacoes...
        git pull --quiet 2>nul
    )
)

REM ---------- componentes ----------
python -c "import openpyxl, pandas, holidays, pymupdf" >nul 2>&1
if errorlevel 1 (
    echo Instalando os componentes necessarios. Isso demora cerca de 1 minuto.
    echo.
    python -m pip install -r requirements.txt
    echo.
)

REM ---------- abrir ----------
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw main.py
) else (
    python main.py
)
