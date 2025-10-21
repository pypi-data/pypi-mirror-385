"""
Camada Controller: coordena a execução de ordens de venda.
"""

from mtcli.logger import setup_logger
from mtcli_trade.models.venda_model import (
    enviar_ordem_venda,
    preparar_ordem_venda,
    verificar_risco,
)

log = setup_logger()


def executar_venda(
    symbol: str,
    lot: float,
    sl: float,
    tp: float,
    limit: bool,
    preco: float | None = None,
) -> dict:
    """
    Controla o fluxo completo da execução de venda:
    - verifica risco,
    - prepara a ordem,
    - envia ao MetaTrader 5,
    - retorna o resultado estruturado.
    """

    if verificar_risco():
        log.info("Envio de ordem bloqueado por risco diário.")
        return {"status": "bloqueado", "mensagem": "Limite de prejuízo atingido."}

    try:
        ordem, is_limit = preparar_ordem_venda(symbol, lot, sl, tp, limit, preco)
        if ordem is None:
            return {
                "status": "falha",
                "mensagem": "Falha ao preparar ordem.",
                "resultado": {
                    "tipo": "LIMIT" if limit else "MARKET",
                    "preco": preco,
                    "retcode": None,
                    "mensagem": "Tick inválido ou símbolo não encontrado.",
                },
            }

        resultado = enviar_ordem_venda(ordem, is_limit)

        # MetaTrader 5 retorna 10009 = TRADE_RETCODE_DONE (sucesso)
        if resultado.get("retcode") not in (10009,):
            log.warning(f"Ordem recusada pelo MT5: {resultado}")
            return {
                "status": "falha",
                "mensagem": "MetaTrader 5 recusou a ordem.",
                "resultado": resultado,
            }

        log.info(f"✅ Ordem de compra enviada com sucesso para {symbol}.")
        return {"status": "ok", "resultado": resultado}

    except ValueError as e:
        log.error(f"Erro de validação: {e}")
        return {"status": "erro", "mensagem": str(e)}
    except Exception as e:
        log.exception(f"Erro inesperado ao executar venda: {e}")
        return {"status": "erro", "mensagem": str(e)}
