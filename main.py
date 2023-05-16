import os
import random
import threading

import pygame

from enemy import Enemy
from player import Player

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
run = True
enemies = []
lives = 500

player = Player(300, 630)


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
    global run, enemies
    FPS = 60
    level = 0

    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 40)

    enemies = []
    enemy_vel_max = 3
    enemy_vel_min = 1

    for i in range(5):
        # enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
        enemy1 = Enemy(100, random.randrange(-1500, -100))
        enemy_vel = random.randrange(enemy_vel_min, enemy_vel_max)
        enemy1.vel = enemy_vel
        enemies.append(enemy1)
    wave_length = 5

    player_vel = 5

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
        for enemy1 in enemies:
            enemy1.draw(SCREEN)
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
                # enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                enemy1 = Enemy(100, random.randrange(-1500, -100))
                enemy_vel = random.randrange(enemy_vel_min, enemy_vel_max)
                enemy1.vel = enemy_vel
                enemies.append(enemy1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        player_thread = threading.Thread(target=player_move(player, player_vel))
        player.move_lasers(-5, enemies)
        player_thread.start()
        for enemy in enemies:
            enemy_thread = threading.Thread(target=enemy.run_thread(player, enemies, lives))
            enemy_thread.start()


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
