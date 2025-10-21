"""
Camada Model responsável pela lógica de ordens de compra no MetaTrader 5.
"""

import MetaTrader5 as mt5

from mtcli.logger import setup_logger
from mtcli_trade.conf import LOSS_LIMIT, STATUS_FILE
from mtcli_trade.models.ordem_model import criar_ordem, enviar_ordem, inicializar
from mtcli_trade.models.risco_model import controlar_risco

log = setup_logger()


def verificar_risco() -> bool:
    """Retorna True se o controle de risco bloquear a operação."""
    try:
        return controlar_risco(STATUS_FILE, LOSS_LIMIT)
    except Exception as e:
        log.exception(f"Erro ao verificar risco: {e}")
        return True


def preparar_ordem_compra(
    symbol: str,
    lot: float,
    sl: float,
    tp: float,
    limit: bool,
    preco: float | None = None,
):
    """
    Prepara uma ordem de compra (market ou limit) para envio.

    Retorna:
        tuple: (ordem, limit) se sucesso, ou (None, None) se falha.
    """
    tick = inicializar(symbol)
    if not tick:
        log.error(f"Falha ao inicializar tick para símbolo {symbol}")
        return None, None

    if limit:
        if preco is None:
            raise ValueError("Preço obrigatório para ordens pendentes (--limit).")
        price = preco
        order_type = mt5.ORDER_TYPE_BUY_LIMIT
    else:
        price = tick.ask
        order_type = mt5.ORDER_TYPE_BUY

    ordem = criar_ordem(symbol, lot, sl, tp, price, order_type, limit)
    log.debug(f"Ordem preparada: {ordem}")
    return ordem, limit


def enviar_ordem_compra(ordem: dict, limit: bool):
    """
    Envia uma ordem de compra válida para o MetaTrader 5.

    Args:
        ordem (dict): Estrutura de ordem gerada pelo Model.
        limit (bool): Define se é ordem limitada (True) ou a mercado (False).

    Returns:
        dict: Resultado retornado pela função `enviar_ordem()`.
    """
    if not ordem:
        log.error("Ordem inválida, cancelando envio.")
        return {"retcode": None, "comment": "Ordem inválida."}

    try:
        resultado = enviar_ordem(ordem, limit)
        log.debug(f"Resultado do envio da ordem: {resultado}")
        return resultado
    except Exception as e:
        log.exception(f"Erro ao enviar ordem: {e}")
        return {"retcode": None, "comment": str(e)}
