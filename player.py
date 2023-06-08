from ship import Ship
import pygame
import os

PLAYER_SHIP = pygame.image.load(os.path.join("assets", "player.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
WIDTH, HEIGHT = 750, 750

class Player(Ship):
    def __init__(self, x, y, health=1000):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = GREEN_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, enemies, bosses):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for enemy in enemies:
                    if laser.collision(enemy):
                        enemies.remove(enemy)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                for boss in bosses:
                    if laser.collision(boss):
                        boss.health -= 10
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
