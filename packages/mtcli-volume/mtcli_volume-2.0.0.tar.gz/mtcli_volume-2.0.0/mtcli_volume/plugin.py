from mtcli_volume.commands.volume_cli import volume


def register(cli):
    cli.add_command(volume, name="volume")
