"""Guarda os períodos de férias informados, para não precisar digitar de novo.

O holerite traz quanto foi pago de férias, mas não as datas. O período é
digitado uma vez (pelo aviso de férias) e fica guardado: nos meses que ele
atravessa, o sistema preenche sozinho.

Dois arquivos:
- ferias_iniciais.json: períodos já conhecidos, que vêm com o sistema
- ferias.json: os que você digitou neste computador (a atualização não mexe)
"""

import json
from datetime import datetime

from gerador import _pasta_de_trabalho, _pasta_do_programa, ler_periodo

ARQUIVO_INICIAL = _pasta_do_programa() / "ferias_iniciais.json"
ARQUIVO_LOCAL = _pasta_de_trabalho() / "ferias.json"


def _chave(empresa_codigo, codigo, nome):
    # O código do funcionário é único dentro da empresa; o nome é a reserva
    return f"{empresa_codigo}|{codigo or nome}".upper()


def _ler(arquivo):
    try:
        with open(arquivo, encoding="utf-8") as entrada:
            return json.load(entrada)
    except (OSError, ValueError):
        return {}


def carregar():
    periodos = _ler(ARQUIVO_INICIAL)
    for chave, lista in _ler(ARQUIVO_LOCAL).items():
        periodos.setdefault(chave, [])
        for periodo in lista:
            if periodo not in periodos[chave]:
                periodos[chave].append(periodo)
    return periodos


def guardar(empresa_codigo, codigo, nome, texto, mes, ano):
    """Guarda o período digitado. Devolve as datas, já validadas."""
    inicio, fim = ler_periodo(texto, mes, ano)
    periodo = {"nome": nome, "inicio": inicio.strftime("%Y-%m-%d"), "fim": fim.strftime("%Y-%m-%d")}

    locais = _ler(ARQUIVO_LOCAL)
    lista = locais.setdefault(_chave(empresa_codigo, codigo, nome), [])
    # um período novo que se sobrepõe a um antigo é a correção dele
    lista[:] = [p for p in lista if p["fim"] < periodo["inicio"] or p["inicio"] > periodo["fim"]]
    lista.append(periodo)

    ARQUIVO_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_LOCAL, "w", encoding="utf-8") as saida:
        json.dump(locais, saida, ensure_ascii=False, indent=1)
    return inicio, fim


def periodo_do_mes(empresa_codigo, codigo, nome, mes, ano):
    """O período guardado que passa por este mês, como texto, ou None."""
    primeiro = f"{ano:04d}-{mes:02d}-01"
    proximo_mes = f"{ano + mes // 12:04d}-{mes % 12 + 1:02d}-01"

    # os digitados neste computador vêm por último e têm preferência
    for periodo in reversed(carregar().get(_chave(empresa_codigo, codigo, nome), [])):
        if periodo["inicio"] < proximo_mes and periodo["fim"] >= primeiro:
            inicio = datetime.strptime(periodo["inicio"], "%Y-%m-%d")
            fim = datetime.strptime(periodo["fim"], "%Y-%m-%d")
            return f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}"
    return None
