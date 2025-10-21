import click

from mtcli_volume.conf import DIGITOS

BARRA_CHAR = "#"  # Pode mudar para "■" ou "=" se UTF-8 for garantido


def exibir_volume_profile(profile, stats, symbol):
    """Exibe o volume profile no terminal."""
    if not profile:
        click.echo(f"Nenhum dado disponível para {symbol}")
        return

    dados_ordenados = sorted(profile.items(), reverse=True)

    click.echo(f"\nVolume Profile {symbol}\n")
    max_vol = max(profile.values())
    for preco, vol in dados_ordenados:
        barra = BARRA_CHAR * (vol // max(1, max_vol // 50))
        click.echo(f"{preco:>8.{DIGITOS}f} {vol:>6} {barra}")

    # Estatísticas
    if stats.get("poc") is not None:
        click.echo(f"\nPOC (Preço de Maior Volume): {stats['poc']:.{DIGITOS}f}")
        click.echo(
            f"Área de Valor: {stats['area_valor'][0]:.{DIGITOS}f} a {stats['area_valor'][1]:.{DIGITOS}f}"
        )
        click.echo(f"HVNs: {stats['hvns']}")
        click.echo(f"LVNs: {stats['lvns']}")
    else:
        click.echo("\nEstatísticas indisponíveis (dados insuficientes).")
