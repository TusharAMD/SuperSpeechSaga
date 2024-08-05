# File: puzzle.py

import pygame

class Puzzle:
    def __init__(self, name, solution, clue):
        self.name = name
        self.solution = solution
        self.clue = clue
        self.current_input = ""

    def input_letter(self, letter):
        self.current_input += letter
        if len(self.current_input) > len(self.solution):
            self.current_input = self.current_input[1:]

    def is_solved(self):
        return self.current_input.lower() == self.solution.lower()

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        clue_text = font.render(self.clue, True, (255, 255, 255))
        input_text = font.render(self.current_input, True, (255, 255, 255))
        screen.blit(clue_text, (100, 100))
        screen.blit(input_text, (100, 150))

    def to_dict(self):
        return {
            "name": self.name,
            "solution": self.solution,
            "clue": self.clue,
            "current_input": self.current_input
        }

    @classmethod
    def from_dict(cls, data):
        puzzle = cls(data["name"], data["solution"], data["clue"])
        puzzle.current_input = data["current_input"]
        return puzzle