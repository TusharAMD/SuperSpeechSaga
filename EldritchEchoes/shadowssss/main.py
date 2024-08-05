# File: main.py

import pygame
import sys
from game import CosmicShadows
from assets import load_assets

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Shadows")

# Load assets
assets = load_assets()

def main():
    clock = pygame.time.Clock()
    game = CosmicShadows(screen, assets)

    running = True
    while running:
        dt = clock.tick(60) / 1000  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update(dt)
        game.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()