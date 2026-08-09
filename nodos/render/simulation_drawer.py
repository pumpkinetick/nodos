from __future__ import annotations

from typing import TYPE_CHECKING

from nodos.render.layers import *

if TYPE_CHECKING:
    from nodos.core.hex_math import HexLayout, HexObject
    from nodos.world.map import WorldMap


class SimulationDrawer:
    def __init__(self, layout: HexLayout):
        self.layout = layout

        self.terrain_layer = TerrainLayer(layout=layout)
        self.zoning_layer = ZoningLayer(layout=layout)
        self.road_layer = RoadLayer(layout=layout)
        self.border_layer = BorderLayer(layout=layout)

    def build_geometry(self, world_map: WorldMap):
        self.terrain_layer.build(world_map=world_map)
        self.zoning_layer.build(world_map=world_map)
        self.road_layer.build(world_map=world_map)
        self.border_layer.build(world_map=world_map)

    def remove_tiles(self,
                     hexes: list[HexObject],
                     world_map: WorldMap
                     ):
        self.terrain_layer.remove_tiles(hexes=hexes)
        self.border_layer.remove_tiles(hexes=hexes)

        for h in hexes:
            tile = world_map.get_tile(hex_obj=h)
            if tile:
                self.zoning_layer.update_tile(hex_obj=h, tile=tile)

    def bake_roads(self, world_map: WorldMap):
        self.road_layer.build(world_map=world_map)

    def draw_layer(self, view_mode: str):
        if view_mode == 'terrain':
            self.terrain_layer.draw()
            self.border_layer.draw()
        elif view_mode == 'zoning':
            self.zoning_layer.draw()

        self.road_layer.draw()
