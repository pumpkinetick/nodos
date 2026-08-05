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
NOISE_SCALE = 0.1
NOISE_OCTAVES = 3
NOISE_PERSISTENCE = 0.5
NOISE_LACUNARITY = 2.0

# --- Biome Definitions ---
# Format: (Upper Elevation Threshold, (R, G, B, A) Color, Is_Buildable, Name)
BIOMES = [
    (-0.25, (25, 60, 110, 255), False, 'deep_water'),
    (-0.05, (45, 105, 175, 255), False, 'shallow_water'),
    (0.25, (110, 160, 80, 255), True, 'plains'),
    (0.50, (60, 130, 75, 255), True, 'forest'),
    (0.70, (130, 150, 100, 255), True, 'hills'),
    (0.85, (110, 110, 110, 255), False, 'mountains'),
    (float('inf'), (220, 225, 230, 255), False, 'snow')
]
