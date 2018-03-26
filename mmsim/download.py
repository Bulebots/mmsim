import os
import tarfile
from pathlib import Path
from urllib.request import urlretrieve

from .typing import TarMembers


def clean_tar_members(members: TarMembers) -> TarMembers:
    """
    Strip .tar components (i.e.: remove top-level directory) from members.

    Parameters
    ----------
    members
        A list of .tar members.

    Returns
    -------
        A clean .tar member list with the stripped components.
    """
    clean = []
    for member in members:
        path = Path(member.name)
        member.name = path.relative_to(path.parts[0])
        clean.append(member)
    return clean


def download_micromouseonline_mazes(download_path: Path):
    """
    Download Micromouseonline mazes.

    Parameters
    ----------
    download_path
        Where to download the maze files to.
    """
    url = 'https://github.com/micromouseonline/mazefiles/'\
        'archive/master.tar.gz'
    reveal_tar, headers = urlretrieve(url)
    with tarfile.open(reveal_tar) as tar:
        members = clean_tar_members(tar.getmembers())
        tar.extractall(str(download_path), members)
    os.remove(reveal_tar)
