from abc import ABC, abstractmethod

from nodos.world.map import WorldMap


class RenderLayer(ABC):
    @abstractmethod
    def build(self, world_map: WorldMap):
        pass

    @abstractmethod
    def draw(self):
        pass
