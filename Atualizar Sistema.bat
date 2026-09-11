@echo off
REM ============================================================
REM  Baixa a versao mais recente do sistema.
REM  De dois cliques neste arquivo sempre que houver novidade.
REM ============================================================
cd /d "%~dp0"

where git >nul 2>&1
if errorlevel 1 (
    echo.
    echo O Git nao esta instalado neste computador.
    echo Baixe em: https://git-scm.com/download/win
    echo.
    pause
    exit /b
)

if not exist ".git" (
    echo.
    echo Esta pasta nao foi criada pelo Git, entao nao da para atualizar
    echo automaticamente. Peca as instrucoes para baixar a pasta de novo.
    echo.
    pause
    exit /b
)

echo Baixando a versao mais recente...
echo.
git pull

echo.
echo ============================================================
echo  Atualizado. Pode fechar esta janela e abrir o sistema.
echo ============================================================
pause
