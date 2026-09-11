@echo off
setlocal
title Instalador - Sistema de Cartao Ponto

set "DESTINO=%LOCALAPPDATA%\CartaoPonto"
set "REPOSITORIO=https://github.com/HeyAngel666/sistemaponto.git"
set "FALTA=0"

echo ============================================================
echo   INSTALADOR - SISTEMA DE CARTAO PONTO
echo ============================================================
echo.
echo  Este instalador vai:
echo    1. Instalar o Python e o Git, se ainda nao existirem
echo    2. Baixar o sistema para:
echo       %DESTINO%
echo    3. Criar o atalho "Cartao Ponto" na Area de Trabalho
echo.
echo  Nada e apagado do seu computador.
echo.
pause
echo.

REM ---------- 1. verificar o winget ----------
where winget >nul 2>&1
if errorlevel 1 (
    echo [ERRO] O instalador de aplicativos do Windows ^(winget^) nao foi encontrado.
    echo        Atualize a Microsoft Store e tente de novo, ou instale manualmente:
    echo          Python: https://www.python.org/downloads/
    echo          Git:    https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

REM ---------- 2. Git ----------
where git >nul 2>&1
if errorlevel 1 (
    echo Instalando o Git...
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    set "FALTA=1"
) else (
    echo Git ja instalado.
)

REM ---------- 3. Python ----------
where python >nul 2>&1
if errorlevel 1 (
    echo Instalando o Python...
    winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
    set "FALTA=1"
) else (
    echo Python ja instalado.
)

if "%FALTA%"=="1" (
    echo.
    echo ============================================================
    echo   QUASE LA
    echo ============================================================
    echo.
    echo  O Python e/ou o Git acabaram de ser instalados.
    echo  Feche esta janela e abra o Instalar.bat MAIS UMA VEZ
    echo  para concluir.
    echo.
    pause
    exit /b 0
)

REM ---------- 4. baixar ou atualizar o sistema ----------
echo.
if exist "%DESTINO%\.git" (
    echo Atualizando o sistema...
    pushd "%DESTINO%"
    git pull
    popd
) else (
    echo Baixando o sistema...
    if exist "%DESTINO%" rmdir /s /q "%DESTINO%"
    git clone "%REPOSITORIO%" "%DESTINO%"
)

if not exist "%DESTINO%\main.py" (
    echo.
    echo [ERRO] Nao foi possivel baixar o sistema. Verifique a internet.
    echo.
    pause
    exit /b 1
)

REM ---------- 5. dependencias ----------
echo.
echo Instalando os componentes do sistema...
pushd "%DESTINO%"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
popd

REM ---------- 6. atalho na area de trabalho ----------
echo.
echo Criando o atalho na Area de Trabalho...
powershell -NoProfile -Command "$a=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Cartao Ponto.lnk')); $a.TargetPath='%DESTINO%\Abrir Cartao Ponto.bat'; $a.WorkingDirectory='%DESTINO%'; $a.IconLocation='%SystemRoot%\System32\shell32.dll,21'; $a.Save()"

echo.
echo ============================================================
echo   PRONTO
echo ============================================================
echo.
echo  O atalho "Cartao Ponto" esta na sua Area de Trabalho.
echo  O sistema se atualiza sozinho toda vez que voce abrir.
echo.
pause
