import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Shadows: Eldritch Encounters")

# Colors and Fonts
BLACK, WHITE, RED, GREEN, BLUE = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)
PURPLE, YELLOW, BROWN = (128, 0, 128), (255, 255, 0), (165, 42, 42)
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)

# Load images (using colored rectangles for simplicity)
player_img = pygame.Surface((32, 32))
player_img.fill(BLUE)
shoggoth_img = pygame.Surface((64, 64))
shoggoth_img.fill(PURPLE)
migo_img = pygame.Surface((48, 48))
migo_img.fill(GREEN)
deep_one_img = pygame.Surface((56, 56))
deep_one_img.fill((0, 100, 100))
chest_img = pygame.Surface((40, 40))
chest_img.fill(YELLOW)
weapon_img = pygame.Surface((24, 24))
weapon_img.fill(RED)
food_img = pygame.Surface((24, 24))
food_img.fill(BROWN)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = player_img
        self.speed = 5
        self.sanity = 100
        self.max_sanity = 100
        self.experience = 0
        self.skills = {"Investigation": 1, "Occult Knowledge": 1, "Mental Fortitude": 1}
        self.inventory = []
        self.equipped_weapon = None

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        screen.blit(self.image, self.rect)
        name = SMALL_FONT.render("Investigator", True, WHITE)
        screen.blit(name, (self.rect.x, self.rect.y - 20))

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= 100:
            self.level_up()

    def level_up(self):
        self.experience -= 100
        skill = random.choice(list(self.skills.keys()))
        self.skills[skill] += 1
        print(f"Leveled up {skill}! The forbidden knowledge grows...")

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def use_item(self, item):
        if isinstance(item, Weapon):
            self.equipped_weapon = item
            print(f"Equipped {item.name}")
        elif isinstance(item, Food):
            self.sanity = min(self.sanity + item.sanity_restore, self.max_sanity)
            self.inventory.remove(item)
            print(f"Used {item.name}. Sanity restored to {self.sanity}")

class Enemy:
    def __init__(self, name, image, health):
        self.name = name
        self.image = image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = health
        self.max_health = health

    def draw(self):
        screen.blit(self.image, self.rect)
        name = SMALL_FONT.render(self.name, True, WHITE)
        screen.blit(name, (self.rect.x, self.rect.y - 20))
        
        # Health bar
        bar_width = self.image.get_width()
        health_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, bar_width, 5))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, health_width, 5))

class CombatAnimation:
    def __init__(self, start_pos, end_pos, color):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.progress = 0
        self.speed = 0.05

    def update(self):
        self.progress += self.speed
        if self.progress > 1:
            return True
        return False

    def draw(self):
        current_pos = (
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress,
            self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        )
        pygame.draw.line(screen, self.color, self.start_pos, current_pos, 2)

class Combat:
    def __init__(self, player):
        self.player = player
        self.enemy = None
        self.is_active = False
        self.eldritch_horrors = [
            ("Shoggoth", shoggoth_img, 100),
            ("Mi-go", migo_img, 80),
            ("Deep One", deep_one_img, 90)
        ]
        self.animations = []

    def start_combat(self):
        enemy_data = random.choice(self.eldritch_horrors)
        self.enemy = Enemy(*enemy_data)
        self.is_active = True

    def resolve(self, action):
        start_pos = (self.player.rect.centerx, self.player.rect.centery)
        end_pos = (self.enemy.rect.centerx, self.enemy.rect.centery)
        
        weapon_bonus = self.player.equipped_weapon.damage if self.player.equipped_weapon else 0
        
        if action == "evade":
            success = random.random() < 0.9 + (self.player.skills["Mental Fortitude"] * 0.05)
            self.animations.append(CombatAnimation(start_pos, end_pos, BLUE))
            if success:
                self.enemy.health -= 10 + weapon_bonus
                result = f"You successfully evaded the {self.enemy.name}, but the memory lingers..."
            else:
                self.player.sanity -= 5
                result = f"Evasion failed. The {self.enemy.name}'s presence shatters your perception of reality."
        elif action == "confront":
            success = random.random() < 0.7 + (self.player.skills["Occult Knowledge"] * 0.05)
            self.animations.append(CombatAnimation(start_pos, end_pos, RED))
            if success:
                self.enemy.health -= 20 + weapon_bonus
                self.player.gain_experience(20)
                result = f"You successfully confronted the {self.enemy.name}! The victory feels hollow as you grasp the true nature of existence."
            else:
                self.player.sanity -= 10
                result = f"Confrontation failed. The {self.enemy.name}'s true form is beyond human comprehension."

        if self.enemy.health <= 0:
            self.is_active = False
            result += " The entity dissipates into the aether."
        
        return result

    def update(self):
        completed_animations = []
        for anim in self.animations:
            if anim.update():
                completed_animations.append(anim)
        for anim in completed_animations:
            self.animations.remove(anim)

    def draw(self):
        if self.is_active:
            self.enemy.draw()
            for anim in self.animations:
                anim.draw()

