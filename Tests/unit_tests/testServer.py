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




if __name__ == '__main__':
    unittest.main()
