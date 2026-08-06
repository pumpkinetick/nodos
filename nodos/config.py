HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
]
POINTY_TOP_DIRECTIONS = [
    (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)
]

# --- Window & Display ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
WINDOW_TITLE = 'Nodos'

# --- Hex Layout ---
HEX_SIZE = 32.0
ORIGIN_X = 0.0
ORIGIN_Y = 0.0
MAP_WIDTH = 100
MAP_HEIGHT = 100

# --- Terrain Noise Generation ---
NOISE_SEED = 42
NOISE_SCALE = 1.0 / 30
NOISE_OCTAVES = 5
NOISE_PERSISTENCE = 1.0 / 2
NOISE_LACUNARITY = 2.0

# --- Biome Definitions ---
# Format: (Upper Elevation Threshold, (R, G, B, A) Color, Is_Buildable, Name)
BIOMES = [
    (-0.3, (25, 60, 110, 255), False, 'deep_water'),
    (-0.2, (45, 105, 175, 255), False, 'shallow_water'),
    (-0.15, (230, 200, 120, 255), True, 'shore'),
    (0.1, (110, 160, 80, 255), True, 'plains'),
    (0.3, (60, 130, 75, 255), True, 'forest'),
    (0.4, (130, 150, 100, 255), True, 'hills'),
    (0.5, (110, 110, 110, 255), False, 'mountains'),
    (float('inf'), (220, 225, 230, 255), False, 'snow')
]

# --- Cities & Zoning ---
INIT_NUM_CITIES = 10
MIN_CITY_DISTANCE = 20
CITY_EXPANSION_STEPS = 3
NUM_NEIGHBORS = 3
ZONE_COLORS = {
    'center': (255, 255, 255, 255),
    'residential': (70, 130, 200, 255),
    'industrial': (220, 180, 50, 255),
    'commercial': (210, 80, 80, 255)
}
NAME_PREFIXES = ['Oak', 'River', 'Stone', 'Iron', 'Kings', 'Frost', 'Sun', 'Moon', 'Star', 'Wind']
NAME_SUFFIXES = ['ville', 'town', 'ford', 'bridge', 'gate', 'hold', 'port', 'stead', 'val', 'grad']

# --- Default City State Values ---
DEFAULT_POPULATION = 100.0
DEFAULT_RESOURCES = 100.0
DEFAULT_HAPPINESS = 1.0
DEFAULT_GROWTH_RATE = 0.0
