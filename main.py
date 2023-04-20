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

# Player player
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "player.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

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
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def draw(self, window):
        super().draw(window)


class Enemy(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = ENEMY_SHIP
        self.mask = pygame.mask.from_surface(self.ship_img)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def enemy_move(vel, enemy):
    enemy.y += vel


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


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 40)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5

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

        for enemy in enemies:
            enemy.draw(SCREEN)

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
            # for i in range(wave_length):
            enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
            enemies.append(enemy1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        player_thread = threading.Thread(target=player_move(player, player_vel))
        player_thread.start()

        for enemy in enemies[:]:
            # enemy.move(enemy_vel)
            enemy_thread = threading.Thread(target=enemy_move(enemy_vel, enemy))
            enemy_thread.start()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)


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
