from queue import PriorityQueue
from threading import Event, Lock, Thread

from event_schema import EventSchema

import json

class Config:
    def __init__(self, filename):
        self.config_data = self._load_config(filename)

    def _load_config(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            config_str = file.read()
            config_data = json.loads(config_str)
        return config_data

    def __getitem__(self, key):
        return self.config_data[key]

def __generate_id() -> int:
    """ ID generator """
    id_ = 1
    while True:
        yield id_
        id_ += 1


ID_GENERATOR = __generate_id()


class PriorityEvent(object):
    """ Event priority queue item """

    def __init__(self, event, priority):
        self.event = event

        if priority is None:
            self.priority = self.__priority_factory()
        else:
            self.priority = priority

    def __priority_factory(self) -> int:
        if self.event.name == EventSchema.MOVE:
            return 0
        return 1

    def __gt__(self, other):
        return self.priority < other.priority

    def __lt__(self, other):
        return self.priority > other.priority


class EventQueue(object):
    """ Event priority queue """

    def __init__(self):
        self.__queue = PriorityQueue()
        self.__mutex = Lock()

    def insert(self, event, priority=None):
        with self.__mutex:
            item = PriorityEvent(event, priority)
            self.__queue.put(item)

    def remove(self):
        with self.__mutex:
            item = self.__queue.get()
        return item.event if item else None

    def empty(self):
        with self.__mutex:
            return self.__queue.empty()


class Coordinate(object):
    """ Coordinate point """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def get_dict(self):
        return {'x': self.x, 'y': self.y}

    def calc_radius(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def get_coordinates(self):
        return self.x, self.y

    def calc_distance(self, point):
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5


class StoppableThread(Thread):
    """ Thread wrapper with manual stop """

    def __init__(self, target=None, name=None, args=(), **kwargs):
        self._target = target
        self._args = args
        self._kwargs = kwargs
        super().__init__(target=target, name=name, args=args, kwargs=kwargs)
        self.stopper = Event()

    def is_alive(self):
        return not self.stopper.is_set()

    def run(self):
        while not self.stopper.is_set():
            self._target()

    def start(self):
        super().start()
        print('{} initiated'.format(self.name))

    def stop(self):
        print('Stopping {}'.format(self.name))
        self.stopper.set()
        print('{} stopped'.format(self.name))
