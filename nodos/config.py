HEX_DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

# --- Window & Display ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
WINDOW_TITLE = 'Nodos'

# --- Hex Layout ---
HEX_SIZE = 32.0
ORIGIN_X = 0.0
ORIGIN_Y = 0.0
MAP_WIDTH = 160
MAP_HEIGHT = 90

# --- Terrain Noise Generation ---
NOISE_SEED = 42
NOISE_SCALE = 0.05
NOISE_OCTAVES = 3
NOISE_PERSISTENCE = 0.5
NOISE_LACUNARITY = 2.0

# --- Biome Definitions ---
# Format: (Upper Elevation Threshold, (R, G, B, A) Color, Is_Buildable, Name)
BIOMES = [
    (-0.3, (25, 60, 110, 255), False, 'deep_water'),
    (-0.2, (45, 105, 175, 255), False, 'shallow_water'),
    (-0.1, (230, 200, 120, 255), True, 'shore'),
    (0.1, (110, 160, 80, 255), True, 'plains'),
    (0.3, (60, 130, 75, 255), True, 'forest'),
    (0.4, (130, 150, 100, 255), True, 'hills'),
    (0.5, (110, 110, 110, 255), False, 'mountains'),
    (float('inf'), (220, 225, 230, 255), False, 'snow')
]

# --- Districts & Zoning ---
NUM_CITIES = 6
CITY_EXPANSION_STEPS = 10
ZONE_TYPES = ['residential', 'industrial', 'commercial']
ZONE_COLORS = {
    'center': (255, 255, 255, 255),
    'residential': (220, 180, 50, 255),
    'industrial': (70, 130, 200, 255),
    'commercial': (210, 80, 80, 255)
}
