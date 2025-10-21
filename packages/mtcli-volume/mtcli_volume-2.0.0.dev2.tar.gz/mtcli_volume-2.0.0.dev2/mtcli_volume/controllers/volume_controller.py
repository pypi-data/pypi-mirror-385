from mtcli.logger import setup_logger
from mtcli_volume.models.volume_model import (
    calcular_estatisticas,
    calcular_profile,
    obter_rates,
)

log = setup_logger()


def calcular_volume_profile(symbol, period, bars, step, volume):
    """Controla o fluxo de cálculo do volume profile."""
    volume = volume.lower().strip()
    if volume not in ["tick", "real"]:
        log.error(f"Tipo de volume inválido: {volume}. Use 'tick' ou 'real'.")
        raise ValueError(f"Tipo de volume inválido: {volume}. Use 'tick' ou 'real'.")

    rates = obter_rates(symbol, period, bars)
    if not rates:
        log.error("Falha ao obter dados de preços para cálculo do volume profile.")
        return {}, {}

    profile = calcular_profile(rates, step, volume)
    stats = calcular_estatisticas(profile)

    return profile, stats
