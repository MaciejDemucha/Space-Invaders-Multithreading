import threading

import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load images
ENEMY_SHIP = pygame.image.load(os.path.join("assets", "enemy.png"))

# Player
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "player.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=1000):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = GREEN_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)


class Enemy(Ship):

    def __init__(self, x, y, health=100):
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


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def enemy_move(enemy):
    enemy.y += enemy.vel


def player_move(player, player_vel):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x - player_vel > 0:  # left
        player.x -= player_vel
    if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
        player.x += player_vel
    if keys[pygame.K_w] and player.y - player_vel > 0:  # up
        player.y -= player_vel
    if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
        player.y += player_vel
    if keys[pygame.K_SPACE]:
        player.shoot()


def main():
    run = True
    FPS = 60
    level = 0
    lives = 500
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 40)

    enemies = []
    wave_length = 5
    enemy_vel_max = 3
    enemy_vel_min = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        SCREEN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        hp_label = main_font.render(f"Health: {player.health}", 1, (255, 255, 255))

        SCREEN.blit(lives_label, (10, 10))
        SCREEN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        SCREEN.blit(hp_label, (10, HEIGHT - 50))

        for enemy_ship in enemies:
            enemy_ship.draw(SCREEN)

        player.draw(SCREEN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            SCREEN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                enemy_vel = random.randrange(enemy_vel_min, enemy_vel_max)
                enemy1.vel = enemy_vel
                enemies.append(enemy1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        player_thread = threading.Thread(target=player_move(player, player_vel))
        player_thread.start()

        for enemy in enemies[:]:
            enemy_thread = threading.Thread(target=enemy_move(enemy))
            enemy_thread.start()
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        if len(enemies) > 1:
            for i in range(len(enemies)):
                for j in range(i + 1, len(enemies)):
                    print("i: " + str(i) + " j: " + str(j))
                    if collide(enemies[i], enemies[j]):
                        enemies.pop(i)
                        enemies.pop(j)
        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        SCREEN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        SCREEN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
