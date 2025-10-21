from mtcli_trade.commands.compra_cli import compra_cmd
from mtcli_trade.commands.ordens_cli import ordens_cmd
from mtcli_trade.commands.posicoes_cli import posicoes_cmd
from mtcli_trade.commands.venda_cli import venda_cmd


def register(cli):
    cli.add_command(compra_cmd, name="compra")
    cli.add_command(venda_cmd, name="venda")
    cli.add_command(ordens_cmd, name="ordens")
    cli.add_command(posicoes_cmd, name="posicoes")
