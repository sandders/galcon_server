import unittest
from in_game_objects.player import Player

ADDRESS_DEFAULT = (1, 2, 3)
PLAYER_ID_DEFAULT = 23


class TestClassPLayer(unittest.TestCase):

    def setUp(self):
        self.player = Player(ADDRESS_DEFAULT, PLAYER_ID_DEFAULT)

    def test_constructor(self):
        self.assertEqual(self.player.id, PLAYER_ID_DEFAULT, 'incorrect id init')
        self.assertEqual(self.player.addr, ADDRESS_DEFAULT, 'incorrect address init')

    def test_info(self):
        self.assertEqual({'id': self.player.id, 'nickname': self.player.nickname,
                          'ready': self.player.ready}, self.player.get_info(),
                         'incorrect dictionary format')


if __name__ == '__main__':
    unittest.main()
