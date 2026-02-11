import pygame
import math

pygame.font.init()

#pygame window size 1000x1000
WIDTH = 1300
HEIGHT = 1300

#create class for different planets
class Planet:
    AU = 149.6e6 * 1000 #Astronomical unit in meters
    G = 6.67428e-11 #Gravitational constant in m^3 kg^-1 s^-2
    SCALE = 250 / AU # 1 AU = 250 pixels
    TIME = 3600 * 24 #1 day rotation

    def __init__(self, x, y, radius, mass, color): #initialize class
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.is_sun = False
        self.distance_to_sun = 0
        self.y_velocity = 0
        self.x_velocity = 0
        self.orbit = []

    def force_of_attraction(self, other):
        other_x = other.x
        other_y = other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt((distance_x ** 2) + (distance_y ** 2))
        force = (self.G * self.mass * other.mass) / distance ** 2 #force of attraction formula
        angle = math.atan2(distance_y, distance_x)
        x_force = math.cos(angle) * force
        y_force = math.sin(angle) * force

        if other.is_sun:
            self.distance_to_sun = distance

        return x_force, y_force

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.force_of_attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_velocity += total_fx / self.mass * self.TIME
        self.y_velocity += total_fy / self.mass * self.TIME

        self.x += self.x_velocity * self.TIME
        self.y += self.y_velocity * self.TIME
        self.orbit.append((self.x, self.y))


    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2
        pygame.draw.circle(win, self.color, (x, y), self.radius)