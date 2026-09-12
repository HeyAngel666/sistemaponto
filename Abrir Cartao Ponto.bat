@echo off
REM ============================================================
REM  Abre o Sistema de Cartao Ponto.
REM  O proprio programa busca atualizacoes ao iniciar.
REM ============================================================
cd /d "%~dp0"

python -c "import openpyxl, pandas, holidays, pymupdf" >nul 2>&1
if errorlevel 1 (
    echo Instalando os componentes necessarios. Isso demora cerca de 1 minuto.
    echo.
    python -m pip install -r requirements.txt
    echo.
)

where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw main.py
) else (
    python main.py
)
