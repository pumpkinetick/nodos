import opensimplex

from nodos.config import (
    NOISE_SEED, NOISE_SCALE, NOISE_OCTAVES, NOISE_PERSISTENCE, NOISE_LACUNARITY,
    BIOMES
)


class TerrainGenerator:
    def __init__(self,
                 seed: int = NOISE_SEED,
                 scale: float = NOISE_SCALE,
                 octaves: int = NOISE_OCTAVES,
                 persistence: float = NOISE_PERSISTENCE,
                 lacunarity: float = NOISE_LACUNARITY
                 ):
        self.noise = opensimplex.OpenSimplex(seed=seed)
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

    def get_elevation(self,
                      q: int,
                      r: int
                      ) -> float:
        amplitude = 1.0
        frequency = 1.0
        total_value = 0.0
        max_value = 0.0

        for _ in range(self.octaves):
            sample_x = q * self.scale * frequency
            sample_y = r * self.scale * frequency

            total_value += self.noise.noise2(x=sample_x, y=sample_y) * amplitude
            max_value += amplitude

            amplitude *= self.persistence
            frequency *= self.lacunarity

        return total_value / max_value

    @staticmethod
    def get_biome_data(elevation: float) -> tuple[str, tuple[int, int, int, int], bool]:
        for threshold, color, is_buildable, name in BIOMES:
            if elevation < threshold:
                return name, color, is_buildable

        return BIOMES[-1][3], BIOMES[-1][1], BIOMES[-1][2]
