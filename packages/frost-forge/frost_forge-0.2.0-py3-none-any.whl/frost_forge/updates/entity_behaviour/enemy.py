from .entity_movement import move_entity


def enemy(
    chunks, chunk, tile, current_tile, location, health, player_distance, create_tile
):
    if player_distance == 1:
        health -= 1
    elif player_distance < 73:
        chunks, create_tile = move_entity(chunks, chunk, tile, current_tile, 1, location, create_tile)
    else:
        chunks, create_tile = move_entity(chunks, chunk, tile, current_tile, 0, location, create_tile)
    return chunks, health, create_tile
