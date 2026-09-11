@echo off
REM ============================================================
REM  Abre o Sistema de Cartao Ponto.
REM  De dois cliques neste arquivo para usar o programa.
REM ============================================================
cd /d "%~dp0"

python -c "import openpyxl, pandas, holidays" >nul 2>&1
if errorlevel 1 (
    echo Primeira execucao: instalando os componentes necessarios.
    echo Isso demora cerca de 1 minuto e so acontece uma vez.
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
