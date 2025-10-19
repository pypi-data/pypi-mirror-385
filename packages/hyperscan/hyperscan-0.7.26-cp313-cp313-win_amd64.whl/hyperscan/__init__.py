"""""" # start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'hyperscan.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

import typing

from hyperscan._hs_ext import *  # noqa: F403

try:
    from hyperscan._version import __version__  # pyright: ignore
except ImportError:
    __version__ = "unknown"


class ExpressionExt(typing.NamedTuple):
    flags: int
    min_offset: int = 0
    max_offset: int = 0
    min_length: int = 0
    edit_distance: int = 0
    hamming_distance: int = 0
