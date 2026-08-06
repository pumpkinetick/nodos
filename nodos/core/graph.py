import networkx as nx

from nodos.core.hex_math import Hex
from nodos.world.zones import City

from nodos.config import HEX_DIRECTIONS


class InfrastructureGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.road_edges: list[tuple[Hex, Hex]] = list()

    def build_regional_network(self,
                               tiles: dict,
                               cities: list[City]
                               ):
        nav_graph = nx.Graph()

        for hex_obj, hex_tile in tiles.items():
            if not hex_tile.is_buildable:
                continue

            nav_graph.add_node(hex_obj)

            for dq, dr in HEX_DIRECTIONS:
                neighbor = Hex(q=hex_obj.q + dq, r=hex_obj.r + dr)
                if neighbor in tiles and tiles[neighbor].is_buildable:
                    nav_graph.add_edge(
                        u_of_edge=hex_obj,
                        v_of_edge=neighbor,
                        weight=abs(hex_tile.elevation - tiles[neighbor].elevation)
                    )

        for city_a in cities:
            others = sorted(
                [c for c in cities if c != city_a],
                key=lambda c: city_a.center.distance_to(other=c.center)
            )

            for city_b in others[:2]:
                try:
                    path = nx.astar_path(
                        G=nav_graph,
                        source=city_a.center,
                        target=city_b.center,
                        heuristic=lambda a, b: a.distance_to(other=b),
                        weight='weight'
                    )

                    for p1, p2 in zip(path[:-1], path[1:]):
                        if (p1, p2) not in self.road_edges and (p2, p1) not in self.road_edges:
                            self.road_edges.append((p1, p2))
                            self.graph.add_edge(u_of_edge=p1, v_of_edge=p2)

                except nx.NetworkXNoPath:
                    continue
