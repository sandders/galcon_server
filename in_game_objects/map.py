import math
import random
import matplotlib.pyplot as plt
import numpy as np

from typing import List

from in_game_objects.planet import Planet, PlanetSize


class Coords:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def get_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    def calc_radius(self) -> float:
        return math.hypot(self.x, self.y)

    def get_coord(self) -> tuple:
        return self.x, self.y

    def calc_distance(self, point: 'Coords') -> float:
        return math.hypot(self.x - point.x, self.y - point.y)



class Map:
    def __init__(self, configuration, planet_free_space_radius=None):
        self.screen_length = configuration['Screen']['length_multiplier'] * configuration['Screen']['multiplier']
        self.screen_height = configuration['Screen']['height_multiplier'] * configuration['Screen']['multiplier']
        self.border_angle = math.degrees(math.atan(self.screen_height / self.screen_length))
        self.planets = []
        self.max_planet_count = random.randint(40, 55)
        self.players = -1
        self.start_position_radius = 0
        self.max_gen_try_subplanets = 25
        self.max_gen_try_separated_planets = self.max_gen_try_subplanets * 200

        if planet_free_space_radius:
            self.planet_free_space_radius = planet_free_space_radius
        else:
            self.planet_free_space_radius = round(50 / 120 * configuration['Screen']['multiplier'])

    def run(self, players_ids: List[int]) -> List[Planet]:
        self.players = len(players_ids)
        self.generate_start_position(players_ids)
        self.generate_subplanets()
        self.generate_separated_planets()
        return self.planets

    def generate_start_position(self, players_ids: List[int]):
        players_count = len(players_ids)
        planets = []
        alpha = random.randint(0, int(360 / players_count))

        for player_id in players_ids:
            coord = Coords()
            tang = math.tan(math.radians(alpha))

            if alpha >= 360:
                alpha -= 360

            if alpha in (90, 270):
                coord.x = 0
                coord.y = self.screen_height * math.sin(math.radians(alpha)) / 2
            elif alpha in (0, 180):
                coord.x = self.screen_length * math.cos(math.radians(alpha)) / 2
                coord.y = 0
            elif 0 < alpha < 90:
                if alpha >= self.border_angle:
                    height_border = self.screen_height / 2
                    coord.x = height_border / tang
                    coord.y = height_border
                else:
                    height_border = self.screen_length / 2
                    coord.x = height_border
                    coord.y = height_border * tang
            elif 90 < alpha < 180:
                if alpha <= 180 - self.border_angle:
                    height_border = self.screen_height / 2
                    coord.x = height_border / tang
                    coord.y = height_border
                else:
                    height_border = self.screen_length / 2
                    coord.x = -height_border
                    coord.y = abs(height_border * tang)
            elif 180 < alpha < 270:
                if alpha >= 180 + self.border_angle:
                    height_border = self.screen_height / 2
                    coord.x = -height_border / tang
                    coord.y = -height_border
                else:
                    height_border = self.screen_length / 2
                    coord.x = -height_border
                    coord.y = -height_border * tang
            elif 270 < alpha < 360:
                if alpha <= 360 - self.border_angle:
                    height_border = self.screen_height / 2
                    coord.x = abs(height_border / tang)
                    coord.y = -height_border
                else:
                    height_border = self.screen_length / 2
                    coord.x = self.screen_length / 2
                    coord.y = height_border * tang

            planets.append([coord.calc_radius(), Planet(coord, PlanetSize.BIG, player_id, units_count=100), alpha])
            alpha += 360 / players_count

        min_rad = min(planets, key=lambda x: x[0])
        self.start_position_radius = min_rad[0] - self.planet_free_space_radius

        for p in planets:
            p[1].coords.x = int(self.start_position_radius * math.cos(math.radians(p[2])))
            p[1].coords.y = int(self.start_position_radius * math.sin(math.radians(p[2])))
            p[0] = self.start_position_radius

        self.planets += [planet[1] for planet in planets]

    @staticmethod
    def get_random_planet_type() -> str:
        return random.choices([PlanetSize.SMALL, PlanetSize.MEDIUM, PlanetSize.BIG], [600, 300, 200])[0]

    def generate_subplanets(self):
        subplanet_max_count = round((self.max_planet_count - self.players - 1) * 0.6 / self.players)

        for planet in self.planets[:self.players]:
            subplanet_num = 0
            try_num = 0
            subplanets = []

            while try_num <= self.max_gen_try_subplanets and subplanet_num < subplanet_max_count:
                sub_alpha = random.randint(0, 359)
                sub_radius = random.randint(
                    2 * self.planet_free_space_radius,
                    int(self.start_position_radius * math.sin(math.radians(180 / self.players))) - self.planet_free_space_radius
                )

                check = True
                new_planet = Planet(
                    Coords(
                        sub_radius * math.cos(math.radians(sub_alpha)) + planet.coords.x,
                        sub_radius * math.sin(math.radians(sub_alpha)) + planet.coords.y
                    ),
                    self.get_random_planet_type()
                )

                if abs(new_planet.coords.x) > self.screen_length / 2 - self.planet_free_space_radius or abs(new_planet.coords.y) > self.screen_height / 2 - self.planet_free_space_radius:
                    try_num += 1
                    continue

                for sp in subplanets:
                    if new_planet.coords.calc_distance(sp.coords) < 2 * self.planet_free_space_radius:
                        check = False
                        break

                if check:
                    subplanets.append(new_planet)
                    try_num = 0
                else:
                    try_num += 1

                subplanet_num += 1

            self.planets += subplanets

    def generate_separated_planets(self):
        separated_max_count = self.max_planet_count - len(self.planets)
        separated_num = 0
        try_num = 0
        separated = []

        while try_num <= self.max_gen_try_separated_planets and separated_num < separated_max_count:
            x = random.randint(-self.screen_length / 2, self.screen_length / 2)
            y = random.randint(-self.screen_height / 2, self.screen_height / 2)

            check = True
            new_planet = Planet(Coords(x, y), self.get_random_planet_type())

            if abs(new_planet.coords.x) > self.screen_length / 2 - self.planet_free_space_radius or abs(new_planet.coords.y) > self.screen_height / 2 - self.planet_free_space_radius:
                check = False

            subradius = self.start_position_radius * math.sin(math.radians(180 / self.players))

            for p in self.planets[:self.players]:
                if new_planet.coords.calc_distance(p.coords) < subradius:
                    check = False
                    break

            for s in separated:
                if new_planet.coords.calc_distance(s.coords) < 2 * self.planet_free_space_radius:
                    check = False
                    break

            if check:
                separated.append(new_planet)
                try_num = 0
            else:
                try_num += 1

            separated_num += 1

        self.planets += separated

    def display(self):
        coords = []

        plt.figure()

        colors = ['red', 'orange', 'brown', 'purple']

        for i in self.planets:
            position = i.coords.get_coord()
            coords.append(position)

        X = np.array(coords)

        plt.axis("equal")
        plt.xlim((-self.screen_length / 2 - 150, self.screen_length / 2 + 150))
        plt.ylim((-self.screen_height / 2 - 150, self.screen_height / 2 + 150))

        t1 = plt.Polygon(X[:self.players], fill=False, color="black")
        plt.gca().add_patch(t1)

        screen = plt.Rectangle((-self.screen_length / 2, -self.screen_height / 2), self.screen_length, self.screen_height, fill=False, color="black")
        plt.gca().add_patch(screen)
        colors = [colors[i.type.value - 1] for i in self.planets]

        plt.scatter(X[:, 0], X[:, 1], color=colors)

        plt.show()