class NPC:
    def __init__(self, name, x, y, dialogue):
        self.name = name
        self.rect = pygame.Rect(x, y, 32, 32)
        self.dialogue = dialogue
        self.image = pygame.Surface((32, 32))
        self.image.fill(PURPLE)

    def draw(self, player):
        screen.blit(self.image, self.rect)
        name = SMALL_FONT.render(self.name, True, WHITE)
        screen.blit(name, (self.rect.x, self.rect.y - 20))
        
        if self.rect.colliderect(player.rect.inflate(50, 50)):
            prompt = SMALL_FONT.render("Click to interact", True, WHITE)
            screen.blit(prompt, (self.rect.x, self.rect.y + 40))

    def get_dialogue(self, player_sanity):
        return self.dialogue[min(key for key in self.dialogue.keys() if key >= player_sanity)]

class DialogueSystem:
    def __init__(self):
        self.active = False
        self.current_dialogue = []
        self.current_index = 0

    def start_dialogue(self, dialogue):
        self.active = True
        self.current_dialogue = dialogue
        self.current_index = 0

    def next_dialogue(self):
        self.current_index += 1
        if self.current_index >= len(self.current_dialogue):
            self.active = False

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, BLACK, (50, HEIGHT - 150, WIDTH - 100, 100))
            pygame.draw.rect(screen, WHITE, (50, HEIGHT - 150, WIDTH - 100, 100), 2)
            text = FONT.render(self.current_dialogue[self.current_index], True, WHITE)
            screen.blit(text, (60, HEIGHT - 140))

class Chest:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.image = chest_img
        self.opened = False

    def draw(self, player):
        screen.blit(self.image, self.rect)
        if not self.opened and self.rect.colliderect(player.rect.inflate(50, 50)):
            prompt = SMALL_FONT.render("Click to open", True, WHITE)
            screen.blit(prompt, (self.rect.x, self.rect.y + 50))

    def open(self):
        if not self.opened:
            self.opened = True
            return random.choice([Weapon("Eldritch Blade", 15), Food("Sanity Potion", 30)])
        return None

class Weapon:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage
        self.image = weapon_img

    def draw(self, x, y):
        screen.blit(self.image, (x, y))

class Food:
    def __init__(self, name, sanity_restore):
        self.name = name
        self.sanity_restore = sanity_restore
        self.image = food_img

    def draw(self, x, y):
        screen.blit(self.image, (x, y))

