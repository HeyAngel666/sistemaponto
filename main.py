"""Ponto de entrada do sistema de cartão ponto."""

import atualizador

if __name__ == "__main__":
    # Antes de abrir a tela, para que a versão nova já valha nesta sessão
    atualizador.atualizar_em_silencio()

    from interface import abrir

    abrir()
