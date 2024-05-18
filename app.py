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
import random

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
bg_img = pygame.transform.scale(bg_img,(int(bg_img.get_width()*(screen_height/bg_img.get_height())),screen_height))
rep = math.ceil(screen_width/bg_img.get_width())
print(rep)

pygame.display.set_caption("SuperSpeechSaga")

player_image = [pygame.image.load("character/sprite_0.png"),pygame.image.load("character/sprite_1.png")]
player_rect = player_image[0].get_rect()
player_rect.x = 50
player_rect.y = 350
WHITE = (255, 255, 255)
GRAVITY = 4
JUMP_FORCE = -10
font = pygame.font.Font(None, 24)

villager_image = [pygame.image.load("side_character1/sprite_0.png"),pygame.image.load("character/sprite_1.png")]
villager_rect = player_image[0].get_rect()
villager_rect.x = 500
villager_rect.y = 350
villager_text = "Villager 1 says: Hi"
villager_text_surface = font.render(villager_text, True, (255, 255, 255))

villager2_image = [pygame.image.load("side_character1/sprite_1.png")]
villager2_rect = player_image[0].get_rect()
villager2_rect.x = 750
villager2_rect.y = 295
villager2_text = "Villager 2 says: Hi"
villager2_text_surface = font.render(villager2_text, True, (255, 255, 255))

font2 = pygame.font.Font(None, 16)
villager3_image = [pygame.image.load("side_character1/sprite_2.png")]
villager3_rect = player_image[0].get_rect()
villager3_rect.x = 150
villager3_rect.y = 295
villager3_text = "About the game"
villager3_text_surface = font2.render(villager3_text, True, (255, 255, 255))


info_image = [pygame.image.load("assets/info.png"),pygame.image.load("assets/info_complete.png")]
info_image_rect = info_image[0].get_rect()

check_point = pygame.image.load("assets/check_point.png")
check_point_rect = check_point.get_rect()
check_point_rect.x = 1100
check_point_rect.y = 350

# List of prompts for detective interrogation
prompts = [
    "Hello, I'm Detective John. Can you tell me your name and if you witnessed anything suspicious recently?",
    "Could you confirm your role here? Are you one of the maids? We need to gather information about everyone present in the house.",
    "I understand this might be frightening, but did you happen to notice anything out of the ordinary today? Any unfamiliar faces or unusual activities?",
    "You're safe here. I need your cooperation to solve this. Did you see anyone acting suspiciously around the time of the theft?",
    "I assure you, your safety is my priority. I need your help to catch the culprit. Please, don't hesitate to share anything you might know.",
    "You're not alone in this. I'll do everything in my power to protect you. Can you describe anyone who might have been involved in the theft?",
    "I understand you're scared, but remaining silent won't help anyone. Please, trust me and share what you saw. Your testimony could make all the difference.",
    "Your testimony could be the missing piece we need to solve this case. Every detail you provide brings us closer to catching the thief.",
    "I won't let anything happen to you. You're under my protection. Please, tell me if you saw anything that could help us catch the thief.",
    "You're doing great. Just take your time. Can you share any details, no matter how small, that might help us catch the thief?",
    "I understand your fear, but we can't let the thief get away with their crime. Your testimony could make all the difference in bringing them to justice.",
    "I promise to do everything in my power to ensure justice is served. Your cooperation is vital to achieving that. Can you tell me what you saw?",
    "This room is a safe space. You can trust me. Please, share anything you saw, even if you're unsure of its relevance.",
    "I appreciate your bravery in coming forward. Your testimony is invaluable. Can you describe anyone you saw acting suspiciously today?",
    "I'll wait as long as it takes for you to feel comfortable. Whenever you're ready, I'm here to listen to whatever you have to say.",
    "You're not alone in this. We're a team, and together we can bring the culprit to justice. Please, share anything you remember about the theft.",
    "Trust is essential in solving this case. I promise to protect you. Can you tell me if you saw anything that could help us identify the thief?",
    "You're safe here. I won't let anything happen to you. Please, tell me if you saw anything suspicious leading up to the theft.",
    "Your testimony could be the key to solving this case. Every detail you provide brings us closer to catching the thief.",
    "Your safety is my priority. Anything you share with me will be kept confidential. Please, don't hesitate to tell me if you saw anything suspicious.",
    "I understand you're scared, but staying silent won't help us catch the thief. Your testimony could be the breakthrough we need to solve this case.",
    "Trust is essential in solving this case. I promise to protect you. Can you tell me if you saw anything that could help us identify the thief?",
    "We can't solve this case without your help. Please, tell me if you witnessed anything that could help us identify the thief.",
    "I need your help to solve this case. Together, we can ensure the thief is apprehended and the stolen items are recovered. Please, share anything you know.",
    "Your testimony could be the missing piece we need to solve this case. Every detail you provide brings us closer to catching the thief.",
    "I assure you, your safety is my priority. I need your help to catch the culprit. Please, don't hesitate to share anything you might know.",
    "You're not alone in this. We're a team, and together we can bring the culprit to justice. Please, share anything you remember about the theft.",
    "Your testimony could be the key to solving this case. Every detail you provide brings us closer to catching the thief.",
    "I understand your fear, but we can't let the thief get away with their crime. Your testimony could make all the difference in bringing them to justice.",
    "I promise to do everything in my power to ensure justice is served. Your cooperation is vital to achieving that. Can you tell me what you saw?",
    "Trust is essential in solving this case. I promise to protect you. Can you tell me if you saw anything that could help us identify the thief?",
    "You're safe here. I won't let anything happen to you. Please, tell me if you saw anything suspicious leading up to the theft.",
    "Your safety is my priority. Anything you share with me will be kept confidential. Please, don't hesitate to tell me if you saw anything suspicious.",
    "I understand you're scared, but staying silent won't help us catch the thief. Your testimony could be the breakthrough we need to solve this case.",
]

