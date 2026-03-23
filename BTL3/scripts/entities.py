import pygame
import random
from scripts.settings import WIDTH, HEIGHT

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, image=None):
        super().__init__()
        self.image = image if image else pygame.Surface((80, 80))
        if not image: self.image.fill((255, 0, 0)) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = speed_x

    def update(self, dt):
        self.rect.x -= self.speed_x * dt
        if self.rect.right < 0:
            self.kill()

class Obstacle(Entity):
    pass

class Collectible(Entity):
    pass

class TunnelPart(Entity):
    def __init__(self, x, y, width, height, speed_x):
        super().__init__(x, y, speed_x)
        self.image = pygame.Surface((width, height))
        self.image.fill((34, 139, 34)) # Forest Green
        
        # AABB collision box
        self.rect = self.image.get_rect(topleft=(x, y))

class ScoreZone(Entity):
    def __init__(self, x, y, width, height, speed_x):
        super().__init__(x, y, speed_x)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Invisible box
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill((255, 255, 0)) 
        self.rect = self.image.get_rect(center=(x, y))
                
        self.velocity_y = 0.0
        self.gravity = 1620.0        
        self.flap_power = -720.0    
        
        self.animation_timer = 0.0
        self.state = "idle" 

    def update(self, dt):
        self.velocity_y += self.gravity * dt
        self.rect.y += self.velocity_y * dt

        self.animation_timer += dt
        if self.velocity_y < 0:
            self.state = "active/flapping"
        else:
            self.state = "idle/falling"

    def flap(self):
        self.velocity_y = self.flap_power

class SpawnerManager:
    def __init__(self, tunnels_group, score_zones_group):
        self.tunnels_group = tunnels_group
        self.score_zones_group = score_zones_group
        self.spawn_timer = 0.0
        
    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= 2.0: 
            self.spawn_timer = 0.0
            self.spawn_tunnel_pair()

    def spawn_tunnel_pair(self):
        gap_size = 280 
        gap_y = random.randint(200, HEIGHT - 200 - gap_size)
        
        x_pos = WIDTH + 100
        speed = 450.0
        
        cap_w, cap_h = 140, 50
        pillar_w, pillar_h = 80, 800
        pillar_offset = (cap_w - pillar_w) // 2

        # Spawn Top Tunnel
        top_pillar = TunnelPart(x_pos + pillar_offset, gap_y - cap_h - pillar_h, pillar_w, pillar_h, speed)
        top_cap = TunnelPart(x_pos, gap_y - cap_h, cap_w, cap_h, speed)
        
        # Spawn Bottom Tunnel
        bottom_cap = TunnelPart(x_pos, gap_y + gap_size, cap_w, cap_h, speed)
        bottom_pillar = TunnelPart(x_pos + pillar_offset, gap_y + gap_size + cap_h, pillar_w, pillar_h, speed)
        
        # Spawn score zone
        score_zone = ScoreZone(x_pos + cap_w, gap_y, 20, gap_size, speed)
        
        self.tunnels_group.add(top_pillar, top_cap, bottom_cap, bottom_pillar)
        self.score_zones_group.add(score_zone)