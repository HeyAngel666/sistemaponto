"""Geração do cartão ponto em Excel.

As regras de cálculo (horas extras, faltas, atestados e feriados) são as
mesmas desde a primeira versão do sistema. O que mudou foi a origem dos
horários: agora vêm do cadastro da empresa (empresas.py).
"""

import calendar
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import holidays
from openpyxl import load_workbook

from empresas import (
    DOMINGO,
    NOME_DIA_SEMANA,
    cabecalho_empresa,
    horario_do_dia,
    obter_empresa,
)


# =====================================
# CONFIGURAÇÕES
# =====================================
def _pasta_do_programa():
    """Onde ficam os arquivos do sistema (dentro do .exe, quando empacotado)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _pasta_de_trabalho():
    """Onde os cartões são salvos (ao lado do .exe, quando empacotado)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


ARQUIVO_MODELO = _pasta_do_programa() / "modelo" / "MODELO - CARTÃO PONTO.xlsx"
PASTA_SAIDA = _pasta_de_trabalho() / "cartoes"

# Onde a tabela de dias começa na planilha modelo
LINHA_INICIAL = 6

# Células fixas do modelo
CELULA_EMPRESA = "B2"
CELULA_NOME = "B3"
CELULA_MES_ANO = "F3"

# Colunas da tabela
COL_DATA = 1
COL_ENTRADA_MANHA = 2
COL_SAIDA_MANHA = 3
COL_ENTRADA_TARDE = 4
COL_SAIDA_TARDE = 5
COL_ENTRADA_EXTRA = 6
COL_SAIDA_EXTRA = 7

# Limites de horas extras por dia (em minutos)
EXTRA_MIN_POR_DIA = 30
EXTRA_MAX_POR_DIA = 120

FERIADOS_BR = holidays.Brazil()

MESES_PT = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO",
}

_TRADUCAO_FERIADOS = {
    "New Year's Day": "CONFRATERNIZAÇÃO UNIVERSAL",
    "New Year's Day (observed)": "CONFRATERNIZAÇÃO UNIVERSAL",
    "Carnival": "CARNAVAL",
    "Carnival Monday": "CARNAVAL",
    "Carnival Tuesday": "CARNAVAL",
    "Ash Wednesday": "QUARTA-FEIRA DE CINZAS",
    "Good Friday": "SEXTA-FEIRA SANTA",
    "Easter Sunday": "PÁSCOA",
    "Tiradentes' Day": "TIRADENTES",
    "Tiradentes Day": "TIRADENTES",
    "Worker's Day": "DIA DO TRABALHO",
    "Workers' Day": "DIA DO TRABALHO",
    "Labor Day": "DIA DO TRABALHO",
    "Corpus Christi": "CORPUS CHRISTI",
    "Independence Day": "INDEPENDÊNCIA DO BRASIL",
    "Our Lady of Aparecida": "NOSSA SENHORA APARECIDA",
    "All Souls' Day": "FINADOS",
    "All Souls Day": "FINADOS",
    "Republic Day": "PROCLAMAÇÃO DA REPÚBLICA",
    "Republic Proclamation Day": "PROCLAMAÇÃO DA REPÚBLICA",
    "Christmas Day": "NATAL",
    "Christmas": "NATAL",
}


def traduzir_feriado(nome):
    """Nome do feriado em português."""
    return _TRADUCAO_FERIADOS.get(nome, str(nome).upper())


# =====================================
# ESCRITA NA PLANILHA
# =====================================
def set_valor(ws, row, col, value):
    """Escreve respeitando células mescladas (escreve sempre na âncora)."""
    cell = ws.cell(row=row, column=col)
    for merged in ws.merged_cells.ranges:
        if cell.coordinate in merged:
            ws.cell(merged.min_row, merged.min_col).value = value
            return
    cell.value = value


def preencher_descricao(ws, linha, data, descricao):
    """Preenche a linha inteira com uma ocorrência (DOMINGO, FALTA, etc)."""
    set_valor(ws, linha, COL_DATA, data.strftime("%d/%m"))
    for col in range(COL_ENTRADA_MANHA, COL_SAIDA_EXTRA + 1):
        set_valor(ws, linha, col, descricao)


def calcular_horario(hora_str, variar):
    """Converte 'HH:MM' em datetime, com variação opcional de ±5 minutos."""
    base = datetime.strptime(hora_str, "%H:%M")
    if variar:
        base += timedelta(minutes=random.randint(-5, 5))
    return base


