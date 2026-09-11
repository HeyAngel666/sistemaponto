@echo off
REM ============================================================
REM  Gera o executavel do Sistema de Cartao Ponto (Windows)
REM  Basta dar dois cliques neste arquivo.
REM ============================================================

echo.
echo === Instalando o que o sistema precisa ===
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo === Gerando o executavel ===
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "Cartao Ponto" ^
    --add-data "modelo;modelo" ^
    main.py

echo.
echo ============================================================
echo  Pronto! O programa esta em:  dist\Cartao Ponto.exe
echo  Os cartoes gerados ficam na pasta "cartoes", ao lado dele.
echo ============================================================
pause
