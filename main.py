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

    #Jupiter
    jupiter = Planet(5.20 * Planet.AU, 0, 23, 1.8981 * (10**27), (209, 167, 127))
    jupiter.y_velocity = 1.3056 * (10**4)

    #Saturn
    saturn = Planet(9.50 * Planet.AU, 0, 20, 5.6832 * (10**26), (237, 219, 173))
    saturn.y_velocity = 9.6391 * (10**3)

    #Neptune
    neptune = Planet(30.06 * Planet.AU, 0, 19, 1.0241 * (10**26), (124, 183, 187))
    neptune.y_velocity = 5.4349 * (10**3)

    planets = [sun, earth, venus, mercury, mars, jupiter, neptune, saturn]

    while run:
        clock.tick(60)
        WIN.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll UP -> Zoom In
                    Planet.SCALE *= 1.1
                    for planet in planets:
                        planet.radius *= 1.1
                if event.button == 5:  # Scroll DOWN -> Zoom Out
                    Planet.SCALE /= 1.1
                    for planet in planets:
                        planet.radius /= 1.1

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        pygame.display.update()

    pygame.quit()

main()

