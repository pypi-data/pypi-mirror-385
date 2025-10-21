import click
import csv
from datetime import datetime
from mtcli.logger import setup_logger
from mtcli_volume.conf import DIGITOS

log = setup_logger()
BARRA_CHAR = "#"  # Pode mudar para "■" ou "=" se UTF-8 for garantido


def exibir_volume_profile(profile, stats, symbol, exporta_csv=False, sem_histograma=False):
    """Exibe o volume profile no terminal ou exporta para CSV."""
    if not profile:
        click.echo(f"Nenhum dado disponível para {symbol}.")
        return

    dados_ordenados = sorted(profile.items(), reverse=True)

    if exporta_csv:
        try:
            data_str = datetime.now().strftime("%Y%m%d_%H%M")
            nome_arquivo = f"volume_profile_{symbol}_{data_str}.csv"
            with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Faixa de Preço", "Volume"])
                writer.writerows(dados_ordenados)
            click.echo(f"Exportado para {nome_arquivo}")
            log.info(f"Exportado para {nome_arquivo}")
        except Exception as e:
            log.error(f"Erro ao exportar CSV: {e}")
            click.echo(f"Erro ao exportar CSV: {e}")
        return

    # Exibição textual
    click.echo(f"\nVolume Profile {symbol}\n")
    max_vol = max(profile.values())
    for preco, vol in dados_ordenados:
        barra = "" if sem_histograma else BARRA_CHAR * (vol // max(1, max_vol // 50))
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
