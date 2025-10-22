import click

from mtcli_volume.conf import BARS, PERIOD, STEP, SYMBOL, VOLUME
from mtcli_volume.controllers.volume_controller import calcular_volume_profile
from mtcli_volume.views.volume_view import exibir_volume_profile


@click.command(
    "volume",
    help="Exibe o Volume Profile, agrupando volumes por faixa de preço no histórico recente.",
)
@click.version_option(package_name="mtcli-volume")
@click.option(
    "--symbol", "-s", default=SYMBOL, show_default=True, help="Simbolo do ativo."
)
@click.option(
    "--period",
    "-p",
    default=PERIOD,
    show_default=True,
    help="Timeframe (ex: M1, M5, H1).",
)
@click.option("--bars", "-b", default=BARS, show_default=True, help="Numero de barras.")
@click.option(
    "--step",
    "-e",
    type=float,
    default=STEP,
    show_default=True,
    help="Tamanho do agrupamento de precos.",
)
@click.option(
    "--volume",
    "-v",
    default=VOLUME,
    show_default=True,
    help="Tipo de volume (tick ou real).",
)
def volume(symbol, period, bars, step, volume):
    """Exibe o Volume Profile agrupando volumes por faixa de preço."""
    profile, stats = calcular_volume_profile(symbol, period, bars, step, volume)
    exibir_volume_profile(profile, stats, symbol)


if __name__ == "__main__":
    volume()
