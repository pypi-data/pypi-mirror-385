"""Controle automático de risco baseado no lucro/prejuízo da conta."""

from datetime import date

from mtcli_risco.models.checar_model import (
    cancelar_todas_ordens,
    carregar_estado,
    encerrar_todas_posicoes,
    risco_excedido,
    salvar_estado,
)

from mtcli.logger import setup_logger

log = setup_logger()


def controlar_risco(arq_estado, limite):
    """Verifica limites de risco e executa ações de proteção."""
    hoje = date.today()
    estado = carregar_estado(arq_estado)

    if estado.get("data") != hoje.isoformat():
        estado["data"] = hoje.isoformat()
        estado["bloqueado"] = False
        salvar_estado(arq_estado, hoje, False)

    if estado.get("bloqueado"):
        log.info("Bloqueado hoje por risco. Nenhuma ordem deve ser enviada")
        return True

    if risco_excedido(limite):
        log.info(
            f"Limite diário {limite} excedido. Encerrando posições e bloqueando novas ordens"
        )
        encerrar_todas_posicoes()
        cancelar_todas_ordens()
        salvar_estado(arq_estado, hoje, True)
        return True

    return False
