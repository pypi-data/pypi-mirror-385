from typing import Any

import MetaTrader5 as mt5

from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao
from mtcli_trade.conf import DIGITOS

log = setup_logger()


def buscar_ordens(symbol: str | None = None):
    """Recupera ordens pendentes do MetaTrader 5."""
    with mt5_conexao():
        return mt5.orders_get(symbol=symbol) if symbol else mt5.orders_get()


def formatar_ordem(ordem):
    tipo = (
        "COMPRA"
        if ordem.type == mt5.ORDER_TYPE_BUY_LIMIT
        else "VENDA"
        if ordem.type == mt5.ORDER_TYPE_SELL_LIMIT
        else str(ordem.type)
    )
    return {
        "tipo": tipo,
        "symbol": ordem.symbol,
        "volume": ordem.volume_current,
        "preco": round(ordem.price_open, DIGITOS),
        "ticket": ordem.ticket,
    }


def cancelar_ordens(symbol: str | None = None) -> list[Any]:
    """Cancela todas as ordens (ou as de um símbolo específico)."""
    resultados = []
    with mt5_conexao():
        ordens = mt5.orders_get(symbol=symbol) if symbol else mt5.orders_get()

        if not ordens:
            log.info(
                f"Nenhuma ordem pendente para {symbol}"
                if symbol
                else "Nenhuma ordem pendente encontrada."
            )
            return resultados

        for ordem in ordens:
            req = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ordem.ticket,
                "symbol": ordem.symbol,
                "magic": 1000,
                "comment": "Cancelamento via CLI",
            }

            resultado = mt5.order_send(req)
            if (
                resultado
                and getattr(resultado, "retcode", None) == mt5.TRADE_RETCODE_DONE
            ):
                log.info(f"Ordem cancelada: ticket {ordem.ticket} ({ordem.symbol})")
            else:
                log.error(
                    f"Falha ao cancelar {ordem.ticket} código {getattr(resultado, 'retcode', 'N/A')}"
                )
            resultados.append(resultado)

    return resultados
