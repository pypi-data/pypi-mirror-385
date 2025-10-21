from collections import defaultdict

import MetaTrader5 as mt5

from mtcli.logger import setup_logger
from mtcli.models.rates_model import RatesModel
from mtcli.mt5_context import mt5_conexao
from mtcli_volume.conf import DIGITOS

log = setup_logger()


def obter_rates(symbol, period, bars):
    """Obtém os dados históricos de preços via MetaTrader 5."""
    with mt5_conexao():
        tf = getattr(mt5, f"TIMEFRAME_{period.upper()}", None)
        if tf is None:
            log.error(f"Timeframe inválido: {period}")
            return

        if not mt5.symbol_select(symbol, True):
            log.error(f"Erro ao selecionar símbolo {symbol}")
            return

        rates = RatesModel(symbol, period, bars).get_data()

        if not rates:
            log.error("Erro: não foi possível obter os dados históricos.")
            return

    return rates


def calcular_profile(rates, step, volume="tick"):
    """Calcula o volume total por faixa de preço, suportando dicionários, objetos ou tuplas."""
    from collections.abc import Mapping

    profile = defaultdict(int)

    for r in rates:
        # Detecta se r é dict, objeto com atributos ou tupla
        if isinstance(r, Mapping):  # dict
            preco = r["close"]
            tick_volume = r["tick_volume"]
            real_volume = r.get("real_volume", tick_volume)
        elif hasattr(r, "close"):  # objeto com atributos
            preco = r.close
            tick_volume = r.tick_volume
            real_volume = getattr(r, "real_volume", tick_volume)
        elif isinstance(r, (tuple, list)) and len(r) >= 6:  # tupla com campos esperados
            preco = r[4]  # índice típico de 'close' em rates do MT5
            tick_volume = r[5]
            real_volume = r[6] if len(r) > 6 else tick_volume
        else:
            raise TypeError(f"Formato de rate desconhecido: {type(r)}")

        faixa = round(round(preco / step) * step, DIGITOS)
        profile[faixa] += tick_volume if volume == "tick" else real_volume

    return dict(profile)


def calcular_estatisticas(profile):
    """Calcula POC, área de valor (70%), HVNs e LVNs."""
    if profile is None or len(profile) == 0:
        return {
            "poc": None,
            "area_valor": (None, None),
            "hvns": [],
            "lvns": [],
        }

    # Ordena faixas de preço pelo volume em ordem decrescente
    volumes_ordenados = sorted(profile.items(), key=lambda x: x[1], reverse=True)
    poc = volumes_ordenados[0][0]

    # Área de valor (70% do volume)
    total_volume = sum(profile.values())
    acumulado = 0
    faixas_area_valor = []
    for faixa, vol in volumes_ordenados:
        acumulado += vol
        faixas_area_valor.append(faixa)
        if acumulado >= total_volume * 0.7:
            break
    area_valor = (min(faixas_area_valor), max(faixas_area_valor))

    # HVNs (High Volume Nodes) e LVNs (Low Volume Nodes)
    media = total_volume / len(profile)
    hvns = sorted([faixa for faixa, vol in profile.items() if vol >= media * 1.5])
    lvns = sorted([faixa for faixa, vol in profile.items() if vol <= media * 0.5])

    return {
        "poc": poc,
        "area_valor": area_valor,
        "hvns": hvns,
        "lvns": lvns,
    }
