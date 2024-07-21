# File: game.py

import pygame
from player import Player
from npc import NPC
from puzzle import Puzzle
from dialogue import DialogueSystem
import json

class GameState:
    MENU = 0
    PLAYING = 1
    DIALOGUE = 2
    PUZZLE = 3
    INVENTORY = 4

class CosmicShadows:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.state = GameState.MENU
        self.player = Player(400, 300, assets['player_image'])
        self.npcs = [NPC(200, 200, assets['npc_image'], "Detective")]
        self.puzzles = [Puzzle("Decrypt the ancient tome", "ELDRITCHHORROR", "Unscramble the letters")]
        self.dialogue_system = DialogueSystem(assets['dialogue_bg'])
        self.current_dialogue = None
        self.sanity_drain_rate = 1  # Sanity points lost per second
        self.load_game()

    def handle_event(self, event):
        if self.state == GameState.PLAYING:
            self.player.handle_event(event)
        elif self.state == GameState.DIALOGUE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.current_dialogue = self.dialogue_system.next()
                if self.current_dialogue is None:
                    self.state = GameState.PLAYING
        elif self.state == GameState.PUZZLE:
            if event.type == pygame.KEYDOWN:
                self.puzzles[0].input_letter(event.unicode)

    def update(self, dt):
        if self.state == GameState.PLAYING:
            self.player.update(dt)
            self.update_sanity(dt)
            self.check_npc_interactions()
        elif self.state == GameState.PUZZLE:
            if self.puzzles[0].is_solved():
                self.state = GameState.PLAYING
                self.player.knowledge += 1

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == GameState.PLAYING:
            self.player.draw(self.screen)
            for npc in self.npcs:
                npc.draw(self.screen)
        elif self.state == GameState.DIALOGUE:
            self.dialogue_system.draw(self.screen, self.current_dialogue)
        elif self.state == GameState.PUZZLE:
            self.puzzles[0].draw(self.screen)

        # Draw sanity meter
        pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, self.player.sanity * 2, 20))
        
        pygame.display.flip()

    def update_sanity(self, dt):
        self.player.sanity -= self.sanity_drain_rate * dt
        if self.player.sanity <= 0:
            self.game_over()

    def check_npc_interactions(self):
        for npc in self.npcs:
            if self.player.rect.colliderect(npc.rect):
                self.start_dialogue(npc)

    def start_dialogue(self, npc):
        self.state = GameState.DIALOGUE
        self.current_dialogue = self.dialogue_system.start_dialogue(npc.name)

    def game_over(self):
        print("Game Over - Sanity depleted")
        self.save_game()
        pygame.quit()
        sys.exit()

    def save_game(self):
        game_state = {
            "player": {
                "x": self.player.rect.x,
                "y": self.player.rect.y,
                "sanity": self.player.sanity,
                "inventory": self.player.inventory,
                "knowledge": self.player.knowledge
            },
            "npcs": [{"x": npc.rect.x, "y": npc.rect.y, "name": npc.name} for npc in self.npcs],
            "puzzles": [puzzle.to_dict() for puzzle in self.puzzles]
        }
        with open("savegame.json", "w") as f:
            json.dump(game_state, f)

    def load_game(self):
        try:
            with open("savegame.json", "r") as f:
                game_state = json.load(f)
            self.player.rect.x = game_state["player"]["x"]
            self.player.rect.y = game_state["player"]["y"]
            self.player.sanity = game_state["player"]["sanity"]
            self.player.inventory = game_state["player"]["inventory"]
            self.player.knowledge = game_state["player"]["knowledge"]
            self.npcs = [NPC(npc["x"], npc["y"], self.assets['npc_image'], npc["name"]) for npc in game_state["npcs"]]
            self.puzzles = [Puzzle.from_dict(puzzle_dict) for puzzle_dict in game_state["puzzles"]]
        except FileNotFoundError:
            print("No save game found. Starting new game.")
