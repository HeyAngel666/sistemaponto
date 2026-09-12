@echo off
setlocal enabledelayedexpansion
title Instalador - Sistema de Cartao Ponto

set "DESTINO=%LOCALAPPDATA%\CartaoPonto"
set "PACOTE=https://codeload.github.com/HeyAngel666/sistemaponto/zip/refs/heads/claude/sharp-goodall-j5y3n3"

echo ============================================================
echo   INSTALADOR - SISTEMA DE CARTAO PONTO
echo ============================================================
echo.
echo  Este instalador vai:
echo    1. Instalar o Python, se ainda nao existir
echo    2. Baixar o sistema
echo    3. Criar o atalho "Cartao Ponto" na Area de Trabalho
echo.
echo  Nada e apagado do seu computador.
echo.
pause
echo.

REM ---------- 1. Python ----------
where python >nul 2>&1
if errorlevel 1 (
    echo Instalando o Python...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo.
        echo [ERRO] O Python nao esta instalado e o winget nao esta disponivel.
        echo        Instale o Python manualmente em https://www.python.org/downloads/
        echo        marcando a opcao "Add Python to PATH", e rode este instalador de novo.
        echo.
        pause
        exit /b 1
    )
    winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
    echo.
    echo ============================================================
    echo   QUASE LA
    echo ============================================================
    echo.
    echo  O Python acabou de ser instalado. Feche esta janela e abra
    echo  o Instalar.bat MAIS UMA VEZ para concluir.
    echo.
    pause
    exit /b 0
)
echo Python encontrado.

REM ---------- 2. baixar o sistema ----------
echo.
echo Baixando o sistema...
set "TEMPZIP=%TEMP%\cartaoponto.zip"
set "TEMPDIR=%TEMP%\cartaoponto_extraido"

if exist "%TEMPDIR%" rmdir /s /q "%TEMPDIR%"

powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri '%PACOTE%' -OutFile '%TEMPZIP%' -UseBasicParsing; Expand-Archive -Path '%TEMPZIP%' -DestinationPath '%TEMPDIR%' -Force; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel baixar. Verifique a conexao com a internet.
    echo.
    pause
    exit /b 1
)

REM a pasta extraida tem um nome com o ramo; pega a primeira que houver
for /d %%D in ("%TEMPDIR%\*") do set "ORIGEM=%%D"

if not exist "%ORIGEM%\main.py" (
    echo [ERRO] O pacote baixado veio incompleto.
    pause
    exit /b 1
)

echo Instalando em: %DESTINO%
if not exist "%DESTINO%" mkdir "%DESTINO%"
xcopy "%ORIGEM%\*" "%DESTINO%\" /E /I /Y /Q >nul

del "%TEMPZIP%" >nul 2>&1
rmdir /s /q "%TEMPDIR%" >nul 2>&1

REM ---------- 3. dependencias ----------
echo.
echo Instalando os componentes do sistema. Isso pode demorar alguns minutos.
pushd "%DESTINO%"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
popd

REM ---------- 4. atalho na area de trabalho ----------
echo.
echo Criando o atalho na Area de Trabalho...

set "PYTHONW="
for /f "delims=" %%P in ('where pythonw 2^>nul') do if not defined PYTHONW set "PYTHONW=%%P"
if not defined PYTHONW set "PYTHONW=pythonw.exe"

powershell -NoProfile -Command "$a=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Cartao Ponto.lnk')); $a.TargetPath='%PYTHONW%'; $a.Arguments='\"%DESTINO%\main.py\"'; $a.WorkingDirectory='%DESTINO%'; $a.IconLocation='%SystemRoot%\System32\shell32.dll,21'; $a.Description='Sistema de Cartao Ponto'; $a.Save()"

echo.
echo ============================================================
echo   PRONTO
echo ============================================================
echo.
echo  O atalho "Cartao Ponto" esta na sua Area de Trabalho.
echo  O sistema se atualiza sozinho toda vez que voce abre.
echo.
pause
