import random
from enum import IntEnum

from utils import Coordinate, ID_GENERATOR


class PlanetSize(IntEnum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3


class Planet(object):
    cache  = {}

    def __init__(self, coords: Coordinate, planet_size: PlanetSize, owner: int = None, units_count: int = None):
        self.coords = coords
        self.size = planet_size

        if units_count is None:
            units_count = random.randint(0, 40) * planet_size.value
        self.units_count = units_count

        self.owner = owner
        self.__id = next(ID_GENERATOR)

        self.cache[self.__id] = self

    def get_dict(self) -> dict:
        return {
            'size': self.size,
            'owner': self.owner,
            'units_count': self.units_count,
            'coords': self.coords.get_dict(),
            'id': self.__id,
        }
