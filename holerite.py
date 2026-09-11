"""Leitura dos holerites em PDF.

O PDF vem com o texto embaralhado: o sistema de folha grava as letras como
desenhos, sem dizer qual letra é qual. Cada letra é identificada aqui pelo
desenho dela (o mesmo desenho sempre representa a mesma letra), usando a
tabela de referência do arquivo letras_holerite.json.
"""

import hashlib
import json
import re
from pathlib import Path

import pymupdf

from empresas import EMPRESAS

PASTA = Path(__file__).resolve().parent
ARQUIVO_LETRAS = PASTA / "letras_holerite.json"

# Largura padrão do glifo; larguras diferentes são espaçamento, não letra
LARGURA_GLIFO = 6.00
TOLERANCIA = 0.2

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}


class HoleriteIlegivel(Exception):
    pass


def carregar_letras():
    with open(ARQUIVO_LETRAS, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _desenhos_da_fonte(doc, xref_fonte):
    """{código usado no texto: impressão digital do desenho da letra}"""
    encoding = doc.xref_get_key(xref_fonte, "Encoding")
    if encoding[0] != "xref":
        return {}

    diferencas = doc.xref_get_key(int(encoding[1].split()[0]), "Differences")[1]

    codigo_para_nome, atual = {}, 0
    for token in re.findall(r"\d+|/[^\s\[\]/]+", diferencas):
        if token.startswith("/"):
            codigo_para_nome[atual] = token[1:]
            atual += 1
        else:
            atual = int(token)

    desenhos = doc.xref_get_key(xref_fonte, "CharProcs")[1]
    nome_para_xref = {
        m.group(1): int(m.group(2))
        for m in re.finditer(r"/([^\s/]+)\s+(\d+)\s+0\s+R", desenhos)
    }

    return {
        codigo: hashlib.sha1(doc.xref_stream(nome_para_xref[nome])).hexdigest()[:16]
        for codigo, nome in codigo_para_nome.items()
        if nome in nome_para_xref
    }


def ler_paginas(caminho_pdf):
    """Devolve, para cada página, a lista de linhas de texto já decifradas."""
    letras = carregar_letras()
    doc = pymupdf.open(caminho_pdf)

    cache_fontes = {}
    nao_reconhecidas = set()
    paginas = []

    for numero in range(doc.page_count):
        fontes = doc[numero].get_fonts()
        if not fontes:
            paginas.append([])
            continue

        xref = fontes[0][0]
        if xref not in cache_fontes:
            cache_fontes[xref] = _desenhos_da_fonte(doc, xref)
        desenhos = cache_fontes[xref]

        linhas = []
        for bloco in doc[numero].get_text("rawdict")["blocks"]:
            for linha in bloco.get("lines", []):
                texto = []
                for span in linha["spans"]:
                    for caractere in span["chars"]:
                        x0, _, x1, _ = caractere["bbox"]
                        codigo = ord(caractere["c"])
                        if codigo == 32 and abs((x1 - x0) - LARGURA_GLIFO) > TOLERANCIA:
                            texto.append(" ")
                            continue
                        letra = letras.get(desenhos.get(codigo, ""))
                        if letra is None:
                            nao_reconhecidas.add(desenhos.get(codigo, "?"))
                            letra = "?"
                        texto.append(letra)
                conteudo = "".join(texto).strip()
                if conteudo:
                    linhas.append(conteudo)

        # cada página traz a mesma via duas vezes
        paginas.append(list(dict.fromkeys(linhas)))

    doc.close()
    return paginas, nao_reconhecidas


def _empresa_pelo_cnpj(linhas):
    for linha in linhas:
        achado = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", linha)
        if not achado:
            continue
        cnpj = achado.group(0)
        for codigo, empresa in EMPRESAS.items():
            if empresa["cnpj"] == cnpj:
                return codigo
    return None


def _competencia(linhas):
    for linha in linhas:
        achado = re.search(r"Mês:\s*(\w+)/(\d{4})", linha)
        if achado:
            mes = MESES.get(achado.group(1).lower())
            if mes:
                return mes, int(achado.group(2))
    return None, None


def _numero_seguinte(linhas, indice):
    """Valor da coluna Referência, que vem na linha seguinte à rubrica."""
    if indice + 1 < len(linhas) and re.fullmatch(r"\d+", linhas[indice + 1]):
        return int(linhas[indice + 1])
    return 0


def _horas_seguintes(linhas, indice):
    """Referência de horas, no formato HH:MM, convertida em horas decimais."""
    if indice + 1 >= len(linhas):
        return 0.0

    achado = re.fullmatch(r"(\d{1,3}):(\d{2})", linhas[indice + 1])
    if achado:
        return int(achado.group(1)) + int(achado.group(2)) / 60

    if re.fullmatch(r"\d{1,3}", linhas[indice + 1]):
        return float(linhas[indice + 1])

    return 0.0


def _percentual_da_extra(linha):
    """Percentual da rubrica de hora extra: 50, 100 ou None se não for extra.

    Ex: 'HORA EXTRA 050%' -> 50 | 'HORA EXTRA 100%' -> 100
    O DSR sobre horas extras não entra: é reflexo, não hora trabalhada.
    """
    # Cobre HORA EXTRA, HORAS EXTRAS, H.EXTRA, ADICIONAL HORA EXTRA...
    texto = linha.upper()
    if "EXTRA" not in texto or "DSR" in texto:
        return None

    achado = re.search(r"(\d{2,3})\s*%", texto)
    if achado:
        return 100 if int(achado.group(1)) >= 100 else 50

    # Sem percentual no nome, assume o adicional comum de dia útil
    return 50


# Rubricas em horas que não são hora extra e por isso não entram no cartão
RUBRICAS_DE_HORAS_CONHECIDAS = ("HORAS TRABALHADAS", "HORAS NORMAIS", "DSR")


def _rubrica_de_horas_nao_lida(linha, linhas, indice):
    """Rubrica lançada em horas que o sistema não soube classificar.

    Serve de rede de segurança: se a folha usar um nome diferente para a
    hora extra, isso aparece como aviso em vez de sumir do cartão.
    """
    texto = linha.upper()
    if any(conhecida in texto for conhecida in RUBRICAS_DE_HORAS_CONHECIDAS):
        return False
    if not re.match(r"^\d{5}\s", linha):
        return False
    return bool(
        indice + 1 < len(linhas)
        and re.fullmatch(r"\d{1,3}:\d{2}", linhas[indice + 1])
    )


def ler_holerite(caminho_pdf):
    """Lê o PDF e devolve a lista de funcionários encontrados."""
    paginas, nao_reconhecidas = ler_paginas(caminho_pdf)

    funcionarios = []
    for linhas in paginas:
        if not linhas:
            continue

        empresa_codigo = _empresa_pelo_cnpj(linhas)
        mes, ano = _competencia(linhas)

        registro = {
            "empresa_codigo": empresa_codigo,
            "mes": mes,
            "ano": ano,
            "codigo": "",
            "nome": "",
            "admissao": "",
            "faltas": 0,
            "horas_extras": 0.0,
            "horas_extras_100": 0.0,
            "dias_ferias": 0,
            "avisos": [],
        }

        rubricas_estranhas = set()

        for indice, linha in enumerate(linhas):
            cabecalho = re.match(r"^(\d{5})\s+([A-ZÇÁÉÍÓÚÃÕÂÊÔ][A-ZÇÁÉÍÓÚÃÕÂÊÔ\s]+)$", linha)
            if cabecalho and not registro["nome"]:
                descricao = cabecalho.group(2).strip()
                if not any(p in descricao for p in
                           ("SALARIO", "DESCONTO", "FALTAS", "FERIAS", "ARREDONDAMENTO",
                            "CREDITO", "ADICIONAL", "DEDUCAO", "LIQUIDO", "DESC")):
                    registro["codigo"] = cabecalho.group(1)
                    registro["nome"] = descricao

            if linha.startswith("Admissão:"):
                registro["admissao"] = linha.replace("Admissão:", "").strip()

            if re.search(r"\bFALTAS$", linha):
                registro["faltas"] = _numero_seguinte(linhas, indice)

            percentual = _percentual_da_extra(linha)
            if percentual == 100:
                registro["horas_extras_100"] += _horas_seguintes(linhas, indice)
            elif percentual == 50:
                registro["horas_extras"] += _horas_seguintes(linhas, indice)
            elif _rubrica_de_horas_nao_lida(linha, linhas, indice):
                rubricas_estranhas.add(linha)

            if "FERIAS" in linha and "DEDUCAO" not in linha:
                dias = re.search(r"SALARIO NORMAL", " ".join(linhas))
                if dias:
                    for outra in linhas:
                        proporcao = re.fullmatch(r"(\d{1,2})/(\d{2})", outra)
                        if proporcao:
                            trabalhados, total = int(proporcao.group(1)), int(proporcao.group(2))
                            if trabalhados < total:
                                registro["dias_ferias"] = total - trabalhados
                            break

        if not registro["nome"]:
            continue

        registro["horas_extras"] = round(registro["horas_extras"], 2)
        registro["horas_extras_100"] = round(registro["horas_extras_100"], 2)

        for rubrica in sorted(rubricas_estranhas):
            registro["avisos"].append(f"rubrica em horas não reconhecida: {rubrica}")

        if registro["empresa_codigo"] is None:
            registro["avisos"].append("empresa não reconhecida pelo CNPJ")
        if "?" in registro["nome"]:
            registro["avisos"].append("nome com letra não reconhecida")

        funcionarios.append(registro)

    if not funcionarios:
        raise HoleriteIlegivel(
            "Nenhum holerite reconhecido neste PDF. Verifique se é o arquivo certo."
        )

    if nao_reconhecidas:
        funcionarios[0]["avisos"].append(
            f"{len(nao_reconhecidas)} símbolo(s) novo(s) no PDF — confira os nomes"
        )

    return funcionarios


def dia_inicial_por_admissao(registro):
    """Se foi admitido dentro do mês do holerite, devolve o dia da admissão."""
    achado = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", registro.get("admissao", ""))
    if not achado:
        return 1
    dia, mes, ano = (int(p) for p in achado.groups())
    if mes == registro["mes"] and ano == registro["ano"]:
        return dia
    return 1