class CosmicShadows:
    def __init__(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.combat = Combat(self.player)
        self.sanity_drain_rate = 0.001
        self.message = ""
        self.message_timer = 0
        self.npcs = [
            NPC("Old Man", 100, 100, {
                100: ["The stars are aligning...", "Beware the ancient ones!"],
                50: ["The shadows... they're moving!", "Can you hear the whispers?"],
                0: ["The truth! It burns! Make it stop!"]
            }),
            NPC("Scholar", 700, 500, {
                100: ["I've seen things...", "The knowledge comes at a price."],
                50: ["The books... they speak to me now.", "Reality is not what it seems."],
                0: ["The cosmos! The vast, uncaring cosmos!"]
            })
        ]
        self.dialogue_system = DialogueSystem()
        self.chests = [Chest(200, 200), Chest(600, 400)]
        self.combat_chance = 0.001  # Reduced from 0.005 to 0.001 for less frequent combat

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.combat.is_active:
                    if event.button == 1:  # Left click
                        self.message = self.combat.resolve("evade")
                        self.message_timer = 3
                    elif event.button == 3:  # Right click
                        self.message = self.combat.resolve("confront")
                        self.message_timer = 3
                else:
                    if event.button == 1:  # Left click
                        for npc in self.npcs:
                            if npc.rect.collidepoint(event.pos):
                                self.dialogue_system.start_dialogue(npc.get_dialogue(self.player.sanity))
                        for chest in self.chests:
                            if chest.rect.collidepoint(event.pos) and chest.rect.colliderect(self.player.rect.inflate(50, 50)):
                                item = chest.open()
                                if item:
                                    self.player.add_to_inventory(item)
                                    self.message = f"You found a {item.name}!"
                                    self.message_timer = 3
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory()
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    index = event.key - pygame.K_1
                    if index < len(self.player.inventory):
                        self.player.use_item(self.player.inventory[index])
                elif event.key == pygame.K_SPACE:
                    if self.dialogue_system.active:
                        self.dialogue_system.next_dialogue()
        return True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if not self.combat.is_active and not self.dialogue_system.active:
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            self.player.move(dx, dy)

        self.player.sanity -= self.sanity_drain_rate * (1 - (self.player.skills["Mental Fortitude"] * 0.05))
        self.player.sanity = max(0, min(self.player.sanity, self.player.max_sanity))

        if self.player.sanity <= 0:
            print("Your mind shatters as the true nature of reality is revealed.")
            return False

        self.combat.update()

        if self.message_timer > 0:
            self.message_timer -= dt

        
        if random.random() < self.combat_chance and not self.combat.is_active:
            self.combat.start_combat()

        return True

    def draw(self):
        screen.fill(BLACK)
        
        for chest in self.chests:
            chest.draw(self.player)
        
        self.player.draw()
        self.combat.draw()

        for npc in self.npcs:
            npc.draw(self.player)

        # Draw sanity bar
        sanity_color = (int(255 * (1 - self.player.sanity / 100)), int(255 * (self.player.sanity / 100)), 0)
        pygame.draw.rect(screen, sanity_color, (10, 10, self.player.sanity * 2, 20))

        # Draw stats
        stats_text = SMALL_FONT.render(f"Sanity: {int(self.player.sanity)}  XP: {self.player.experience}", True, WHITE)
        screen.blit(stats_text, (WIDTH - stats_text.get_width() - 10, 10))

        # Draw skills
        for i, (skill, level) in enumerate(self.player.skills.items()):
            skill_text = SMALL_FONT.render(f"{skill}: {level}", True, WHITE)
            screen.blit(skill_text, (WIDTH - skill_text.get_width() - 10, 40 + i * 20))

        if self.combat.is_active:
            combat_text = FONT.render(f"A {self.combat.enemy.name} appears! Left click to Evade, Right click to Confront", True, RED)
            screen.blit(combat_text, (WIDTH // 2 - combat_text.get_width() // 2, 50))

        if self.message_timer > 0:
            message_text = SMALL_FONT.render(self.message, True, WHITE)
            screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT - 50))

        self.dialogue_system.draw()

        pygame.display.flip()

    def show_inventory(self):
        inventory_surface = pygame.Surface((WIDTH, HEIGHT))
        inventory_surface.set_alpha(200)
        inventory_surface.fill(BLACK)
        screen.blit(inventory_surface, (0, 0))

        title = FONT.render("Inventory", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for i, item in enumerate(self.player.inventory):
            item_text = SMALL_FONT.render(f"{i+1}. {item.name}", True, WHITE)
            screen.blit(item_text, (WIDTH // 2 - 100, 100 + i * 30))
            item.draw(WIDTH // 2 + 100, 100 + i * 30)

        if self.player.equipped_weapon:
            equipped_text = SMALL_FONT.render(f"Equipped: {self.player.equipped_weapon.name}", True, WHITE)
            screen.blit(equipped_text, (WIDTH // 2 - equipped_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                        waiting = False

def main():
    clock = pygame.time.Clock()
    game = CosmicShadows()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        running = game.handle_events()
        if not game.update(dt):
            running = False
        game.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()