from pathlib import Path

import click

from .ui import run


@click.command()
@click.argument('maze_file')
@click.option('-h', '--host', type=str, default='127.0.0.1',
              help='Listen on IP (default: 127.0.0.1).')
@click.option('-p', '--port', type=int, default=6574,
              help='Listen on port (default: 6574).')
def launch(maze_file: Path, host: str='127.0.0.1', port: int=6574):
    """
    Launch the Micromouse Maze Simulator interface.
    """
    run(host, port, maze_file)
