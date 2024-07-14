import pygame
import sys
import math
import speech_recognition as sr
import time
import google.generativeai as genai
import json
import pyttsx3
import threading
import traceback
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG, filename='game.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Initialize Pygame
pygame.init()

# Gemini LLM
with open('config_keys.json') as f:
    config = json.load(f)
api_key = config['GOOGLE_API_KEY']
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

screen_width = 1300
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
bg_img = pygame.image.load("background.jpg")
bg_img = pygame.transform.scale(bg_img, (int(bg_img.get_width() * (screen_height / bg_img.get_height())), screen_height))
rep = math.ceil(screen_width / bg_img.get_width())
logging.info(f'Background repetition count: {rep}')

pygame.display.set_caption("SuperSpeechSaga")

player_image = [pygame.image.load("character/sprite_0.png"), pygame.image.load("character/sprite_1.png")]
player_rect = player_image[0].get_rect()
player_rect.x = 50
player_rect.y = 350
WHITE = (255, 255, 255)
GRAVITY = 4
JUMP_FORCE = -10
font = pygame.font.Font(None, 24)

villager_image = [pygame.image.load("side_character1/sprite_0.png"), pygame.image.load("character/sprite_1.png")]
villager_rect = player_image[0].get_rect()
villager_rect.x = 500
villager_rect.y = 350
villager_text = "Villager 1 says: Hi"
villager_text_surface = font.render(villager_text, True, WHITE)

villager2_image = [pygame.image.load("side_character1/sprite_1.png")]
villager2_rect = player_image[0].get_rect()
villager2_rect.x = 750
villager2_rect.y = 295
villager2_text = "Villager 2 says: Hi"
villager2_text_surface = font.render(villager2_text, True, WHITE)

font2 = pygame.font.Font(None, 16)
villager3_image = [pygame.image.load("side_character1/sprite_2.png")]
villager3_rect = player_image[0].get_rect()
villager3_rect.x = 150
villager3_rect.y = 295
villager3_text = "About the game"
villager3_text_surface = font2.render(villager3_text, True, WHITE)

info_image = [pygame.image.load("assets/info.png"), pygame.image.load("assets/info_complete.png")]
info_image_rect = info_image[0].get_rect()

check_point = pygame.image.load("assets/check_point.png")
check_point_rect = check_point.get_rect()
check_point_rect.x = 1100
check_point_rect.y = 350

engine = pyttsx3.init()

def perform_speech(prompt, villager):
    global villager_text, villager2_text, villager3_text, e_not_yet_pressed, e_not_yet_pressed2

    if villager == 0:
        villager_text = f"..."
    elif villager == 1:
        villager2_text = f"..."
    elif villager == 2:
        villager3_text = f"..."

    try:
        # Gemini
        response = model.generate_content(prompt)
        logging.info(f'Response: {response.text}')

        res_text = response.text

        if "json" in res_text:
            res_text = res_text.split("```")[1]
            res_text = res_text.split("json")[1]

        dialog = json.loads(res_text)["dialog"]

        logging.info(f'Dialog: {dialog}')

        if villager == 0:
            villager_text = f"Villager 1 says: {dialog}"
        elif villager == 1:
            villager2_text = f"Villager 2 says: {dialog}"
        elif villager == 2:
            villager3_text = f"Villager 3 says: {dialog}"

        # Pyttsx3
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[villager % 2].id)
        logging.info(dialog)
        engine.say(dialog)
        engine.runAndWait()
    except Exception as e:
        logging.error(traceback.format_exc())
        if villager == 0:
            e_not_yet_pressed = True
        else:
            e_not_yet_pressed = True

def fall(player_rect):
    if player_rect.y < 350:
        player_rect.y += GRAVITY

def divide_text(string):
    words = string.split()
    total_words = len(words)
    
    first_split = total_words // 3
    second_split = first_split * 2
    
    part1 = ' '.join(words[:first_split])
    part2 = ' '.join(words[first_split:second_split])
    part3 = ' '.join(words[second_split:])
    
    return part1, part2, part3

