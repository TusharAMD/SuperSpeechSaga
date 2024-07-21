# File: npc.py

import pygame

class NPC:
    def __init__(self, x, y, image, name):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = image
        self.name = name

    def draw(self, screen):
        screen.blit(self.image, self.rect)
