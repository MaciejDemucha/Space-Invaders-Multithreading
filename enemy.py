import random

from laser import Laser, collide
from ship import Ship
import pygame
import os

ENEMY_SHIP = pygame.image.load(os.path.join("assets", "enemy.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
WIDTH, HEIGHT = 750, 750


class Enemy(Ship):

    def __init__(self, x, y, health=10):
        super().__init__(x, y, health)
        self.ship_img = ENEMY_SHIP
        self.laser_img = RED_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.vel = 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
