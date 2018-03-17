from pathlib import Path

import click

from .ui import run
from .download import download_micromouseonline_mazes


@click.command()
@click.argument('mazes_path', type=click.Path(), default=Path.home()/'.mmsim')
@click.option('-h', '--host', type=str, default='127.0.0.1',
              help='Listen on IP (default: 127.0.0.1).')
@click.option('-p', '--port', type=int, default=6574,
              help='Listen on port (default: 6574).')
def launch(mazes_path: Path, host: str='127.0.0.1', port: int=6574):
    """
    Launch the Micromouse Maze Simulator interface.
    """
    mazes_path = Path(mazes_path)
    if not mazes_path.exists():
        download_micromouseonline_mazes(mazes_path)
    run(host, port, Path(mazes_path))
