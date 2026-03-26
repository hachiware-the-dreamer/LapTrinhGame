import pygame
import random

class FeatherParticle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 255, 255, 200), (0, 0, 8, 12)) 
        self.rect = self.image.get_rect(center=(x, y))
        
        self.vel_x = random.uniform(-100, 100)
        self.vel_y = random.uniform(-150, -50)
        self.gravity = 400.0
        
        self.lifetime = 0.8 
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        if self.age > self.lifetime:
            self.kill()
            
        self.vel_y += self.gravity * dt
        self.rect.x += self.vel_x * dt
        self.rect.y += self.vel_y * dt
        
        alpha = int(255 * (1 - (self.age / self.lifetime)))
        self.image.set_alpha(max(0, alpha))

class ArrowParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, gravity_dir):
        super().__init__()
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        
        if gravity_dir == -1.0: 
            pygame.draw.polygon(self.image, (50, 255, 100, 200), [(15, 0), (30, 20), (20, 20), (20, 40), (10, 40), (10, 20), (0, 20)])
            self.vel_y = -300.0
        else:
            pygame.draw.polygon(self.image, (255, 150, 50, 200), [(10, 0), (20, 0), (20, 20), (30, 20), (15, 40), (0, 20), (10, 20)])
            self.vel_y = 300.0
            
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 0.4 
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        if self.age > self.lifetime:
            self.kill()
            
        self.rect.y += self.vel_y * dt
        
        alpha = int(200 * (1 - (self.age / self.lifetime)))
        self.image.set_alpha(max(0, alpha))