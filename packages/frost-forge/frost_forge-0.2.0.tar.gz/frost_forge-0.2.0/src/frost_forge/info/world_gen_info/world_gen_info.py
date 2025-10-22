WORLD_TYPES = ("default", "skyblock", "large biomes", "no structures")
NOISE_TILES = {
    "plains": (
        ((-0.5, -0.25), (0, 0.5), {"floor": "ice"}),
        ((-0.5, -0.2), (-0.15, 0), {"kind": "flint"}),
        ((-0.2, 0.1), (-0.5, -0.35), {"kind": "rock"}),
        ((-0.1, 0.1), (0.45, 0.5), {"kind": "mushroom", "inventory": {"spore": 2}, "floor": "dirt"},),
        ((-0.15, 0.15), (0.4, 0.5), {"kind": "spore", "floor": "dirt"}),
        ((0.3, 0.5), (0.2, 0.3), {"kind": "tree", "inventory": {"log": 2, "sapling": 2}, "floor": "dirt"},),
        ((0.25, 0.5), (0.15, 0.35), {"kind": "treeling", "inventory": {"log": 1, "sapling": 1}, "floor": "dirt",},),
        ((0.15, 0.5), (0.1, 0.4), {"kind": "sapling", "floor": "dirt"}),
        ((-0.01, 0), (0.27, 0.28), {"kind": "rabbit adult", "floor": "dirt", "inventory": {"rabbit meat": 1, "rabbit fur": 1},},),
        ((-0.05, 0), (0.25, 0.3), {"kind": "carrot", "floor": "dirt"}),
        ((-0.25, -0.15), (0.2, 0.3), {"kind": "clay"}),
        ((0.05, 0.1), (0.35, 0.4), {"kind": "bluebell", "floor": "dirt"}),
    ),
    "lake": (
        ((0, 0.1), (0.3, 0.5), {"kind": "clay"}),
        ((-0.5, 0), (-0.1, 0.5), {"floor": "ice"}),
        ((-0.5, -0.1), (-0.25, -0.1), {"kind": "flint"}),
    ),
    "forest": (
        ((0, 0.1), (0.3, 0.35), {"kind": "bluebell", "floor": "dirt"}),
        ((-0.1, 0.1), (0.45, 0.5), {"kind": "mushroom", "inventory": {"spore": 2}, "floor": "dirt"},
        ),
        ((-0.25, 0.25), (0.4, 0.5), {"kind": "spore", "floor": "dirt"}),
        ((0.25, 0.5), (0, 0.3), {"kind": "tree", "inventory": {"log": 2, "sapling": 2}, "floor": "dirt"},),
        ((0.2, 0.5), (-0.05, 0.35), {"kind": "treeling", "inventory": {"log": 1, "sapling": 1}, "floor": "dirt",},),
        ((0.1, 0.5), (-0.1, 0.4), {"kind": "sapling", "floor": "dirt"}),
        ((0, 0.05), (0.2, 0.25), {"kind": "potato", "floor": "dirt"}),
        ((0, 0.5), (0, 0.5), {"floor": "dirt"}),
    ),
    "mountain": (
        ((0.3, 0.4), (0.1, 0.2), {"kind": "coal ore", "inventory": {"coal": 1}, "floor": "pebble"},),
        ((0.4, 0.5), (0, 0.1), {"kind": "copper ore", "inventory": {"raw copper": 1}, "floor": "pebble"},),
        ((0.1, 0.4), (-0.15, 0.15), {"kind": "stone", "floor": "pebble"}),
        ((0, 0.5), (-0.2, 0.2), {"kind": "rock", "floor": "pebble"}),
        ((-0.1, 0.3), (-0.25, 0.25), {"floor": "pebble"}),
        ((-0.2, -0.19), (-0.3, -0.28), {"kind": "slime", "inventory": {"slime ball": 1}},),
    ),
}
BIOMES = (
    (-0.05, 0.05, "lake"),
    (-0.25, -0.1, "forest"),
    (0.25, 0.5, "mountain"),
)
