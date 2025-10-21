import MetaTrader5 as mt5

MT5_RETCODE_DESCRICOES = {
    mt5.TRADE_RETCODE_DONE: "Ordem executada com sucesso.",
    mt5.TRADE_RETCODE_DONE_PARTIAL: "Ordem parcialmente executada.",
    mt5.TRADE_RETCODE_ERROR: "Erro genérico no envio.",
    mt5.TRADE_RETCODE_INVALID: "Parâmetros da ordem inválidos.",
    mt5.TRADE_RETCODE_INVALID_VOLUME: "Volume inválido.",
    mt5.TRADE_RETCODE_MARKET_CLOSED: "Mercado fechado.",
    mt5.TRADE_RETCODE_CONNECTION: "Sem conexão com o servidor.",
    mt5.TRADE_RETCODE_REJECT: "Ordem rejeitada.",
    mt5.TRADE_RETCODE_TIMEOUT: "Tempo de envio excedido.",
    mt5.TRADE_RETCODE_TRADE_DISABLED: "Trading desabilitado para o símbolo.",
    mt5.TRADE_RETCODE_NO_MONEY: "Margem insuficiente.",
    mt5.TRADE_RETCODE_PRICE_CHANGED: "Preço mudou antes da execução.",
    mt5.TRADE_RETCODE_ORDER_CHANGED: "SL ou TP alterados.",
}
