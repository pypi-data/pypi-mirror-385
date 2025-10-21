import click
from mtcli_volume.controllers.volume_controller import calcular_volume_profile
from mtcli_volume.views.volume_view import exibir_volume_profile
from mtcli_volume.conf import SYMBOL, PERIOD, BARS, STEP, VOLUME


@click.command(
    "volume",
    help="Exibe o Volume Profile, agrupando volumes por faixa de preço no histórico recente."
)
@click.version_option(package_name="mtcli-volume")
@click.option("--symbol", "-s", default=SYMBOL, help="Símbolo do ativo (default WIN$N).")
@click.option("--period", "-p", default=PERIOD, help="Timeframe (ex: M1, M5, H1).")
@click.option("--bars", "-b", default=BARS, help="Número de barras (default 566).")
@click.option(
    "--step", "-e", type=float, default=STEP,
    help="Tamanho do agrupamento de preços (default 100)."
)
@click.option(
    "--volume", "-v", default=VOLUME,
    help="Tipo de volume (tick ou real), default tick."
)
def volume(symbol, period, bars, step, volume):
    """Exibe o Volume Profile agrupando volumes por faixa de preço."""
    profile, stats = calcular_volume_profile(symbol, period, bars, step, volume)
    exibir_volume_profile(profile, stats, symbol)


if __name__ == "__main__":
    volume()
