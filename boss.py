import pygame
import os
import random
import threading
from ship import Ship

clock = pygame.time.Clock()
WIDTH, HEIGHT = 750, 750

main_path = os.path.dirname(os.path.realpath(__file__))
mutex = threading.Lock()

# Load images
BOSS1_SPACESHIP = pygame.image.load(os.path.join("assets", "boss.png"))


# Class representing the boss ship objects which using threading to run
class Boss(Ship, threading.Thread):

    # init method which initially calls the parent classes' inits, sets the images used, health and movement speed
    def __init__(self, x: int, y: int, layer: pygame.Surface, health=20):
        super().__init__(x, y, health)
        threading.Thread.__init__(self)
        self.not_collision = True
        super().__init__(x, y, health)
        self.ship_img = BOSS1_SPACESHIP
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.layer = layer
        self.max_health = health

        self.vel_y = 4.0
        self.vel_x = random.randrange(0, 10)

    # function used to determine whether the ship has hit one of the game area's borders, changes the ship's speed to
    # be used further
    def check_border(self):
        if self.x < 0 or (self.x + self.ship_img.get_width()) > WIDTH:
            self.vel_x *= -1.0

        if self.y < 0 or (self.y + self.ship_img.get_height()) > HEIGHT - 100:
            self.vel_y *= -1.0

    # temporary str() function returning the ship's current health, used for debugging
    def __str__(self):
        return str(self.health)

    # run() method used by the threading aspect of the class object, moves and draws the ship on its layer each
    # frame, provided that its health is positive
    def run(self):
        while self.health > 0:
            clock.tick(60)

            self.move()

            self.layer.fill((255, 255, 0))
            self.draw(self.layer)

        self.layer.fill((255, 255, 0))
        self.layer = None

    # draws the ship's image and its healthbar on the designated window
    def draw(self, window):
        mutex.acquire(timeout = 10)
        try:
            super().draw(window)
            self.healthbar(window)
        finally:
           mutex.release()

    # determines the healthbar's length and proceeds to draw it on the designated window
    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width() * (self.health / self.max_health),
                                               10))

    # a function which calculates the ship's position based on its current speed parameters
    def move(self):
        self.check_border()
        self.x += self.vel_x
        self.y += self.vel_y