def get_random_prompt():
    return random.choice(prompts)



def perform_speech(prompt, villager):

    global villager_text
    global villager2_text
    global villager3_text
    global e_not_yet_pressed
    global e_not_yet_pressed2

    if villager==0:
        villager_text=f"..."
    elif villager==1:
        villager2_text=f"..."
    elif villager==2:
        villager3_text=f"..."

    try:
        # Gemini
        response = model.generate_content(prompt)
        print(response.text)

        res_text = response.text

        if "json" in res_text:
            res_text = res_text.split("```")[1]
            res_text = res_text.split("json")[1]

        dialog = json.loads(res_text)["dialog"]

        print(dialog)

        if villager==0:
            villager_text=f"Villager 1 says: {dialog}"
        elif villager==1:
            villager2_text=f"Villager 2 says: {dialog}"
        elif villager==2:
            villager3_text=f"Villager 3 says: {dialog}"

        # Pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[villager%2].id)
        print(dialog)
        engine.say(dialog)
        engine.runAndWait()
    except Exception as e:
        traceback.print_exc() 
        if villager==0:
            e_not_yet_pressed = True
        else:
            e_not_yet_pressed = True
    

def fall(player_rect):
    if player_rect.y<350:
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

running = True
walk_count = 0
e_not_yet_pressed = True
e_not_yet_pressed2 = True
while running:
    isWalking = False
    
    fall(player_rect)
    for i in range(0, rep):
        screen.blit(bg_img,(i*bg_img.get_width(),0))
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
        screen.blit(player_image[walk_count%2], player_rect)
        walk_count+=1
    else:
        screen.blit(player_image[0], player_rect)

    ######## Villager 1 ########
    if player_rect.x<550 and player_rect.x>450:
        info_image_rect.x = 510
        info_image_rect.y = 280
        if e_not_yet_pressed:
            screen.blit(info_image[0],info_image_rect)
        else:
            screen.blit(info_image[1],info_image_rect)

        if not e_not_yet_pressed:
            x1,x2,x3 = divide_text(villager_text)
            
            villager_text_surface = font.render(x1, True, (255, 255, 255))
            villager_text_rect = villager_text_surface.get_rect(center=(screen_width // 2, 530))

            villager_text_surface_1 = font.render(x2, True, (255, 255, 255))
            villager_text_rect_1 = villager_text_surface_1.get_rect(center=(screen_width // 2, 550))

            villager_text_surface_2 = font.render(x3, True, (255, 255, 255))
            villager_text_rect_2 = villager_text_surface_2.get_rect(center=(screen_width // 2, 570))

            screen.blit(villager_text_surface, villager_text_rect)
            screen.blit(villager_text_surface_1, villager_text_rect_1)
            screen.blit(villager_text_surface_2, villager_text_rect_2)
        else:
            villager_text_surface = font.render(villager_text, True, (255, 255, 255))
            villager_text_rect = villager_text_surface.get_rect(center=(screen_width // 2, screen_height // 1.1))
            screen.blit(villager_text_surface, villager_text_rect)
        
        if e_not_yet_pressed and keys[pygame.K_e]:
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(128)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio)
                    print(text)

                    prompt = f'''Generate a dialog for game character that speaks in Shakespearean. This character knows location of checkpoint which is on right side of map. Only if a traveller asks about whereabouts of check point then mention character gives direction. Else character will talk about nice weather. If traveller says that he doesn't understand what he is saying then tell him to ask next villager
                    Return the dialog in form of json {{dialog:<Character dialog>}}
                    Traveller says: {text}
                    '''
                    print(prompt)

                    dialog_thread = threading.Thread(target=perform_speech, args=(prompt,0))
                    dialog_thread.start()

                    e_not_yet_pressed = False
                except Exception as e:
                    print(e)
                    print("No audio received")
                    e_not_yet_pressed = True
            
    
    ######## Villager 2 ########
    if player_rect.x<800 and player_rect.x>700:
        info_image_rect.x = 750
        info_image_rect.y = 220
        if e_not_yet_pressed2:
            screen.blit(info_image[0],info_image_rect)
        else:
            screen.blit(info_image[1],info_image_rect)

        if not e_not_yet_pressed2:
            x1,x2,x3 = divide_text(villager2_text)
            
            villager2_text_surface = font.render(x1, True, (255, 255, 255))
            villager2_text_rect = villager2_text_surface.get_rect(center=(screen_width // 2, 530))

            villager2_text_surface_1 = font.render(x2, True, (255, 255, 255))
            villager2_text_rect_1 = villager2_text_surface_1.get_rect(center=(screen_width // 2, 550))

            villager2_text_surface_2 = font.render(x3, True, (255, 255, 255))
            villager2_text_rect_2 = villager2_text_surface_2.get_rect(center=(screen_width // 2, 570))

            screen.blit(villager2_text_surface, villager2_text_rect)
            screen.blit(villager2_text_surface_1, villager2_text_rect_1)
            screen.blit(villager2_text_surface_2, villager2_text_rect_2)
        else:
            villager2_text_surface = font.render(villager2_text, True, (255, 255, 255))
            villager2_text_rect = villager2_text_surface.get_rect(center=(screen_width // 2, screen_height // 1.1))
            
            screen.blit(villager2_text_surface, villager2_text_rect)
        
        if e_not_yet_pressed2 and keys[pygame.K_e]:
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(128)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio)
                    print(text)

                    prompt = f'''Generate a dialog for game character that speaks in GenZ lingo. This character knows location of checkpoint which is on right side of map. Only if a traveller asks about whereabouts of check point then mention character gives direction. Else character will talk about new tech she just discovered. Return the dialog in form of json {{dialog:<Character dialog>}}
                    Traveller says: {text}
                    '''
                    print(prompt)

                    dialog_thread = threading.Thread(target=perform_speech, args=(prompt,1))
                    dialog_thread.start()

                    e_not_yet_pressed2 = False
                except Exception as e:
                    print(e)
                    print("No audio received")
                    e_not_yet_pressed2 = True

    

    ######## Villager 3 ########
    if player_rect.x<200 and player_rect.x>100:
        info_image_rect.x = 150
        info_image_rect.y = 220

        screen.blit(info_image[0],info_image_rect)

        x1,x2,x3 = divide_text(villager3_text)
        
        villager3_text_surface = font2.render(x1, True, (255, 255, 255))
        villager3_text_rect = villager3_text_surface.get_rect(center=(screen_width // 2, 530))

        villager3_text_surface_1 = font2.render(x2, True, (255, 255, 255))
        villager3_text_rect_1 = villager3_text_surface_1.get_rect(center=(screen_width // 2, 550))
        
        villager3_text_surface_2 = font2.render(x3, True, (255, 255, 255))
        villager3_text_rect_2 = villager3_text_surface_2.get_rect(center=(screen_width // 2, 570))

        screen.blit(villager3_text_surface, villager3_text_rect)
        screen.blit(villager3_text_surface_1, villager3_text_rect_1)
        screen.blit(villager3_text_surface_2, villager3_text_rect_2)
        
        if keys[pygame.K_e]:
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(128)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio)
                    print(text)

                    prompt = f'''Generate a dialog for game character. This character tells us information about the game. Currently this is a prototype. The game is platform game in which we play using audio input using mic and move character using keys. The input is taken from the user and output is text and audio. Feels like talking with game character in real life. It tells us that this game generates dialog in realtime using LLM technology. Please keep explaination short and crisp. Return the dialog in form of json {{"dialog":<Character dialog>}}
                    Traveller says: {text}
                    '''
                    print(prompt)

                    dialog_thread = threading.Thread(target=perform_speech, args=(prompt,2))
                    dialog_thread.start()
                except Exception as e:
                    print(e)
                    print("No audio received")

    

    pygame.display.flip()

    pygame.time.Clock().tick(60)


pygame.quit()
sys.exit()
