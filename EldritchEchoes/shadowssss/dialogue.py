# File: dialogue.py

import pygame

class DialogueSystem:
    def __init__(self, background_image):
        self.background = background_image
        self.dialogues = {
            "Detective": [
                "Welcome to Shadowbrook. I'm Detective Johnson.",
                "We've been experiencing some strange occurrences lately.",
                "I hope you can help us get to the bottom of this mystery."
            ]
        }
        self.current_npc = None
        self.dialogue_index = 0

    def start_dialogue(self, npc_name):
        self.current_npc = npc_name
        self.dialogue_index = 0
        return self.dialogues[npc_name][self.dialogue_index]

    def next(self):
        self.dialogue_index += 1
        if self.dialogue_index < len(self.dialogues[self.current_npc]):
            return self.dialogues[self.current_npc][self.dialogue_index]
        else:
            return None

    def draw(self, screen, current_dialogue):
        screen.blit(self.background, (50, 400))
        font = pygame.font.Font(None, 28)
        text = font.render(current_dialogue, True, (255, 255, 255))
        screen.blit(text, (60, 410))