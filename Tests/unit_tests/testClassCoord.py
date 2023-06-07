from utils import Coordinate
import unittest

x = 10
y = 15


class Test_case_coord(unittest.TestCase):

    def test_constructor(self):
        c = Coordinate(x, y)
        self.assertEqual(c.x, x,
                         'incorrect x')
        self.assertEqual(c.y, y, 'incorrect y')

    def test_str(self):
        c = Coordinate(x, y)
        self.assertEqual(c.__str__(), "(10, 15)", 'incorrect format of str')

    def test_get_dictionary(self):
        c = Coordinate(x, y)
        self.assertEqual(c.get_dict()["x"], x, 'incorrect convertion to dict (x)')
        self.assertEqual(c.get_dict()["y"], y, 'incorrect convertion to dict (x)')

    def test_calc_radius(self):
        c = Coordinate(x, y)
        self.assertEqual(c.calc_radius(), (c.x ** 2 + c.y ** 2) ** (0.5), 'incorrect radius-vector')

    def test_get_coord(self):
        c = Coordinate(x, y)
        self.assertEqual(c.get_coordinates(), (x, y), 'returned value is incorrect')

    def test_calc_distance(self):
        c = Coordinate(x, y)
        testList = [Coordinate(0, 0), Coordinate(x, y), Coordinate(5, 12)]
        for i, _ in enumerate(testList):
            with self.subTest(i=i):
                self.assertEqual(c.calc_distance(testList[i]),
                                 ((x - testList[i].x) ** 2 + (y - testList[i].y) ** 2) ** 0.5,
                                 "wrong calc_distance for point " + str(testList[i].x) + "," + str(testList[i].y))
