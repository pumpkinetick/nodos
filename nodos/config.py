HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
]
POINTY_TOP_DIRECTIONS = [
    (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)
]

############################
# --- Display Settings --- #
############################

# Window settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
WINDOW_TITLE = 'Nodos'

# Hex layout settings
HEX_SIZE = 32.0
ORIGIN_X = 0.0
ORIGIN_Y = 0.0

###############################
# --- Simulation Settings --- #
###############################

# Map settings
MAP_WIDTH = 100
MAP_HEIGHT = 100

# Terrain generation settings
NOISE_SEED = 42
NOISE_SCALE = 1.0 / 30
NOISE_OCTAVES = 5
NOISE_PERSISTENCE = 1.0 / 2
NOISE_LACUNARITY = 2.0

BIOMES = [
    (-0.3, (25, 60, 110, 255), False, 'deep_water'),
    (-0.2, (45, 105, 175, 255), False, 'shallow_water'),
    (-0.15, (230, 200, 120, 255), True, 'shore'),
    (0.1, (110, 160, 80, 255), True, 'plains'),
    (0.3, (60, 130, 75, 255), True, 'forest'),
    (0.4, (130, 150, 100, 255), True, 'hills'),
    (0.5, (110, 110, 110, 255), False, 'mountains'),
    (float('inf'), (220, 225, 230, 255), False, 'snow')
] # Format: (Upper Elevation Threshold, (R, G, B, A) Color, Is_Buildable, Name)

# Road graph settings
ELEVATION_FACTOR = 2.0

# City settings
INIT_NUM_CITIES = 3
MIN_INIT_CITY_DISTANCE = 20

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

DEFAULT_POPULATION = 100.0
DEFAULT_HAPPINESS = 0.1
DEFAULT_RESOURCES = 100.0
DEFAULT_DEVELOPMENT = 0.1

NEAT_MUTATION_RATE_WEIGHT = 0.5
NEAT_MUTATION_RATE_NODE = 0.05
NEAT_MUTATION_RATE_CONN = 0.05
NEAT_MUTATION_RATE_TOGGLE = 0.05
NEAT_MUTATION_SCALE = 0.5

DEFAULT_REPRODUCTION_COOLDOWN = 8
REPRODUCTION_THRESHOLD = 100.0
REPRODUCTION_POPULATION_COST = 10.0
REPRODUCTION_RESOURCE_COST = 10.0

MIN_CHILD_CITY_DISTANCE = 10
MAX_CHILD_CITY_DISTANCE = 20

DEATH_POPULATION_THRESHOLD = 1

# --- District-to-Metric Correlation Parameters ---
BASE_POP_CAP = 10.0
RES_POP_CAP_BOOST = 10.0

BASE_HAPPINESS = 0.01
COM_HAPPY_BOOST = 0.01
IND_HAPPY_PENALTY = 0.01

BASE_DEVELOPMENT = 0.0
IND_DEV_BOOST = 0.001
COM_DEV_BOOST = 0.001

# Dynamic Resource Rates
IND_RES_PROD = 0.01
COM_RES_PROD = 0.01 # Generated per citizen
POP_CONSUMPTION_RATE = 0.1 # Consumed per citizen

HAPPY_POP_GROWTH_BASE = 10.0
DEV_RES_GROWTH_BASE = 10.0

# --- Action Costs ---
BUILD_DISTRICT_COST = 10.0
CHANGE_DISTRICT_COST = 1.0
DEMOLISH_REFUND = 1.0
