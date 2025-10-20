import ctypes

from . import cbindings

class GameLayer(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_ubyte)),
        ("flags", ctypes.POINTER(ctypes.c_ubyte)),
    ]

class TeleLayer(ctypes.Structure):
    _fields_ = [
        ("number", ctypes.POINTER(ctypes.c_ubyte)),
        ("type", ctypes.POINTER(ctypes.c_ubyte)),
    ]

class SpeedupLayer(ctypes.Structure):
    _fields_ = [
        ("force", ctypes.POINTER(ctypes.c_ubyte)),
        ("max_speed", ctypes.POINTER(ctypes.c_ubyte)),
        ("type", ctypes.POINTER(ctypes.c_ubyte)),
        ("angle", ctypes.POINTER(ctypes.c_short)),
    ]

class SwitchLayer(ctypes.Structure):
    _fields_ = [
        ("number", ctypes.POINTER(ctypes.c_ubyte)),
        ("type", ctypes.POINTER(ctypes.c_ubyte)),
        ("flags", ctypes.POINTER(ctypes.c_ubyte)),
        ("delay", ctypes.POINTER(ctypes.c_ubyte)),
    ]

class DoorLayer(ctypes.Structure):
    _fields_ = [
        ("index", ctypes.POINTER(ctypes.c_ubyte)),
        ("flags", ctypes.POINTER(ctypes.c_ubyte)),
        ("number", ctypes.POINTER(ctypes.c_int)),
    ]

class TuneLayer(ctypes.Structure):
    _fields_ = [
        ("number", ctypes.POINTER(ctypes.c_ubyte)),
        ("type", ctypes.POINTER(ctypes.c_ubyte)),
    ]

class _MapDataInternal(ctypes.Structure):
    _fields_ = [
        ("game_layer", GameLayer),
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("front_layer", GameLayer),
        ("tele_layer", TeleLayer),
        ("speedup_layer", SpeedupLayer),
        ("switch_layer", SwitchLayer),
        ("door_layer", DoorLayer),
        ("tune_layer", TuneLayer),
        ("num_settings", ctypes.c_int),
        ("settings", ctypes.POINTER(ctypes.c_char_p)),
        ("_map_file_data", ctypes.c_void_p),
        ("_map_file_size", ctypes.c_size_t),
    ]

class MapData:
    game_layer: GameLayer
    width: int
    height: int
    front_layer: GameLayer
    tele_layer: TeleLayer
    speedup_layer: SpeedupLayer
    switch_layer: SwitchLayer
    door_layer: DoorLayer
    tune_layer: TuneLayer
    settings: list[str]

    _internal_data: _MapDataInternal

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._internal_data:
            cbindings._free_map_data(ctypes.byref(self._internal_data))
