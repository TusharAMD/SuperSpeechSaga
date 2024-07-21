# File: player.py

import pygame

class Player:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = image
        self.speed = 5
        self.sanity = 100
        self.inventory = []
        self.knowledge = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                print(f"Inventory: {self.inventory}")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
