import random


class Player:
    def __init__(self, addr: tuple, pid: int):
        
        self.id = pid
        self.nickname = self.generate_nickname()
        self.ready = False
        self.addr = addr
        self.objects = []
        

    def generate_nickname(self):
        return ''.join([chr(random.randint(97, 122)) for _ in range(6)])

    def get_info(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'ready': self.ready,
        }
