from ..render_info import FPS


FLOOR = {
    "brick floor",
    "copper brick floor",
    "copper door",
    "copper door open",
    "copper pit",
    "dirt",
    "ice",
    "log floor",
    "moist dirt",
    "mushroom door",
    "mushroom door open",
    "mushroom floor",
    "pebble",
    "slime door",
    "slime door open",
    "slime floor",
    "stone brick floor",
    "stone floor",
    "void",
    "water",
    "wood door",
    "wood door open",
    "wood floor",
}
FLOOR_TYPE = {
    "copper pit": "fluid",
    "ice": "block",
    "void": "block",
    "water": "fluid",
}
SOIL_STRENGTH = {
    "dirt": 1,
    "moist dirt": 1.25,
}
GROW_TIME = {
    "bluebell": 400,
    "carrot": 160,
    "copper pit": 600,
    "water": 60,
    "potato": 240,
    "rabbit child": 200,
    "sapling": 80,
    "spore": 120,
    "treeling": 100,
}
GROW_TILES = {
    "bluebell": {"kind": "bluebell grown", "inventory": {"bluebell": 2}},
    "carrot": {"kind": "carrot grown", "inventory": {"carrot": 2}},
    "copper pit": {"kind": "copper pit grown", "inventory": {"copper ingot": 1}},
    "water": {"floor": "ice"},
    "potato": {"kind": "potato grown", "inventory": {"potato": 2}},
    "rabbit child": {
        "kind": "rabbit adult",
        "inventory": {"rabbit fur": 1, "rabbit meat": 1},
    },
    "sapling": {"kind": "treeling", "inventory": {"sapling": 1, "log": 1}},
    "spore": {"kind": "mushroom", "inventory": {"spore": 2}},
    "treeling": {"kind": "tree", "inventory": {"sapling": 2, "log": 2}},
}
GROW_REQUIREMENT = {
    "bluebell": 1.25
}
MULTI_TILES = {
    "furnace": (2, 2),
    "manual press": (2, 1),
    "masonry bench": (2, 1),
    "obelisk": (1, 2),
    "sawbench": (2, 1),
    "sewbench": (2, 1),
    "wooden bed": (1, 2),
}
PROCESSING_TIME = {
    "composter": 2 * FPS,
    "furnace": 10 * FPS,
    "void convertor": 20 * FPS,
    "wood crucible": 300 * FPS,
    "wooden sieve": 15 * FPS,
}
STORAGE = {
    "small barrel": (1, 512),
    "small crate": (8, 64),
    "void crate": (8, 64),
}
UNBREAK = {
    "copper pit",
    "glass lock",
    "left",
    "obelisk",
    "player",
    "up",
    "void",
    "void convertor",
    "void crate",
}
