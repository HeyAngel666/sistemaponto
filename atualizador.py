"""Mantém o sistema atualizado, sem depender de Git.

Baixa a versão publicada do projeto e substitui os arquivos do programa.
Nada do que você gera (cartões, planilhas) é tocado.
"""

import io
import json
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPOSITORIO = "HeyAngel666/sistemaponto"
RAMO = "claude/sharp-goodall-j5y3n3"

URL_VERSAO = f"https://api.github.com/repos/{REPOSITORIO}/commits/{RAMO}"
URL_PACOTE = f"https://codeload.github.com/{REPOSITORIO}/zip/refs/heads/{RAMO}"

PASTA = Path(__file__).resolve().parent
ARQUIVO_VERSAO = PASTA / "versao.txt"

TEMPO_LIMITE = 30

# O que nunca é sobrescrito pela atualização
NAO_ATUALIZAR = {"cartoes", "versao.txt", "__pycache__", ".git"}


class SemInternet(Exception):
    pass


def versao_instalada():
    if ARQUIVO_VERSAO.exists():
        return ARQUIVO_VERSAO.read_text(encoding="utf-8").strip()
    return ""


def versao_publicada():
    try:
        requisicao = urllib.request.Request(
            URL_VERSAO, headers={"Accept": "application/vnd.github+json"}
        )
        with urllib.request.urlopen(requisicao, timeout=TEMPO_LIMITE) as resposta:
            return json.load(resposta)["sha"]
    except (urllib.error.URLError, TimeoutError, OSError) as erro:
        raise SemInternet(f"Não foi possível verificar atualizações: {erro}") from erro


def tem_atualizacao():
    return versao_publicada() != versao_instalada()


def baixar_pacote():
    try:
        with urllib.request.urlopen(URL_PACOTE, timeout=TEMPO_LIMITE * 4) as resposta:
            return zipfile.ZipFile(io.BytesIO(resposta.read()))
    except (urllib.error.URLError, TimeoutError, OSError) as erro:
        raise SemInternet(f"Não foi possível baixar a atualização: {erro}") from erro


def atualizar(destino=None):
    """Baixa a versão publicada e substitui os arquivos. Devolve o que mudou."""
    destino = Path(destino or PASTA)
    destino.mkdir(parents=True, exist_ok=True)

    pacote = baixar_pacote()
    sha = versao_publicada()

    with tempfile.TemporaryDirectory() as temporaria:
        pacote.extractall(temporaria)

        # o zip vem com uma pasta raiz (nome-do-repositorio-ramo)
        extraidos = list(Path(temporaria).iterdir())
        raiz = extraidos[0] if len(extraidos) == 1 else Path(temporaria)

        alterados = []
        for origem in raiz.rglob("*"):
            if origem.is_dir():
                continue

            relativo = origem.relative_to(raiz)
            if relativo.parts[0] in NAO_ATUALIZAR:
                continue

            alvo = destino / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)

            if not alvo.exists() or alvo.read_bytes() != origem.read_bytes():
                shutil.copy2(origem, alvo)
                alterados.append(str(relativo))

    (destino / ARQUIVO_VERSAO.name).write_text(sha, encoding="utf-8")
    return alterados


def atualizar_em_silencio():
    """Usado na abertura do programa: sem internet, segue a vida."""
    try:
        if tem_atualizacao():
            return atualizar()
    except SemInternet:
        pass
    except Exception:
        pass
    return []


if __name__ == "__main__":
    try:
        if not tem_atualizacao():
            print("O sistema já está na versão mais recente.")
            sys.exit(0)

        print("Baixando atualização...")
        alterados = atualizar()
        print(f"Pronto: {len(alterados)} arquivo(s) atualizado(s).")
        for nome in alterados:
            print("  -", nome)

    except SemInternet as erro:
        print(erro)
        print("Verifique a conexão e tente de novo.")
        sys.exit(1)
