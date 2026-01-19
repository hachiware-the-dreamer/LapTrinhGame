import pygame
import sys
import pygame.image
import random

pygame.init()

# Screen setup
SCREEN_WIDTH = 875
SCREEN_HEIGHT = 490
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
font = pygame.font.Font("font/Pixeltype.ttf", 50)

# Background
background_surf = pygame.image.load("assets/background.png").convert()
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Zombie
zombie_surf = pygame.image.load("assets/zombie.png").convert_alpha()
zombie_surf = pygame.transform.scale(zombie_surf, (75, 75))
zombie_rect = zombie_surf.get_rect(topleft=(random.randint(50, SCREEN_WIDTH - 125), random.randint(100, SCREEN_HEIGHT - 175)))

# Zombie state
zombie_alpha = 255
zombie_fading = False
zombie_fade_start = 0
FADE_DURATION = 1000  # 1 second in milliseconds

# Scoring
hits = 0
misses = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if zombie_rect.collidepoint(mouse_pos) and not zombie_fading:
                hits += 1
                zombie_fading = True
                zombie_fade_start = pygame.time.get_ticks()
            elif not zombie_fading:
                misses += 1
    
    if zombie_fading:
        elapsed = pygame.time.get_ticks() - zombie_fade_start
        if elapsed < FADE_DURATION:
            zombie_alpha = 255 - int((elapsed / FADE_DURATION) * 255)
        else:
            zombie_rect.topleft = (random.randint(50, SCREEN_WIDTH - 125), random.randint(100, SCREEN_HEIGHT - 175))
            zombie_alpha = 255
            zombie_fading = False
    
    # Draw background
    screen.blit(background_surf, (0, 0))
    
    # Zombie spawner
    zombie_temp = zombie_surf.copy()
    zombie_temp.set_alpha(zombie_alpha)
    screen.blit(zombie_temp, zombie_rect)
    
    # Draw scoring text
    total_clicks = hits + misses
    accuracy = (hits / total_clicks * 100) if total_clicks > 0 else 0
    
    hits_text = font.render(f"Hits: {hits}", False, (0, 0, 0))
    misses_text = font.render(f"Misses: {misses}", False, (0, 0, 0))
    accuracy_text = font.render(f"Accuracy: {accuracy:.1f}%", False, (0, 0, 0))
    
    screen.blit(hits_text, (10, 10))
    screen.blit(misses_text, (10, 40))
    screen.blit(accuracy_text, (10, 70))
    
    pygame.display.update()
    clock.tick(60)