from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from nodos.core.hex_math import HexObject

from nodos.config import (
    BUILD_DISTRICT_COST,
    CHANGE_DISTRICT_COST,
    DEMOLISH_REFUND,
    HEX_DIRECTIONS,
    ZONE_COLORS
)

if TYPE_CHECKING:
    from nodos.simulation import SimulationEngine
    from nodos.world.cities import City

logger = logging.getLogger(__name__)


class CityActions:
    def __init__(self, engine: SimulationEngine):
        self.engine = engine

    def build_district(self,
                       city: City,
                       hex_obj: HexObject,
                       zone_type: str
                       ) -> bool:
        if zone_type not in ZONE_COLORS or zone_type == 'center':
            logger.warning('Invalid zone type for new district: %s', zone_type)
            return False

        tile = self.engine.world.tiles.get(hex_obj)
        if tile is None:
            logger.debug('Tile at %s does not exist', hex_obj)
            return False
        if not tile.is_buildable:
            logger.debug('Tile at %s is not buildable', hex_obj)
            return False
        if tile.city_id is not None:
            logger.debug('Tile at %s is already claimed by city %s',
                         hex_obj, tile.city_id)
            return False

        # Adjacency check
        has_adjacent = False
        for dq, dr in HEX_DIRECTIONS:
            neighbor = HexObject(q=hex_obj.q + dq, r=hex_obj.r + dr)
            if neighbor in city.districts:
                has_adjacent = True
                break
        if not has_adjacent:
            logger.debug('Tile at %s is not adjacent to any district of city %s',
                         hex_obj, city.id_num)
            return False

        state = self.engine.get_city_state(city_id=city.id_num)
        if state is None:
            return False

        resources = float(state.get('resources', 0.0))
        if resources < BUILD_DISTRICT_COST:
            logger.debug('City %s has insufficient resources to build district (%f < %f)',
                         city.id_num, resources, BUILD_DISTRICT_COST)
            return False

        # Apply action
        state['resources'] = resources - BUILD_DISTRICT_COST
        tile.city_id = city.id_num
        tile.zone_type = zone_type
        tile.zone_color = ZONE_COLORS[zone_type]
        city.districts[hex_obj] = zone_type

        # Trigger hooks
        for fn in list(self.engine.hooks.get('district_added', list())):
            try:
                fn(self.engine, city.id_num, hex_obj)
            except Exception:
                logger.exception('Error in district_added hook')

        logger.info('City %s built %s district at %s', city.name, zone_type, hex_obj)
        return True

    def change_district_type(self,
                             city: City,
                             hex_obj: HexObject,
                             new_zone_type: str
                             ) -> bool:
        if new_zone_type not in ZONE_COLORS or new_zone_type == 'center':
            logger.warning('Invalid zone type to change to: %s', new_zone_type)
            return False

        if hex_obj not in city.districts:
            logger.debug('Hex %s is not a district of city %s', hex_obj, city.id_num)
            return False

        current_zone = city.districts[hex_obj]
        if current_zone == 'center':
            logger.warning('Cannot change the zone type of the city center')
            return False
        if current_zone == new_zone_type:
            logger.debug('District at %s is already of type %s', hex_obj, new_zone_type)
            return False

        state = self.engine.get_city_state(city.id_num)
        if state is None:
            return False

        resources = float(state.get('resources', 0.0))
        if resources < CHANGE_DISTRICT_COST:
            logger.debug('City %s has insufficient resources to change district type (%f < %f)',
                         city.id_num, resources, CHANGE_DISTRICT_COST)
            return False

        # Apply action
        state['resources'] = resources - CHANGE_DISTRICT_COST
        tile = self.engine.world.tiles.get(hex_obj)
        if tile:
            tile.zone_type = new_zone_type
            tile.zone_color = ZONE_COLORS[new_zone_type]
        city.districts[hex_obj] = new_zone_type

        # Trigger hooks
        for fn in list(self.engine.hooks.get('district_changed', list())):
            try:
                fn(self.engine, city.id_num, hex_obj)
            except Exception:
                logger.exception('Error in district_changed hook')

        logger.info('City %s changed district at %s from %s to %s',
                    city.name, hex_obj, current_zone, new_zone_type)
        return True

    def demolish_district(self, city: City, hex_obj: HexObject) -> bool:
        if hex_obj not in city.districts:
            logger.debug('Hex %s is not a district of city %s', hex_obj, city.id_num)
            return False

        if city.districts[hex_obj] == 'center':
            logger.warning('Cannot demolish the city center')
            return False

        # Connectivity check to make sure the remaining city is connected
        remaining = set(city.districts.keys()) - {hex_obj}
        visited = set()
        frontier = [city.center]
        visited.add(city.center)
        while frontier:
            curr = frontier.pop()
            for dq, dr in HEX_DIRECTIONS:
                neighbor = HexObject(q=curr.q + dq, r=curr.r + dr)
                if neighbor in remaining and neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append(neighbor)

        if len(visited) != len(remaining):
            logger.debug('Cannot demolish district at %s as it would disconnect the city',
                         hex_obj)
            return False

        state = self.engine.get_city_state(city.id_num)
        if state is None:
            return False

        # Apply refund
        resources = float(state.get('resources', 0.0))
        state['resources'] = resources + DEMOLISH_REFUND

        tile = self.engine.world.tiles.get(hex_obj)
        if tile:
            tile.city_id = None
            tile.zone_type = None
            tile.zone_color = None
        city.districts.pop(hex_obj)

        # Trigger hooks
        for fn in list(self.engine.hooks.get('district_removed', list())):
            try:
                fn(self.engine, city.id_num, hex_obj)
            except Exception:
                logger.exception('Error in district_removed hook')

        logger.info('City %s demolished district at %s', city.name, hex_obj)
        return True

    def reproduce(self, city: City) -> bool:
        state = self.engine.get_city_state(city.id_num)
        if state is None:
            return False

        return self.engine.reproduction.try_reproduce(city=city, state=state)