def handle_villager_interaction(villager_num, prompt, e_not_yet_pressed_flag, keys, villager_text, villager_text_surface, villager_text_rect):
    if e_not_yet_pressed_flag and keys[pygame.K_e]:
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            logging.info("Listening...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                logging.info(f'User said: {text}')

                prompt = prompt.format(text=text)
                logging.info(f'Prompt: {prompt}')

                dialog_thread = threading.Thread(target=perform_speech, args=(prompt, villager_num))
                dialog_thread.start()

                return False
            except Exception as e:
                logging.error(e)
                logging.error("No audio received")
                return True
    else:
        x1, x2, x3 = divide_text(villager_text)
        
        villager_text_surface = font.render(x1, True, WHITE)
        villager_text_rect = villager_text_surface.get_rect(center=(screen_width // 2, 530))

        villager_text_surface_1 = font.render(x2, True, WHITE)
        villager_text_rect_1 = villager_text_surface_1.get_rect(center=(screen_width // 2, 550))

        villager_text_surface_2 = font.render(x3, True, WHITE)
        villager_text_rect_2 = villager_text_surface_2.get_rect(center=(screen_width // 2, 570))

        screen.blit(villager_text_surface, villager_text_rect)
        screen.blit(villager_text_surface_1, villager_text_rect_1)
        screen.blit(villager_text_surface_2, villager_text_rect_2)
        
    return e_not_yet_pressed_flag

running = True
walk_count = 0
e_not_yet_pressed = True
e_not_yet_pressed2 = True
while running:
    isWalking = False
    
    fall(player_rect)
    for i in range(0, rep):
        screen.blit(bg_img, (i * bg_img.get_width(), 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    player_speed = 5
    if keys[pygame.K_LEFT]:
        isWalking = True
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        isWalking = True
        player_rect.x += player_speed
    if keys[pygame.K_SPACE]:
        player_rect.y += JUMP_FORCE

    screen.blit(villager_image[0], villager_rect)
    screen.blit(villager2_image[0], villager2_rect)
    screen.blit(villager3_image[0], villager3_rect)

    screen.blit(check_point, check_point_rect)

    if isWalking:
        screen.blit(player_image[walk_count % 2], player_rect)
        walk_count += 1
    else:
        screen.blit(player_image[0], player_rect)

    ######## Villager 1 ########
    if player_rect.x < 550 and player_rect.x > 450:
        info_image_rect.x = 510
        info_image_rect.y = 280
        if e_not_yet_pressed:
            screen.blit(info_image[0], info_image_rect)
        else:
            screen.blit(info_image[1], info_image_rect)

        villager1_prompt = '''Generate a dialog for game character that speaks in Shakespearean. This character knows location of checkpoint which is on right side of map. Only if a traveller asks about whereabouts of check point then mention character gives direction. Else character will talk about nice weather. If traveller says that he doesn't understand what he is saying then tell him to ask next villager
            Return the dialog in form of json {{dialog:<Character dialog>}}
            Traveller says: {text}
            '''
        e_not_yet_pressed = handle_villager_interaction(0, villager1_prompt, e_not_yet_pressed, keys, villager_text, villager_text_surface, info_image_rect)

    ######## Villager 2 ########
    if player_rect.x < 800 and player_rect.x > 700:
        info_image_rect.x = 750
        info_image_rect.y = 220
        if e_not_yet_pressed2:
            screen.blit(info_image[0], info_image_rect)
        else:
            screen.blit(info_image[1], info_image_rect)

        villager2_prompt = '''Generate a dialog for game character that speaks in GenZ lingo. This character knows location of checkpoint which is on right side of map. Only if a traveller asks about whereabouts of check point then mention character gives direction. Else character will talk about new tech she just discovered. Return the dialog in form of json {{dialog:<Character dialog>}}
            Traveller says: {text}
            '''
        e_not_yet_pressed2 = handle_villager_interaction(1, villager2_prompt, e_not_yet_pressed2, keys, villager2_text, villager2_text_surface, info_image_rect)

    ######## Villager 3 ########
    if player_rect.x < 200 and player_rect.x > 100:
        info_image_rect.x = 150
        info_image_rect.y = 220

        screen.blit(info_image[0], info_image_rect)

        x1, x2, x3 = divide_text(villager3_text)
        
        villager3_text_surface = font2.render(x1, True, WHITE)
        villager3_text_rect = villager3_text_surface.get_rect(center=(screen_width // 2, 530))

        villager3_text_surface_1 = font2.render(x2, True, WHITE)
        villager3_text_rect_1 = villager3_text_surface_1.get_rect(center=(screen_width // 2, 550))
        
        villager3_text_surface_2 = font2.render(x3, True, WHITE)
        villager3_text_rect_2 = villager3_text_surface_2.get_rect(center=(screen_width // 2, 570))

        screen.blit(villager3_text_surface, villager3_text_rect)
        screen.blit(villager3_text_surface_1, villager3_text_rect_1)
        screen.blit(villager3_text_surface_2, villager3_text_rect_2)
        
        if keys[pygame.K_e]:
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            pygame.display.flip()

            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                logging.info("Listening...")
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio)
                    logging.info(f'User said: {text}')

                    prompt = '''Generate a dialog for game character. This character tells us information about the game. Currently this is a prototype. The game is platform game in which we play using audio input using mic and move character using keys. The input is taken from the user and output is text and audio. Feels like talking with game character in real life. It tells us that this game generates dialog in realtime using LLM technology. Please keep explanation short and crisp. Return the dialog in form of json {{"dialog":<Character dialog>}}
                    Traveller says: {text}
                    '''
                    logging.info(f'Prompt: {prompt}')

                    dialog_thread = threading.Thread(target=perform_speech, args=(prompt, 2))
                    dialog_thread.start()
                except Exception as e:
                    logging.error(e)
                    logging.error("No audio received")

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
