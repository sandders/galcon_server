import select
import socket
import struct
from typing import Dict, List, Union

from in_game_objects.map import Map
from in_game_objects.planet import Planet
from utils import Config, EventQueue, ID_GENERATOR, StoppableThread
from event_schema import ClientEvent, ClientEventSchema, GameEvent, ServerEventSchema, ServerEvent
from in_game_objects.player import Player

class TCPHandler:
    def __init__(self, config_path: str):
        self.configuration = Config(config_path)
        self.receiver_timeout = self.configuration['Server']['select_timeout']
        self.host = self.configuration['Server']['ip']
        self.port = self.configuration['Server']['port']
        self.max_client_count = self.configuration['Server']['max_client_count']
        self.server = self.tcp_server((self.host, self.port), self.max_client_count)
        self.clients: List[socket.socket] = []
        self.players: Dict[socket.socket, Player] = {}
        self.next_player_id = 0
        self.readiness = False
        self.game_started = False
        self.handler_queue = EventQueue()
        self.sender_queue = EventQueue()
        self.threads: List[StoppableThread] = []

    def start(self):
        self.start_receiver_thread()
        self.start_handler_thread()
        self.start_sender_thread()

    def stop(self):
        for thread in self.threads:
            thread.stop()
            #thread.join()
        self.server.close()

    @staticmethod
    def tcp_server(server_address: Union[tuple, str, bytes], backlog: int, blocking: bool = False) -> socket.socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(blocking)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(server_address)
        server_socket.listen(backlog)
        return server_socket

    def receive_clients(self):
        while True:
            readable, *_ = select.select([self.server, *self.clients], [], [], self.receiver_timeout)

            for sock in readable:
                if sock is self.server:
                    self.wait_for_client(sock)
                else:
                    self.wait_for_client_data(sock)

    def wait_for_client(self, server_sock):
        if not  self.game_started and not self.readiness and len(self.clients) < self.max_client_count:
            client, address = server_sock.accept()
            client.setblocking(0)
            self.next_player_id += 1
            player = Player(address, self.next_player_id)
            self.notify(ServerEventSchema.PLAYER_INIT, {
                'players': [pl.get_info() for pl in self.players.values()],
                "id": player.id
            }, receivers=client)
            self.notify(ServerEventSchema.CONNECT, {
                'player': player.get_info()
            }, receivers=[cl for cl in self.clients])
            self.clients.append(client)
            self.players[client] = player

    def wait_for_client_data(self, client_sock):
        try:
            data_size = client_sock.recv(struct.calcsize('i'))

            if data_size:
                data_size = struct.unpack('i', data_size)[0]
                event = client_sock.recv(data_size)

                if event:
                    player = self.players[client_sock]
                    event = ClientEvent(player, event)
                    self.handler_queue.insert(event)
                else:
                    self.remove_client(client_sock)
            else:
                self.remove_client(client_sock)
        except ConnectionResetError:
            self.remove_client(client_sock)

    def remove_client(self, client_sock):
        player = self.players[client_sock]
        self.clients.remove(client_sock)
        del self.players[client_sock]
        client_sock.close()
        self.notify(ServerEventSchema.DISCONNECT, {
            'player': player.get_info(),
        })

    def send_events(self):
        while True:
            if not self.sender_queue.empty():
                event = self.sender_queue.remove()
                receivers = event.payload.pop("receivers", self.clients)

                for client in receivers:
                    client.send(event.request())

    def notify(self, name: str, args: dict, receivers=None):
        if receivers is not None:
            if not isinstance(receivers, list):
                receivers = [receivers, ]
            args['receivers'] = receivers

        self.sender_queue.insert(ServerEvent(name, **args))

    def handle_events(self):
        while True:
            if not self.handler_queue.empty():
                event = self.handler_queue.remove()
                player = event.payload['player']

                if event.name == ClientEventSchema.READY:
                    self.on_event_ready(event, player)
                elif event.name == ClientEventSchema.RENDERED:
                    self.on_event_rendered(player)
                elif self.game_started:
                    if event.name == ClientEvent.MOVE:
                        self.on_event_move(event, player)
                    elif event.name == ClientEvent.SELECT:
                        self.on_event_select(event, player)
                    elif event.name == ClientEvent.ADD_HP:
                        self.on_event_add_hp(event, player)
                    elif event.name == ClientEvent.DAMAGE:
                        self.on_event_damage(event, player)

    def on_event_ready(self, event: GameEvent, player: Player):
        player.ready = event.payload['ready']
        self.notify(event.name, {
            'player': player.id,
            'ready': event.payload['ready'],
        })

        all_ready = all(player.ready for player in self.players.values())

        if all_ready and len(self.players) > 1:
            gen = Map(self.configuration)
            map_ = gen.run([player.id for player in self.players.values()])
            game_map = [planet.get_dict() for planet in map_]
            self.readiness = True
            self.notify(ServerEventSchema.MAP_INIT, {
                'map': game_map,
            })

    def on_event_rendered(self, player: Player):
        player.rendered = True

        if all(player.rendered for player in self.players.values()):
            self.notify(ServerEventSchema.GAME_STARTED, {})
            self.game_started = True

    def on_event_move(self, event: GameEvent, player: Player):
        if int(event.payload['unit_id']) in player.object_ids:
            self.notify(event.name, event.payload)

    def on_event_select(self, event: GameEvent, player: Player):
        planet_ids = event.payload['from']
        percentage = event.payload['percentage']
        punits = {}

        for planet_id in planet_ids:
            planet_id = int(planet_id)

            if Planet.cache[planet_id].owner == player.id:
                new_ships_count = round(Planet.cache[planet_id].units_count * int(percentage) / 100.0)
                Planet.cache[planet_id].units_count -= new_ships_count
                punits[planet_id] = [next(ID_GENERATOR) for _ in range(new_ships_count)]
                player.object_ids += punits[planet_id]

        self.notify(event.name, {
            'selected': punits,
        })

    def on_event_add_hp(self, event: GameEvent, player: Player):
        planet_id = int(event.payload['planet_id'])
        hp_count = int(event.payload['hp_count'])
        planet = Planet.cache[planet_id]

        if planet.owner == player.id:
            planet.units_count += hp_count
            self.notify(event.name, event.payload)

    def check_game_over(self):
        active_players = []

        for player in self.players.values():
            if len(player.object_ids) > 0:
                for planet in Planet.cache.values():
                    if planet.owner == player.id:
                        active_players.append(player.id)
                        break
            if len(active_players) >= 2:
                break
        else:
            self.notify(ServerEventSchema.GAME_OVER, {
                'winner': active_players[0],
            })

            self.readiness = False
            self.game_started = False
            self.players = {}
            self.clients = []

    def on_event_damage(self, event: GameEvent, player: Player):
        planet_id = int(event.payload['planet_id'])
        unit_id = int(event.payload['unit_id'])
        hp_count = int(event.payload.get('hp_count', 1))
        planet = Planet.cache[planet_id]

        if unit_id in player.object_ids:
            if planet.owner == player.id:
                planet.units_count += hp_count
            else:
                planet.units_count -= hp_count
                if planet.units_count < 0:
                    planet.owner = player.id
                    planet.units_count = abs(planet.units_count)

            player.object_ids.remove(unit_id)

            self.notify(event.name, {
                'planet_change': {
                    'id': planet_id,
                    'units_count': planet.units_count,
                    'owner': planet.owner,
                },
                'unit_id': unit_id,
            })

        self.check_game_over()

    def start_receiver_thread(self):
        receiver_thread = StoppableThread(name='receiver', target=self.receive_data)
        self.threads.append(receiver_thread)
        receiver_thread.start()

    def start_handler_thread(self):
        handler_thread = StoppableThread(name='handler', target=self.handle_events)
        self.threads.append(handler_thread)
        handler_thread.start()

    def start_sender_thread(self):
        sender_thread = StoppableThread(name='sender', target=self.send_events)
        self.threads.append(sender_thread)
        sender_thread.start()

    def receive_data(self):
        while True:
            try:
                readable, *_ = select.select([self.server, *self.clients], [], [], self.receiver_timeout)

                for sock in readable:
                    if sock is self.server:
                        self.wait_for_client(sock)
                    else:
                        self.wait_for_client_data(sock)
            except OSError as e:
                break
