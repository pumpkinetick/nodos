import opensimplex


class TerrainGenerator:
    BIOMES = {
        'deep_water': ((25, 60, 110), False),
        'shallow_water': ((45, 105, 175), False),
        'plains': ((110, 160, 80), True),
        'forest': ((60, 130, 75), True),
        'hills': ((130, 150, 100), True),
        'mountains': ((110, 110, 110), False),
        'snow': ((220, 225, 230), False)
    }

    def __init__(self,
                 seed: int = 42,
                 scale: float = 1,
                 octaves: int = 3,
                 persistence: float = 0.5,
                 lacunarity: float = 2.0
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

    def get_biome_data(self,
                       elevation: float
                       ) -> tuple[str, tuple]:
        if elevation < -0.25: return 'deep_water', self.BIOMES['deep_water']
        if elevation < -0.05: return 'shallow_water', self.BIOMES['shallow_water']
        if elevation < 0.25:  return 'plains', self.BIOMES['plains']
        if elevation < 0.50:  return 'forest', self.BIOMES['forest']
        if elevation < 0.70:  return 'hills', self.BIOMES['hills']
        if elevation < 0.85:  return 'mountains', self.BIOMES['mountains']
        return 'snow', self.BIOMES['snow']
