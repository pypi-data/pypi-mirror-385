from ..chunk_update import update_tile
from ...info import GROW_TILES, ATTRIBUTES, FPS
from ..chunk_update.growth import grow


def update_tiles(state, chunks):
    tile_location = state.location["tile"]
    if len(state.inventory) > state.inventory_number:
        inventory_key = list(state.inventory.keys())[state.inventory_number]
    else:
        inventory_key = None
    if state.tick % (FPS * 5) == 0:
        state.update_chunks = {}
        for chunk_dx in range(-3, 4):
            for chunk_dy in range(-3, 4):
                chunk = (chunk_dx + tile_location[0], chunk_dy + tile_location[1])
                state.update_chunks[chunk] = set()
                for tile in chunks[chunk]:
                    updatable = False
                    current_tile = chunks[chunk][tile]
                    if "kind" in current_tile:
                        if current_tile["kind"] in ATTRIBUTES or current_tile["kind"] in GROW_TILES:
                            updatable = True
                    elif current_tile["floor"] in GROW_TILES:
                        updatable = True
                    if updatable:
                        state.update_chunks[chunk].add(tile)
    create_tile = set()
    for chunk in state.update_chunks:
        for tile in state.update_chunks[chunk]:
            if tile in chunks[chunk]:
                current_tile = chunks[chunk][tile]
                if "kind" in current_tile:
                    chunks, state.health, create_tile = update_tile(
                        current_tile,
                        chunks,
                        chunk,
                        tile,
                        state.tick,
                        state.location["tile"],
                        inventory_key,
                        state.health,
                        create_tile,
                    )
                elif current_tile["floor"] in GROW_TILES:
                    chunks[chunk][tile] = grow(current_tile)
                    if chunks[chunk][tile] == {}:
                        del chunks[chunk][tile]
    for location in create_tile:
        if location[0] not in state.update_chunks:
            state.update_chunks[location[0]] = set()
        state.update_chunks[location[0]].add(location[1])
    return chunks
