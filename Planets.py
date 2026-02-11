import pygame
import math

pygame.font.init()

#pygame window size 1000x1000
WIDTH = 1300
HEIGHT = 1300

#create class for different planets
class Planet:
    AU = 149597870700 #Astronomical unit in meters
    G = 6.6743 * 10e-11 #Gravitational constant in m^3 kg^-1 s^-2
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

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2
        pygame.draw.circle(win, self.color, (x, y), self.radius)