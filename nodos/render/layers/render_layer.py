from abc import ABC, abstractmethod


class RenderLayer(ABC):
    @abstractmethod
    def build(self,
              world_map
              ):
        pass

    @abstractmethod
    def draw(self):
        pass
