from . __version__ import __version__

from typing import Optional
from . import cbindings, ddnet_maploader

def load_map(map_name: str) -> ddnet_maploader.MapData:
    raw_data = cbindings.load_map(map_name.encode(encoding='utf-8'))
    if not raw_data.game_layer.data:
        raise ValueError("failed to load map")

    map_data = ddnet_maploader.MapData()
    map_data._internal_data = raw_data
    map_data.game_layer = raw_data.game_layer
    map_data.width = raw_data.width
    map_data.height = raw_data.height
    map_data.front_layer = raw_data.front_layer
    map_data.tele_layer = raw_data.tele_layer
    map_data.speedup_layer = raw_data.speedup_layer
    map_data.switch_layer = raw_data.switch_layer
    map_data.door_layer = raw_data.door_layer
    map_data.tune_layer = raw_data.tune_layer
    map_data.settings = []
    for i in range(0, raw_data.num_settings - 1):
        map_data.settings.append(raw_data.settings[i].decode("utf-8"))
    return map_data
