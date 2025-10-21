from collections.abc import Sequence

from mtcli.logger import setup_logger
from mtcli_trade.models.ordens_model import (
    buscar_ordens,
    cancelar_ordens,
    formatar_ordem,
)

log = setup_logger()


def obter_ordens_pendentes(symbol: str | None = None) -> Sequence:
    """Retorna lista de ordens pendentes formatadas (pode ser vazia)."""
    ordens_raw = buscar_ordens(symbol)

    if not ordens_raw:
        log.info(
            f"Nenhuma ordem pendente para {symbol}."
            if symbol
            else "Nenhuma ordem pendente encontrada"
        )
        return []

    ordens = []
    for o in ordens_raw:
        dados = formatar_ordem(o)
        log.info(
            f"{dados['tipo']} | {dados['symbol']} | volume: {dados['volume']} | preço: {dados['preco']} | ticket: {dados['ticket']}"
        )
        ordens.append(dados)
    return ordens


def cancelar_ordens_pendentes(symbol: str | None = None):
    """Cancela ordens pendentes via model e retorna resultados."""
    try:
        resultados = cancelar_ordens(symbol)
    except Exception as e:
        log.error(f"Erro ao cancelar ordens: {e}")
        raise
    return resultados
