import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

DEFAULT_MAX_MILISECONDS = 2000

def ding(max_miliseconds=DEFAULT_MAX_MILISECONDS):
    asset_path = os.path.join(os.path.dirname(__file__), "assets", "ding.wav")
    pygame.init()
    pygame.mixer.music.load(asset_path)
    pygame.mixer.music.play()
        
    total_miliseconds_waited = 0.0
    wait_time_miliseconds = max_miliseconds // 10
    while pygame.mixer.music.get_busy():
        if max_miliseconds is not None:
            pygame.time.wait(wait_time_miliseconds)
            total_miliseconds_waited += wait_time_miliseconds
            # If the maximum number of second si achieved, break
            if total_miliseconds_waited >= max_miliseconds:
                pygame.mixer.music.stop()
                break
                
    pygame.quit()