from pathlib import Path

import click

from .ui import run


@click.command()
@click.argument('mazes_path')
@click.option('-h', '--host', type=str, default='127.0.0.1',
              help='Listen on IP (default: 127.0.0.1).')
@click.option('-p', '--port', type=int, default=6574,
              help='Listen on port (default: 6574).')
def launch(mazes_path: Path, host: str='127.0.0.1', port: int=6574):
    """
    Launch the Micromouse Maze Simulator interface.
    """
    run(host, port, Path(mazes_path))
