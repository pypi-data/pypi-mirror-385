import ctypes
import pathlib
import sys
import os

from .ddnet_maploader import _MapDataInternal

so_path = None

path_candidates = [
    "/usr/local/lib/libddnet_map_loader.so",
    "/usr/lib/libddnet_map_loader.so",
    "/lib/libddnet_map_loader.so",
    "libddnet_map_loader.so"
]

if os.name == 'nt':
    path_candidates.append('libddnet_map_loader.dll')
    path_candidates.append('ddnet_map_loader.dll')

for so_path_candidate in path_candidates:
    if pathlib.Path(so_path_candidate).is_file():
        so_path = so_path_candidate
        break

if not so_path:
    print("Missing libddnet_map_loader library!", file=sys.stderr)
    print("Get it from https://github.com/Teero888/ddnet_maploader_c99", file=sys.stderr)
    raise ValueError("missing libddnet_map_loader")

_lib_map_loader = ctypes.cdll.LoadLibrary(so_path)
load_map = _lib_map_loader.load_map
load_map.argtypes = [ctypes.c_char_p]
load_map.restype = _MapDataInternal

_free_map_data = _lib_map_loader.free_map_data
_free_map_data.argtypes = [ctypes.c_void_p]
_free_map_data.restype = None
