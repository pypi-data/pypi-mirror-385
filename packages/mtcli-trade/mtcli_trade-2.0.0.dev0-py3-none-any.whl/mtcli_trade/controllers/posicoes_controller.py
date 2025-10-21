from collections.abc import Sequence

from mtcli.logger import setup_logger
from mtcli_trade.models.posicoes_model import buscar_posicoes, encerra_posicoes

log = setup_logger()


def obter_posicoes(symbol: str | None = None) -> Sequence:
    """Retorna uma sequência (possivelmente vazia) de posições abertas para o symbol ou todas."""
    try:
        posicoes = buscar_posicoes(symbol)
    except Exception as e:
        log.error(f"Erro ao buscar posições: {e}")
        raise

    # normalize: sempre devolve lista/sequence (não None)
    if not posicoes:
        return []
    return posicoes


def encerrar_posicoes(symbol: str | None = None):
    """Encerrar posições (retorna a lista de resultados produzida pelo model)."""
    try:
        resultados = encerra_posicoes(symbol)
    except Exception as e:
        log.error(f"Erro ao encerrar posições: {e}")
        raise
    return resultados
