"""Monta o PDF dos cartões: uma página por funcionário, pronto para imprimir."""

from pathlib import Path

import pymupdf

LARGURA_A4, ALTURA_A4 = 595, 842
MARGEM = 36

FONTE = "helv"
FONTE_NEGRITO = "hebo"

ALTURA_TITULO = 30
ALTURA_CABECALHO = 18
ALTURA_LINHA = 17
ALTURA_ASSINATURA = 44

# Largura de cada coluna: data + 6 marcações
LARGURAS = [52, 78, 78, 78, 78, 78, 78]

GRUPOS = (("MANHÃ", 1, 2), ("TARDE", 3, 4), ("HORA EXTRA", 5, 6))
SUBTITULOS = ("ENTRADA", "SAÍDA", "ENTRADA", "SAÍDA", "ENTRADA", "SAÍDA")

PRETO = (0, 0, 0)
CINZA = (0.45, 0.45, 0.45)


def _posicoes_das_colunas(largura_total):
    """Coordenada x onde cada coluna começa, centralizando a tabela."""
    inicio = (largura_total - sum(LARGURAS)) / 2
    posicoes = [inicio]
    for largura in LARGURAS:
        posicoes.append(posicoes[-1] + largura)
    return posicoes


def _texto_centralizado(pagina, texto, x0, x1, y, tamanho=8, negrito=False):
    if not texto:
        return
    fonte = FONTE_NEGRITO if negrito else FONTE
    largura = pymupdf.get_text_length(str(texto), fontname=fonte, fontsize=tamanho)

    # Reduz a fonte se o texto não couber na coluna (ocorrências longas)
    disponivel = (x1 - x0) - 4
    while largura > disponivel and tamanho > 5:
        tamanho -= 0.5
        largura = pymupdf.get_text_length(str(texto), fontname=fonte, fontsize=tamanho)

    pagina.insert_text(
        (x0 + ((x1 - x0) - largura) / 2, y),
        str(texto), fontname=fonte, fontsize=tamanho, color=PRETO,
    )


def desenhar_cartao(pagina, cartao):
    """Desenha um cartão inteiro numa página."""
    x = _posicoes_das_colunas(pagina.rect.width)
    esquerda, direita = x[0], x[-1]
    y = MARGEM

    # ---- título ----
    pagina.draw_rect(pymupdf.Rect(esquerda, y, direita, y + ALTURA_TITULO), color=PRETO, width=0.8)
    _texto_centralizado(pagina, "CARTÃO PONTO", esquerda, direita, y + 20, 15, negrito=True)
    y += ALTURA_TITULO

    # ---- empresa ----
    pagina.draw_rect(pymupdf.Rect(esquerda, y, direita, y + ALTURA_CABECALHO), color=PRETO, width=0.8)
    pagina.insert_text((esquerda + 5, y + 13), "EMPRESA:", fontname=FONTE_NEGRITO, fontsize=8)
    pagina.insert_text((esquerda + 60, y + 13), cartao["empresa"], fontname=FONTE, fontsize=8)
    y += ALTURA_CABECALHO

    # ---- nome e competência ----
    pagina.draw_rect(pymupdf.Rect(esquerda, y, direita, y + ALTURA_CABECALHO), color=PRETO, width=0.8)
    pagina.insert_text((esquerda + 5, y + 13), "NOME:", fontname=FONTE_NEGRITO, fontsize=8)
    pagina.insert_text((esquerda + 60, y + 13), cartao["nome"], fontname=FONTE, fontsize=8)

    competencia = f"MÊS/ANO: {cartao['competencia']}"
    largura = pymupdf.get_text_length(competencia, fontname=FONTE_NEGRITO, fontsize=8)
    pagina.insert_text((direita - largura - 12, y + 13), competencia,
                       fontname=FONTE_NEGRITO, fontsize=8)
    y += ALTURA_CABECALHO

    # ---- cabeçalho da tabela (duas linhas) ----
    topo_cabecalho = y
    pagina.draw_rect(pymupdf.Rect(esquerda, y, direita, y + ALTURA_CABECALHO * 2),
                     color=PRETO, width=0.8)

    _texto_centralizado(pagina, "DATA", x[0], x[1], y + ALTURA_CABECALHO + 5, 8, negrito=True)
    for titulo, primeira, ultima in GRUPOS:
        _texto_centralizado(pagina, titulo, x[primeira], x[ultima + 1], y + 13, 8, negrito=True)
        pagina.draw_line(pymupdf.Point(x[primeira], y),
                         pymupdf.Point(x[primeira], y + ALTURA_CABECALHO * 2),
                         color=PRETO, width=0.8)

    y += ALTURA_CABECALHO
    pagina.draw_line(pymupdf.Point(x[1], y), pymupdf.Point(direita, y), color=PRETO, width=0.8)
    for coluna, subtitulo in enumerate(SUBTITULOS, start=1):
        _texto_centralizado(pagina, subtitulo, x[coluna], x[coluna + 1], y + 13, 7, negrito=True)
        pagina.draw_line(pymupdf.Point(x[coluna], y),
                         pymupdf.Point(x[coluna], y + ALTURA_CABECALHO),
                         color=CINZA, width=0.4)
    y += ALTURA_CABECALHO

    # ---- linhas dos dias ----
    topo_tabela = y
    for registro in cartao["linhas"]:
        _texto_centralizado(pagina, registro["data"], x[0], x[1], y + 12, 8)
        for coluna, valor in enumerate(registro["colunas"], start=1):
            _texto_centralizado(pagina, valor, x[coluna], x[coluna + 1], y + 12, 8)

        y += ALTURA_LINHA
        pagina.draw_line(pymupdf.Point(esquerda, y), pymupdf.Point(direita, y),
                         color=CINZA, width=0.3)

    # bordas verticais da tabela
    for posicao in x:
        cor = PRETO if posicao in (esquerda, direita) else CINZA
        largura_linha = 0.8 if cor == PRETO else 0.4
        pagina.draw_line(pymupdf.Point(posicao, topo_tabela),
                         pymupdf.Point(posicao, y), color=cor, width=largura_linha)
    pagina.draw_rect(pymupdf.Rect(esquerda, topo_cabecalho, direita, y),
                     color=PRETO, width=0.8)

    # ---- assinatura ----
    y += 16
    pagina.insert_text((esquerda + 5, y + 26), "ASSINATURA DO EMPREGADO:",
                       fontname=FONTE_NEGRITO, fontsize=8)
    pagina.draw_line(pymupdf.Point(esquerda + 160, y + 28),
                     pymupdf.Point(direita - 10, y + 28), color=PRETO, width=0.6)


def gerar_pdf(cartoes, caminho):
    """Grava um PDF com uma página por cartão."""
    if not cartoes:
        raise ValueError("Nenhum cartão para gerar.")

    documento = pymupdf.open()
    for cartao in cartoes:
        pagina = documento.new_page(width=LARGURA_A4, height=ALTURA_A4)
        desenhar_cartao(pagina, cartao)

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    documento.save(caminho)
    documento.close()
    return caminho