# =====================================
# DISTRIBUIÇÃO DAS HORAS EXTRAS
# =====================================
def distribuir_exato(total_minutos, dias_validos):
    """Distribui o total de minutos extras entre os dias disponíveis.

    Cada dia que recebe extra fica entre EXTRA_MIN_POR_DIA e
    EXTRA_MAX_POR_DIA minutos.
    """
    dias_validos = list(dias_validos)

    if total_minutos <= 0:
        return {d: 0 for d in dias_validos}

    max_dias_possiveis = len(dias_validos)
    if max_dias_possiveis == 0:
        raise ValueError("Não há dias disponíveis para lançar horas extras.")

    if total_minutos > max_dias_possiveis * EXTRA_MAX_POR_DIA:
        raise ValueError(
            "Horas extras excedem o máximo possível "
            f"({EXTRA_MAX_POR_DIA} min/dia x {max_dias_possiveis} dias)."
        )

    min_dias_necessarios = -(-total_minutos // EXTRA_MAX_POR_DIA)
    max_dias_necessarios = min(total_minutos // EXTRA_MIN_POR_DIA, max_dias_possiveis)

    if max_dias_necessarios < min_dias_necessarios:
        raise ValueError(
            "Não é possível distribuir as horas extras respeitando o mínimo de "
            f"{EXTRA_MIN_POR_DIA} min e o máximo de {EXTRA_MAX_POR_DIA} min por dia."
        )

    qtd_dias = random.randint(int(min_dias_necessarios), int(max_dias_necessarios))
    dias_escolhidos = random.sample(dias_validos, qtd_dias)

    extras = {d: EXTRA_MIN_POR_DIA for d in dias_escolhidos}
    restante = total_minutos - EXTRA_MIN_POR_DIA * qtd_dias

    dias = dias_escolhidos[:]
    while restante > 0:
        progresso = False
        random.shuffle(dias)

        for d in dias:
            if restante <= 0:
                break

            livre = EXTRA_MAX_POR_DIA - extras[d]
            if livre <= 0:
                continue

            valor = min(random.choice([5, 10, 15, 20, 30]), livre, restante)
            extras[d] += valor
            restante -= valor
            progresso = True

        if not progresso:
            raise ValueError("Erro ao distribuir as horas extras.")

    for d in dias_validos:
        extras.setdefault(d, 0)

    return extras


# =====================================
# GERAÇÃO DO CARTÃO
# =====================================
def gerar_cartao(empresa_codigo, nome, mes, ano, horas_extras=0, faltas=0,
                 atestados=0, dia_inicio=1, dia_fim=None, pasta_saida=None):
    """Gera o cartão ponto de um funcionário e devolve o caminho do arquivo.

    dia_inicio / dia_fim delimitam o período ativo no mês (admissão e
    desligamento). Dias após dia_fim são marcados como DESLIGADO.
    """
    empresa = obter_empresa(empresa_codigo)
    validar_entrada(nome, mes, ano, horas_extras, faltas, atestados)

    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    dia_fim = ultimo_dia_mes if dia_fim in (None, "") else int(dia_fim)
    dia_inicio = int(dia_inicio or 1)

    if not 1 <= dia_inicio <= ultimo_dia_mes:
        raise ValueError(f"Dia inicial deve estar entre 1 e {ultimo_dia_mes}.")
    if not dia_inicio <= dia_fim <= ultimo_dia_mes:
        raise ValueError(
            f"Dia final deve estar entre {dia_inicio} e {ultimo_dia_mes}."
        )

    if not ARQUIVO_MODELO.exists():
        raise FileNotFoundError(f"Planilha modelo não encontrada: {ARQUIVO_MODELO}")

    dias_trabalhados = empresa["dias_trabalhados"]

    # Dias em que o funcionário deveria trabalhar (sem feriados)
    dias_uteis = [
        d for d in range(dia_inicio, dia_fim + 1)
        if datetime(ano, mes, d).weekday() in dias_trabalhados
        and datetime(ano, mes, d).date() not in FERIADOS_BR
    ]

    if faltas + atestados > len(dias_uteis):
        raise ValueError(
            f"Faltas + atestados ({faltas + atestados}) excedem os dias úteis "
            f"do período ({len(dias_uteis)})."
        )

    disponiveis = dias_uteis[:]
    dias_falta = random.sample(disponiveis, min(faltas, len(disponiveis)))
    for d in dias_falta:
        disponiveis.remove(d)

    dias_atestado = random.sample(disponiveis, min(atestados, len(disponiveis)))

    dias_extras = [
        d for d in dias_uteis
        if d not in dias_falta and d not in dias_atestado
    ]
    extras = distribuir_exato(int(round(horas_extras * 60)), dias_extras)

    # ---- Preenchimento da planilha ----
    wb = load_workbook(ARQUIVO_MODELO)
    ws = wb.active

    ws[CELULA_EMPRESA] = cabecalho_empresa(empresa)
    ws[CELULA_NOME] = nome
    ws[CELULA_MES_ANO] = f"{MESES_PT[mes]}/{ano}"

    linha = LINHA_INICIAL + (dia_inicio - 1)

    for d in range(dia_inicio, ultimo_dia_mes + 1):
        data = datetime(ano, mes, d)
        dia_semana = data.weekday()

        if d > dia_fim:
            preencher_descricao(ws, linha, data, "DESLIGADO")
        elif dia_semana == DOMINGO or dia_semana not in dias_trabalhados:
            preencher_descricao(ws, linha, data, NOME_DIA_SEMANA[dia_semana])
        elif data.date() in FERIADOS_BR:
            preencher_descricao(
                ws, linha, data, traduzir_feriado(FERIADOS_BR.get(data.date()))
            )
        elif d in dias_falta:
            preencher_descricao(ws, linha, data, "FALTA")
        elif d in dias_atestado:
            preencher_descricao(ws, linha, data, "ATESTADO")
        else:
            preencher_dia_trabalhado(ws, linha, data, empresa, extras.get(d, 0))

        linha += 1

    pasta = Path(pasta_saida) if pasta_saida else PASTA_SAIDA
    pasta = pasta / f"{ano}-{mes:02d}"
    pasta.mkdir(parents=True, exist_ok=True)

    caminho = pasta / f"{nome_arquivo_seguro(nome)} - {mes:02d}-{ano}.xlsx"
    wb.save(caminho)
    return caminho


def preencher_dia_trabalhado(ws, linha, data, empresa, extra_min):
    """Preenche as marcações de um dia efetivamente trabalhado."""
    horario = horario_do_dia(empresa, data.weekday())
    variacoes = empresa["variacoes"]

    marcacoes = {
        campo: calcular_horario(horario[campo], variacoes.get(campo, False))
        for campo in ("entrada", "saida_almoco", "volta_almoco", "saida")
    }

    set_valor(ws, linha, COL_DATA, data.strftime("%d/%m"))
    set_valor(ws, linha, COL_ENTRADA_MANHA, marcacoes["entrada"].strftime("%H:%M"))
    set_valor(ws, linha, COL_SAIDA_MANHA, marcacoes["saida_almoco"].strftime("%H:%M"))
    set_valor(ws, linha, COL_ENTRADA_TARDE, marcacoes["volta_almoco"].strftime("%H:%M"))
    set_valor(ws, linha, COL_SAIDA_TARDE, marcacoes["saida"].strftime("%H:%M"))

    if extra_min > 0:
        fim_extra = marcacoes["saida"] + timedelta(minutes=extra_min)
        set_valor(ws, linha, COL_ENTRADA_EXTRA, marcacoes["saida"].strftime("%H:%M"))
        set_valor(ws, linha, COL_SAIDA_EXTRA, fim_extra.strftime("%H:%M"))
    else:
        set_valor(ws, linha, COL_ENTRADA_EXTRA, "")
        set_valor(ws, linha, COL_SAIDA_EXTRA, "")


def validar_entrada(nome, mes, ano, horas_extras, faltas, atestados):
    if not str(nome).strip():
        raise ValueError("Informe o nome do funcionário.")
    if mes not in MESES_PT:
        raise ValueError("Mês deve ser um número de 1 a 12.")
    if not 2000 <= ano <= 2100:
        raise ValueError("Ano inválido.")
    if horas_extras < 0:
        raise ValueError("Horas extras não podem ser negativas.")
    if faltas < 0 or atestados < 0:
        raise ValueError("Faltas e atestados não podem ser negativos.")


def nome_arquivo_seguro(nome):
    """Remove caracteres que o Windows não aceita em nome de arquivo."""
    invalidos = '<>:"/\\|?*'
    limpo = "".join("-" if c in invalidos else c for c in str(nome))
    return " ".join(limpo.split()).strip(". ")
