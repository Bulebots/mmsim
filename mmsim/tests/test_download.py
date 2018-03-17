from pathlib import Path
from tarfile import TarInfo
from tempfile import TemporaryDirectory

import pytest

from mmsim.download import download_micromouseonline_mazes
from mmsim.download import select_tar_members


@pytest.mark.parametrize('parent,new_path,expected', [
    (Path('foo'), Path('a/b/c'), ['a/b/c/bar0', 'a/b/c/bar1']),
    (Path('asdf/qwer'), Path('xxx'), ['xxx/foo0.xyz', 'xxx/foo1.xyz']),
])
def test_select_tar_members(parent, new_path, expected):
    """
    Test `select_tar_members()` function.
    """
    members = [TarInfo('toplevel'),
               TarInfo('toplevel/README.rst'),
               TarInfo('toplevel/foo/bar0'),
               TarInfo('toplevel/foo/bar1'),
               TarInfo('toplevel/asdf/qwer/foo0.xyz'),
               TarInfo('toplevel/asdf/qwer/foo1.xyz')]
    result = select_tar_members(members, parent=parent, new_path=new_path)
    assert [x.name for x in result] == expected


def test_download_micromouseonline_mazes():
    """
    Test `download_micromouseonline_mazes()` function.
    """
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        download_micromouseonline_mazes(tmpdir)
        assert (tmpdir / '16x16').is_dir()
        assert (tmpdir / '16x16' / 'japan-2011-qualifier.txt').is_file()
