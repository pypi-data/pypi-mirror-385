from collections.abc import Sequence

import click
import MetaTrader5 as mt5

from mtcli_trade.conf import DIGITOS


def exibir_posicoes(posicoes: Sequence, symbol: str | None = None):
    """Imprime no terminal as posições passadas (lista pode estar vazia)."""
    if not posicoes:
        msg = (
            f"Nenhuma posição aberta para {symbol}."
            if symbol
            else "Nenhuma posição aberta encontrada."
        )
        click.echo(msg)
        return

    click.echo(f"Posições abertas{' para ' + symbol if symbol else ''}:\n")
    for p in posicoes:
        tipo = "COMPRA" if p.type == mt5.POSITION_TYPE_BUY else "VENDA"
        symbol_txt = getattr(p, "symbol", "N/A")
        volume = getattr(p, "volume", 0.0)
        price_open = getattr(p, "price_open", 0.0)
        profit = getattr(p, "profit", 0.0)

        click.echo(
            f"{tipo} {symbol_txt} {volume:.2f} {price_open:.{DIGITOS}f} lucro {profit:.2f}"
        )


def exibir_resultados_encerramento(resultados):
    """Exibe os resultados retornados pelo model ao encerrar posições."""
    if not resultados:
        click.echo("Nenhuma tentativa de encerramento foi realizada.")
        return

    sucesso = [
        r
        for r in resultados
        if r is not None and getattr(r, "retcode", None) == mt5.TRADE_RETCODE_DONE
    ]
    falhas = [
        r
        for r in resultados
        if r is None or getattr(r, "retcode", None) != mt5.TRADE_RETCODE_DONE
    ]

    if sucesso:
        click.echo("Posições encerradas com sucesso:")
        for r in sucesso:
            order = getattr(r, "order", "N/A")
            request = getattr(r, "request", None)
            symbol = getattr(request, "symbol", "N/A") if request is not None else "N/A"
            volume = getattr(r, "volume", "N/A")
            price = getattr(r, "price", "N/A")
            click.echo(f"  order={order} ativo={symbol} volume={volume} preco={price}")

    if falhas:
        click.echo("\nAlgumas posições não foram encerradas corretamente:")
        for r in falhas:
            click.echo(f"  Falha: {r}")
