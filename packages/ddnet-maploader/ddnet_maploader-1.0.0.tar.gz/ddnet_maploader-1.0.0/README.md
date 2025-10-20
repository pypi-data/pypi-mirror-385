# ddnet_maploader_py

Python bindings for https://github.com/Teero888/ddnet_maploader_c99

## dependencies

```
git clone https://github.com/Teero888/ddnet_maploader_c99
cd ddnet_maploader_c99
git checkout 68de38e317ea5fb2ed005479c6046338007d8420
mkdir build && cd build
cmake ..
make install
```

## sample usage

```python
#!/usr/bin/env python3

import ddnet_maploader

with ddnet_maploader.load_map("/home/chiller/.teeworlds/maps/tinycave.map") as map:
    x = 3
    y = 3
    tile = map.game_layer.data[y * map.width + x]
    print(f"at x={x} y={y} tile={tile}")

    for setting in map.settings:
        print(f"map setting: {setting}")
```
