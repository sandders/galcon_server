from tcp_handler import *
import unittest


class Test_case_Server(unittest.TestCase):

    def setUp(self):
        self.server=TCPHandler('config.json')

    def test_start_threads(self):
        self.server.start()
        for thread in self.server.threads:
            self.assertEqual(thread.is_alive(), True, 'not all threads started')
        self.server.stop()

    def test_stop_threads(self):
        self.server.start()
        self.server.stop()
        for thread in self.server.threads:
            self.assertEqual(thread.is_alive(), False, 'not all threads stopped')


ADDRESS_DEFAULT = (1, 2, 3)
PLAYER_ID_DEFAULT = 23

SERVER_ADDRESS = ('', 9080)
BACKLOG = 10


class TestFunctions(unittest.TestCase):

    def test_create_tcp_server(self):
        tcp_server = TCPHandler.tcp_server(SERVER_ADDRESS, BACKLOG)
        self.assertEqual(str(type(tcp_server)), "<class 'socket.socket'>", 'incorrect return type')


if __name__ == '__main__':
    unittest.main()
