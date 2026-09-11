"""Cadastro das empresas e suas escalas de trabalho.

Para incluir/alterar uma empresa, basta editar o dicionário EMPRESAS abaixo.

Dias da semana (padrão Python): 0=segunda, 1=terça, 2=quarta,
3=quinta, 4=sexta, 5=sábado, 6=domingo.
"""

SEGUNDA, TERCA, QUARTA, QUINTA, SEXTA, SABADO, DOMINGO = range(7)

NOME_DIA_SEMANA = {
    SEGUNDA: "SEGUNDA-FEIRA",
    TERCA: "TERÇA-FEIRA",
    QUARTA: "QUARTA-FEIRA",
    QUINTA: "QUINTA-FEIRA",
    SEXTA: "SEXTA-FEIRA",
    SABADO: "SÁBADO",
    DOMINGO: "DOMINGO",
}


EMPRESAS = {
    "MONTSUL": {
        "nome": "MONTSUL MONTAGENS E LOCAÇÕES LTDA",
        "cnpj": "57.066.123/0001-42",
        "dias_trabalhados": [SEGUNDA, TERCA, QUARTA, QUINTA, SEXTA],
        "horario_padrao": {
            "entrada": "07:00",
            "saida_almoco": "12:00",
            "volta_almoco": "13:00",
            "saida": "17:00",
        },
        # Sexta-feira encerra mais cedo
        "horario_excecoes": {
            SEXTA: {"saida": "16:00"},
        },
        # Variação aleatória de ±5 min na marcação
        "variacoes": {
            "entrada": True,
            "saida_almoco": False,
            "volta_almoco": False,
            "saida": True,
        },
    },
    "VAGNER": {
        "nome": "VAGNER BENTO PEREIRA",
        "cnpj": "39.436.093/0001-37",
        "dias_trabalhados": [SEGUNDA, TERCA, QUARTA, QUINTA, SEXTA, SABADO],
        "horario_padrao": {
            "entrada": "06:00",
            "saida_almoco": "11:00",
            "volta_almoco": "12:00",
            "saida": "14:20",
        },
        "horario_excecoes": {},
        "variacoes": {
            "entrada": True,
            "saida_almoco": False,
            "volta_almoco": False,
            "saida": True,
        },
    },
}


def listar_empresas():
    """Retorna os códigos das empresas cadastradas."""
    return list(EMPRESAS.keys())


def obter_empresa(codigo):
    """Retorna os dados da empresa pelo código (ex: 'MONTSUL')."""
    codigo = str(codigo).strip().upper()
    if codigo not in EMPRESAS:
        disponiveis = ", ".join(listar_empresas())
        raise ValueError(
            f"Empresa '{codigo}' não cadastrada. Disponíveis: {disponiveis}"
        )
    return EMPRESAS[codigo]


def cabecalho_empresa(empresa):
    """Texto que vai na linha EMPRESA do cartão."""
    return f"{empresa['nome']} - CNPJ: {empresa['cnpj']}"


def horario_do_dia(empresa, dia_semana):
    """Horário da jornada para um dia da semana, já com as exceções aplicadas."""
    horario = dict(empresa["horario_padrao"])
    horario.update(empresa.get("horario_excecoes", {}).get(dia_semana, {}))
    return horario


def resumo_jornada(empresa):
    """Resumo legível da jornada, para exibir na interface."""
    dias = empresa["dias_trabalhados"]
    nomes_curtos = {
        SEGUNDA: "Seg", TERCA: "Ter", QUARTA: "Qua", QUINTA: "Qui",
        SEXTA: "Sex", SABADO: "Sáb", DOMINGO: "Dom",
    }
    faixa = f"{nomes_curtos[dias[0]]} a {nomes_curtos[dias[-1]]}"

    padrao = empresa["horario_padrao"]
    linhas = [
        f"Dias: {faixa}",
        f"Jornada: {padrao['entrada']} às {padrao['saida']} "
        f"(almoço {padrao['saida_almoco']} - {padrao['volta_almoco']})",
    ]

    for dia, ajuste in empresa.get("horario_excecoes", {}).items():
        detalhes = ", ".join(f"{campo}: {valor}" for campo, valor in ajuste.items())
        linhas.append(f"Exceção {NOME_DIA_SEMANA[dia].title()}: {detalhes}")

    return "\n".join(linhas)
