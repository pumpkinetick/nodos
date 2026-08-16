from __future__ import annotations

import networkx as nx
from typing import TYPE_CHECKING, Optional

from nodos.core.hex_math import HexObject

from nodos.config import (
    ELEVATION_FACTOR,
    HEX_DIRECTIONS,
    NUM_NEIGHBORS
)

if TYPE_CHECKING:
    from nodos.world.cities import City


class RoadNetwork:
    def __init__(self):
        self.nav_graph: Optional[nx.Graph] = None

        self.graph = nx.Graph()

        self.road_edges: list[tuple[HexObject, HexObject]] = list()
        self.city_edge_map: dict[HexObject, set[tuple[HexObject, HexObject]]] = dict()

    def _build_nav_graph(self, tiles: dict):
        self.nav_graph = nx.Graph()

        for hex_obj, hex_tile in tiles.items():
            if not hex_tile.is_buildable:
                continue

            self.nav_graph.add_node(node_for_adding=hex_obj)

            for dq, dr in HEX_DIRECTIONS:
                neighbor = HexObject(q=hex_obj.q + dq, r=hex_obj.r + dr)
                if neighbor in tiles and tiles[neighbor].is_buildable:
                    elevation_diff = abs(hex_tile.elevation - tiles[neighbor].elevation)
                    self.nav_graph.add_edge(
                        u_of_edge=hex_obj,
                        v_of_edge=neighbor,
                        weight=elevation_diff ** ELEVATION_FACTOR
                    )

    def build_regional_network(self,
                               tiles: dict,
                               cities: list[City]
                               ):
        self.graph.clear()
        self.road_edges.clear()
        self.city_edge_map.clear()

        self._build_nav_graph(tiles=tiles)

        for city_a in cities:
            others_sorted = sorted(
                [c for c in cities if c != city_a],
                key=lambda c: city_a.center.distance_to(other=c.center)
            )

            for city_b in others_sorted[:NUM_NEIGHBORS]:
                self.connect_cities(
                    city_a_center=city_a.center,
                    city_b_center=city_b.center,
                    tiles=tiles
                )

    def remove_city_connections(self,
                                center: HexObject
                                ):
        owned_edges = self.city_edge_map.pop(center, set())
        if not owned_edges:
            return
        owned_set = set(owned_edges)

        remaining_edges: list[tuple[HexObject, HexObject]] = list()
        for e in self.road_edges:
            if e in owned_set or (e[1], e[0]) in owned_set:
                continue
            remaining_edges.append(e)
        self.road_edges = remaining_edges

        for (a, b) in list(owned_edges):
            if self.graph.has_edge(a, b):
                self.graph.remove_edge(a, b)

        for city_center, edge_set in list(self.city_edge_map.items()):
            edge_set.difference_update(owned_edges)
            if not edge_set:
                self.city_edge_map[city_center] = set()

        for node in list(self.graph.nodes()):
            if self.graph.degree(node) == 0:
                self.graph.remove_node(node)

    def connect_cities(self,
                       city_a_center: HexObject,
                       city_b_center: HexObject,
                       tiles: dict
                       ) -> bool:
        if self.nav_graph is None:
            self._build_nav_graph(tiles=tiles)

        try:
            path = nx.astar_path(
                G=self.nav_graph,
                source=city_a_center,
                target=city_b_center,
                heuristic=lambda a, b: a.distance_to(other=b),
                weight='weight'
            )

            self.city_edge_map.setdefault(city_a_center, set())
            self.city_edge_map.setdefault(city_b_center, set())

            for p1, p2 in zip(path[:-1], path[1:]):
                edge = (p1, p2)
                if not self.graph.has_edge(p1, p2):
                    self.road_edges.append(edge)
                    self.graph.add_edge(u_of_edge=p1, v_of_edge=p2)

                self.city_edge_map[city_a_center].add(edge)
                self.city_edge_map[city_b_center].add(edge)

            return True

        except nx.NetworkXNoPath:
            return False
