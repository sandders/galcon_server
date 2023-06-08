from in_game_objects.planet import Planet, PlanetSize
from utils import Coordinate
import unittest


class Test_case_Planet(unittest.TestCase):

    def setUp(self):
        self.coords=Coordinate(5,10)
        self.planetlanet_size=PlanetSize.SMALL
        self.owner="owner"
        self.planet=Planet(self.coords,self.planetlanet_size,self.owner,self.planetlanet_size.value*50)

    def test_right_init(self):
        self.assertEqual(self.planet.coords,self.coords,"wrong coord init")
        self.assertEqual(self.planet.size,self.planetlanet_size,"wrong type init")
        self.assertEqual(self.planet.units_count,self.planetlanet_size.value*50,"wrong count of units init")
        self.assertEqual(self.planet.owner,self.owner,"wrong owner init")

    def test_get_dict(self):
        self.assertEqual(self.planet.get_dict(), {'size': self.planetlanet_size, 'units_count': self.planetlanet_size.value*50, 'owner': self.owner,'coords': self.coords.get_dict(), 'id': self.planet._Planet__id}, "wrong dictionary")



if __name__ == '__main__':
    unittest.main()
