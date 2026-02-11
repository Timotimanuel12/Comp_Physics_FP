import pygame
from Planets import Planet, WIDTH, HEIGHT
pygame.init()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Orbit")

BG = (255, 255, 255)


def main():
    run = True
    clock = pygame.time.Clock()

    sun = Planet(0, 0, 30, 1.988416 * (10 ** 30), (255, 255, 0))
    sun.sun = True

    # Earth Radius 15
    earth = Planet(-1 * Planet.AU, 0, 16, 5.9722 * (10 ** 24), (0, 0, 255))
    earth.y_velocity = 29.783 * 1000

    # Venus Radius 12
    venus = Planet(0.72 * Planet.AU, 0, 14, 4.8673 * (10 ** 24), (255, 255, 191))
    venus.y_velocity = 3.5020 * 10 ** 4

    # Mercury Radius 8
    mercury = Planet(0.40 * Planet.AU, 0, 8, 3.3010 * (10 ** 23), (134, 119, 95))
    mercury.y_velocity = 4.7362 * (10 ** 4)

    # Mars Radius 10
    mars = Planet(1.50 * Planet.AU, 0, 12, 6.4169 * (10 ** 23), (198, 123, 92))
    mars.y_velocity = 24.077 * 1000

    planets = [sun, earth, venus, mercury, mars]

    while run:
        clock.tick(60)
        WIN.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        pygame.display.update()

    pygame.quit()

main()

