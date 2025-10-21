import click

from mtcli_trade.controllers.ordens_controller import (
    cancelar_ordens_pendentes,
    obter_ordens_pendentes,
)
from mtcli_trade.views.ordens_view import exibir_cancelar_ordens, exibir_ordens


@click.command("orders", help="Lista ou cancela ordens pendentes no MetaTrader 5.")
@click.version_option(package_name="mtcli-trade")
@click.option("--symbol", "-s", default=None, help="Símbolo do ativo para filtrar.")
@click.option(
    "--cancelar", "-c", is_flag=True, help="Cancela todas as ordens pendentes."
)
def ordens_cmd(symbol, cancelar):
    if cancelar:
        resultados = cancelar_ordens_pendentes(symbol)
        exibir_cancelar_ordens(resultados, symbol)
        return

    ordens = obter_ordens_pendentes(symbol)
    exibir_ordens(ordens)


if __name__ == "__main__":
    ordens_cmd()
