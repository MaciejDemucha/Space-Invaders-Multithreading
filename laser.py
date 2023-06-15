import pygame


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


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

    # Check if laser is at the end of the screen and needs to be removed
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    # Collision with objects
    def collision(self, obj):
        return collide(self, obj)
