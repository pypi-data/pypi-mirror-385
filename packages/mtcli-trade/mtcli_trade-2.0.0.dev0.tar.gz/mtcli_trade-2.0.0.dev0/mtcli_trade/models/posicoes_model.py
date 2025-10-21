"""
Model responsável por gerenciar posições abertas e controle de risco diário.
"""

import MetaTrader5 as mt5

from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao
from mtcli_trade.conf import LOSS_LIMIT, STATUS_FILE
from mtcli_trade.models.ordem_model import criar_ordem, enviar_ordem
from mtcli_trade.models.risco_model import controlar_risco

log = setup_logger()


def buscar_posicoes(symbol: str | None = None):
    """
    Retorna as posições abertas.
    - Se symbol for None, retorna todas as posições abertas.
    - Se symbol for informado, retorna apenas as posições desse símbolo.
    """
    with mt5_conexao():
        try:
            if symbol:
                log.debug(f"Buscando posições para o símbolo: {symbol}")
                posicoes = mt5.positions_get(symbol=symbol)
            else:
                log.debug("Buscando todas as posições abertas.")
                posicoes = mt5.positions_get()

            if not posicoes:
                log.info("Nenhuma posição encontrada.")
                return []

            return list(posicoes)

        except Exception as e:
            log.error(f"Erro ao buscar posições: {e}")
            return []


def encerra_posicoes(symbol: str | None = None):
    """
    Encerra todas as posições abertas, ou apenas as de um símbolo específico.
    Retorna uma lista com o resultado de cada tentativa de encerramento.
    """
    resultados = []
    with mt5_conexao():
        try:
            posicoes = (
                mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
            )
            if not posicoes:
                log.info("Nenhuma posição aberta encontrada.")
                return resultados

            for p in posicoes:
                tick = mt5.symbol_info_tick(p.symbol)
                if not tick:
                    log.error(f"Falha ao obter tick para {p.symbol}")
                    continue

                # Define tipo da operação inversa (encerramento)
                if p.type == mt5.POSITION_TYPE_BUY:
                    tipo_ordem = mt5.ORDER_TYPE_SELL
                    preco = tick.bid
                else:
                    tipo_ordem = mt5.ORDER_TYPE_BUY
                    preco = tick.ask

                ordem = criar_ordem(
                    symbol=p.symbol,
                    lot=p.volume,
                    sl=0,
                    tp=0,
                    price=preco,
                    order_type=tipo_ordem,
                    limit=False,
                )

                try:
                    resultado = enviar_ordem(ordem, limit=False)
                except Exception as e:
                    log.exception(f"Erro ao enviar ordem de encerramento: {e}")
                    resultado = {"retcode": None, "comment": str(e)}

                # Normaliza resultado em dict
                retcode = getattr(resultado, "retcode", resultado.get("retcode", None))
                resultados.append(
                    {"symbol": p.symbol, "ticket": p.ticket, "retcode": retcode}
                )

                if retcode in (mt5.TRADE_RETCODE_DONE, 10009):
                    log.info(f"Posição {p.ticket} ({p.symbol}) encerrada com sucesso.")
                else:
                    log.error(
                        f"Falha ao encerrar {p.symbol} (ticket {p.ticket}): retcode={retcode}"
                    )

        except Exception as e:
            log.exception(f"Erro ao encerrar posições: {e}")

    return resultados


def editar_posicao(ticket, sl=None, tp=None):
    """Edita stop loss ou take profit de uma posição existente."""
    with mt5_conexao():
        posicoes = mt5.positions_get()
        if not posicoes:
            log.warning("Nenhuma posição encontrada para editar.")
            return False

        posicao = next((p for p in posicoes if p.ticket == ticket), None)
        if not posicao:
            log.error(f"Posição com ticket {ticket} não encontrada.")
            return False

        requisicao = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": posicao.ticket,
            "symbol": posicao.symbol,
            "sl": posicao.sl if sl is None else sl,
            "tp": posicao.tp if tp is None else tp,
        }

        resultado = mt5.order_send(requisicao)

        if resultado.retcode == mt5.TRADE_RETCODE_DONE:
            log.info(f"Posição {ticket} editada com sucesso.")
            return True

        log.error(f"Falha ao editar posição {ticket}: retcode={resultado.retcode}")
        return False


def verificar_risco_diario():
    """Executa controle de risco diário."""
    if controlar_risco(STATUS_FILE, LOSS_LIMIT):
        log.warning("Operações bloqueadas: limite de prejuízo diário atingido.")
        return True
    return False
