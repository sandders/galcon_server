from abc import ABC
import json
import struct

from in_game_objects.player import Player


class EventSchema(ABC):
    READY = 'ready'
    RENDERED = 'rendered'
    MOVE = 'move'
    SELECT = 'select'
    ADD_HP = 'add_hp'
    DAMAGE = 'damage'

class ServerEventSchema(EventSchema):
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    PLAYER_INIT = 'player_init'
    MAP_INIT = 'map_init'
    GAME_STARTED = 'game_started'
    GAME_OVER = 'game_over'


class ClientEventSchema(EventSchema):
    pass


class GameEvent(ABC):
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.payload = kwargs


class ServerEvent(GameEvent):
    def request(self) -> bytes:
        string = json.dumps({'name': self.name, **self.payload})
        return struct.pack('i', len(string)) + string.encode('utf-8')


class ClientEvent(GameEvent):
    def __init__(self, player: Player, string: str):
        super().__init__(**json.loads(string, object_hook=lambda d: {**d, 'player': player}))
