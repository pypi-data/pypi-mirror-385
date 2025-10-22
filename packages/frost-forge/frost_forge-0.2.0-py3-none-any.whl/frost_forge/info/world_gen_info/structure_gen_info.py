NOISE_STRUCTURES = {
    "forest": (((0, 0.01), "mushroom hut"),),
    "mountain": (((0, 0.01), "mineshaft"),),
    "plains": (((0, 0.005), "copper dungeon"),),
}
ROOM_COLORS = {
    "copper dungeon": {
        (136, 68, 31): {"kind": "copper brick", "floor": "copper brick floor"},
        (181, 102, 60): {"floor": "copper brick floor"},
        (228, 148, 106): {"floor": "copper door"},
        (138, 138, 140): {"kind": "skeleton", "floor": "copper brick floor"},
        (207, 206, 215): {"kind": "stone brick", "floor": "stone brick floor"},
        (247, 247, 255): {"floor": "stone brick floor"},
        (53, 53, 54): {"kind": "furnace", "loot": "copper furnace", "floor": "stone floor", "recipe": 2},
        (83, 107, 120): {"kind": "left", "floor": "stone floor"},
        (104, 130, 140): {"kind": "up", "floor": "stone floor"},
        (123, 104, 150): {"kind": "wooden table", "floor": "wood floor", "loot": "banquet table"},
        (73, 58, 37): {"kind": "wood", "floor": "wood floor"},
        (92, 74, 49): {"kind": "wooden table", "floor": "wood floor", "loot": "bookshelf"},
        (60, 181, 71): {"kind": "small crate", "floor": "wood floor", "loot": "copper treasure"},
    },
    "mineshaft": {
        (53, 53, 54): {"kind": "stone brick", "floor": "stone floor"},
        (138, 138, 140): {"floor": "stone brick floor"},
        (247, 247, 255): {"kind": "rock", "floor": "stone floor"},
        (73, 58, 37): {"kind": "log", "floor": "wood floor"},
        (92, 74, 49): {"kind": "wood", "floor": "wood floor"},
        (129, 107, 63): {"floor": "wood door"},
        (19, 17, 18): {"kind": "coal ore", "inventory": {"coal": 1}, "floor": "stone floor"},
        (123, 104, 150): {"kind": "small crate", "loot": "mine chest", "floor": "stone floor"},
        (60, 181, 71): {"kind": "slime", "inventory": {"slime ball": 1}, "floor": "stone floor"},
    },
    "mushroom hut": {
        (247, 247, 255): {"kind": "mushroom block", "floor": "mushroom floor"},
        (138, 138, 140): {"floor": "mushroom floor"},
        (53, 53, 54): {"floor": "mushroom door"},
        (106, 228, 138): {"kind": "mushroom shaper", "floor": "mushroom floor"},
        (92, 74, 49): {"kind": "small crate", "loot": "mushroom chest", "floor": "mushroom floor"},
    },
}
STRUCTURE_ENTRANCE = {
    "copper dungeon": {"kind": "glass lock", "floor": "copper door"},
    "mineshaft": {"floor": "stone floor"},
    "mushroom hut": {"floor": "mushroom door"},
}
STRUCTURE_SIZE = {"copper dungeon": 0.6, "mushroom hut": 0.1, "mineshaft": 0.4}
STRUCTURE_ROOMS = {
    "copper dungeon": ("treasury", "hallway", "library", "banquet", "forge"),
    "mineshaft": ("hallway", "coal mine"),
    "mushroom hut": ("mushroom hut",),
}
STRUCTURE_HALLWAYS = {
    "copper dungeon": {"floor": "copper brick floor"},
    "mineshaft": {"floor": "stone brick floor"},
    "mushroom hut": {"floor": "mushroom floor"},
}
LOOT_TABLES = {
    "mushroom chest": ((
        (0.7, "mushroom", 2, 7),
        (0.5, "mushroom block", 3, 5),
        (0.35, "spore", 1, 5),
        (0.25, "fertilizer", 1, 2),
        (0.2, "mushroom floor", 2, 3),
        (0.15, "plant bouquet", 1, 3),
        (0.1, "mushroom shaper", 1, 1),
        (0.05, "mushroom door", 1, 2),
        (0.05, "bluebell jar", 1, 2),
        (0.02, "composter", 1, 1),
    ), 2, 5),
    "mine chest": ((
        (0.7, "rock", 2, 4),
        (0.5, "flint", 3, 5),
        (0.35, "coal", 1, 3),
        (0.25, "stone", 2, 4),
        (0.15, "handle", 1, 2),
        (0.1, "life crystal", 1, 1),
        (0.05, "sawbench", 1, 1),
        (0.05, "rock pickaxe", 1, 1),
        (0.05, "rock axe", 1, 1),
        (0.05, "rock sword", 1, 1),
    ), 2, 6),
    "copper furnace": ((
        (0.8, "fuel", 4, 16),
        (0.4, "raw copper", 2, 4),
        (0.1, "copper ingot", 1, 3),
    ), 1, 2),
    "banquet table": ((
        (0.4, "roasted mushroom", 1, 2),
        (0.3, "roasted rabbit meat", 1, 3),
        (0.2, "mushroom stew", 1, 1),
        (0.1, "life crystal", 1, 1),
    ), 0, 1),
    "bookshelf": ((
        (0.4, "paper", 1, 2),
        (0.3, "blueprint", 1, 1),
        (0.2, "thread", 1, 2),
        (0.1, "copper needle", 1, 1),
    ), 0, 1),
    "copper treasure": ((
        (0.6, "raw copper", 1, 2),
        (0.4, "copper ingot", 1, 3),
        (0.3, "slime crystal", 1, 2),
        (0.25, "handle", 1, 2),
        (0.2, "coal", 2, 3),
        (0.1, "furnace", 1, 1),
        (0.05, "copper block", 1, 1),
        (0.05, "copper pickaxe", 1, 1),
        (0.05, "copper axe", 1, 1),
        (0.05, "copper sword", 1, 1),
    ), 2, 5),
    "basic sift": ((
        (0.7, "pebble", 2, 3),
        (0.4, "coal", 1, 2),
        (0.3, "clay", 1, 1),
        (0.05, "raw copper", 1, 1),
    ), 0, 2),
}
ADJACENT_ROOMS = ((0, -1), (0, 1), (-1, 0), (1, 0))
