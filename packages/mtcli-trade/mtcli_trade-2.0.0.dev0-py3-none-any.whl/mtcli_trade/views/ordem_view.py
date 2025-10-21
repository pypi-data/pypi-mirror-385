"""
Camada View: responsável pela exibição dos resultados da operação de compra/venda.
"""

import click


def exibir_resultado_ordem(resultado: dict):
    """Exibe o resultado do envio da órdem no terminal."""
    status = resultado.get("status")
    dados = resultado.get("resultado", {})

    retcode = dados.get("retcode")
    comment = dados.get("comment") or "Sem comentário"

    if status == "bloqueado":
        click.echo("Ordem bloqueada: limite de prejuízo diário atingido.")

    elif status == "falha":
        click.echo("Falha ao preparar a ordem")
        click.echo(f"Retcode: {retcode} | Comentário: {comment}")

    elif status == "erro":
        click.echo(f"Erro: {resultado.get('mensagem')}")
        click.echo(f"Retcode: {retcode} | Comentário: {comment}")

    elif status == "ok":
        click.echo("Ordem enviada com sucesso.")
        click.echo(f"Retcode: {retcode} | Comentário: {comment}")
        click.echo(f"Detalhes: {dados}")

    else:
        click.echo("Estado desconhecido.")
