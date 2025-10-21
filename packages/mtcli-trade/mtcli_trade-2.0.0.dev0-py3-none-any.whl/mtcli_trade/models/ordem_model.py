"""
Modelo de execução de ordens no MetaTrader 5 (camada Model do MVC).
Responsável por criar, enviar e inicializar ordens de compra/venda.
"""

import MetaTrader5 as mt5

from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao

log = setup_logger()


def inicializar(symbol: str):
    """
    Inicializa o símbolo no MetaTrader 5 e retorna seu tick atual.
    Retorna None se houver falha na seleção ou na obtenção do tick.
    """
    with mt5_conexao():
        if not mt5.symbol_select(symbol, True):
            log.error(f"Erro ao selecionar símbolo {symbol}")
            return None

        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            log.error(f"Erro ao obter cotação de {symbol}")
            return None

        log.debug(f"Símbolo {symbol} inicializado com sucesso.")
        return tick


def criar_ordem(
    symbol: str,
    lot: float,
    sl: float,
    tp: float,
    price: float,
    order_type: int,
    limit: bool,
) -> dict:
    """
    Cria e retorna um dicionário com os parâmetros de uma ordem MT5.
    Suporta ordens a mercado e ordens pendentes (limit).
    """
    try:
        info = mt5.symbol_info(symbol)
        point = getattr(info, "point", 0.01)
    except Exception:
        point = 0.01
        log.warning(
            f"Símbolo {symbol} sem informações completas; usando point padrão 0.01."
        )

    sl_price = (
        price - sl * point
        if order_type in (mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT)
        else price + sl * point
    )
    tp_price = (
        price + tp * point
        if order_type in (mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT)
        else price - tp * point
    )

    ordem = {
        "action": mt5.TRADE_ACTION_PENDING if limit else mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 10,
        "magic": 1000,
        "comment": "Ordem mtcli",
        "type_time": mt5.ORDER_TIME_DAY,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    log.debug(f"Ordem criada: {ordem}")
    return ordem


def enviar_ordem(ordem, limit: bool):
    """Envia a ordem e retorna resultado formatado, mesmo em falha."""
    resultado = mt5.order_send(ordem)

    if resultado is None:
        return {
            "retcode": None,
            "comment": "Erro: ordem não enviada. Possível mercado fechado.",
        }

    return {
        "retcode": resultado.retcode,
        "comment": getattr(resultado, "comment", ""),
        "order": getattr(resultado, "order", None),
        "symbol": ordem["symbol"],
        "type": "LIMIT" if limit else "MARKET",
        "volume": ordem["volume"],
        "price": ordem["price"],
    }
