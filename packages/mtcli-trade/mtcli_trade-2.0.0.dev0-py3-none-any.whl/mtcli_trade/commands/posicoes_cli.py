import click

from mtcli_trade.controllers.posicoes_controller import (
    encerrar_posicoes,
    obter_posicoes,
)
from mtcli_trade.views.posicoes_view import (
    exibir_posicoes,
    exibir_resultados_encerramento,
)


@click.command(
    "positions",
    help="Lista ou encerra as posições abertas, mostrando lucro/prejuízo atual e detalhes por ativo.",
)
@click.version_option(package_name="mtcli-trade")
@click.option("--symbol", "-s", default=None, help="Símbolo do ativo (opcional)")
@click.option(
    "--zerar",
    "-z",
    is_flag=True,
    default=False,
    help="Encerra todas as posições ou de um ativo específico.",
)
def posicoes_cmd(symbol, zerar):
    """Lista ou zera todas as posições abertas (ou de um ativo)."""
    posicoes = obter_posicoes(symbol)

    if zerar:
        resultados = encerrar_posicoes(symbol)
        exibir_resultados_encerramento(resultados)
        return

    exibir_posicoes(posicoes, symbol)


if __name__ == "__main__":
    posicoes_cmd()
