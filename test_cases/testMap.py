from in_game_objects.map import Map
import unittest

from utils import Config


class Test_case_Map(unittest.TestCase):

    def setUp(self):
        self.map = Map(Config('config.json'))

    def test_check_planets_count(self):
        a = self.map.run([1, 2])
        self.assertEqual(len(a) >= 40 & len(a) <= 55, True, "wrong planets count")

    def test_check_start_position_equal_radius_generated(self):  # Точность теста около 1 процента +-
        self.map.generate_start_position([1, 2, 3, 4, 5])
        temp = self.map.planets[1].coords.calc_radius()
        for i in range(len(self.map.planets) - 1):
            self.assertEqual(self.map.planets[i + 1].coords.calc_radius() - temp < (temp / 100),
                             True, "radiuses arent the same")

    def test_check_start_position_player_to_player_distance(self):  # Точность теста около 1 процента +-
        players_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.map.generate_start_position(players_ids)
        temp = self.map.planets[0].coords.calc_distance(
            self.map.planets[len(players_ids)-1].coords)
        for i in range(len(players_ids) - 1):
            self.assertEqual(self.map.planets[i].coords.calc_distance(
                self.map.planets[i + 1].coords) - temp < (temp / 100), True, "wrong distance to planets")


if __name__ == '__main__':
    unittest.main()
