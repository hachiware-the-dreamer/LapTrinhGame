import pygame
import random

class ParticlePool:
    def __init__(self, feather_count=50, arrow_count=20):
        # Pre-allocate all particles in memory when the game boots
        self.feathers = [FeatherParticle(self) for _ in range(feather_count)]
        self.arrows = [ArrowParticle(self) for _ in range(arrow_count)]

    def spawn_feather(self, x, y, active_group):
        if self.feathers: # Only spawn if we haven't run out of inactive particles!
            p = self.feathers.pop()
            p.reset(x, y)
            active_group.add(p)

    def spawn_arrow(self, x, y, gravity_dir, active_group):
        if self.arrows:
            p = self.arrows.pop()
            p.reset(x, y, gravity_dir)
            active_group.add(p)

    def return_feather(self, particle):
        self.feathers.append(particle)

    def return_arrow(self, particle):
        self.arrows.append(particle)

class FeatherParticle(pygame.sprite.Sprite):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool
        self.image = pygame.Surface((8, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 255, 255, 200), (0, 0, 8, 12)) 
        self.rect = self.image.get_rect()
        self.gravity = 400.0
        self.lifetime = 0.8 

    def reset(self, x, y):
        """Called when popped from the pool to get fresh stats."""
        self.rect.center = (x, y)
        self.vel_x = random.uniform(-100, 100)
        self.vel_y = random.uniform(-150, -50)
        self.age = 0.0
        self.image.set_alpha(255)

    def update(self, dt):
        self.age += dt
        if self.age > self.lifetime:
            self.deactivate()
            return # Skip the rest of the math this frame
            
        self.vel_y += self.gravity * dt
        self.rect.x += self.vel_x * dt
        self.rect.y += self.vel_y * dt
        
        alpha = int(255 * (1 - (self.age / self.lifetime)))
        self.image.set_alpha(max(0, alpha))

    def deactivate(self):
        """Removes from Pygame drawing groups and returns to the pool."""
        self.kill() 
        self.pool.return_feather(self)

class ArrowParticle(pygame.sprite.Sprite):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.lifetime = 0.4 

    def reset(self, x, y, gravity_dir):
        self.rect.center = (x, y)
        self.age = 0.0
        self.image.fill((0, 0, 0, 0)) # Wipe the previous arrow drawing clear
        
        # Redraw the polygon based on the new gravity direction
        if gravity_dir == -1.0: 
            pygame.draw.polygon(self.image, (50, 255, 100, 200), [(15, 0), (30, 20), (20, 20), (20, 40), (10, 40), (10, 20), (0, 20)])
            self.vel_y = -300.0
        else:
            pygame.draw.polygon(self.image, (255, 150, 50, 200), [(10, 0), (20, 0), (20, 20), (30, 20), (15, 40), (0, 20), (10, 20)])
            self.vel_y = 300.0

    def update(self, dt):
        self.age += dt
        if self.age > self.lifetime:
            self.deactivate()
            return
            
        self.rect.y += self.vel_y * dt
        alpha = int(200 * (1 - (self.age / self.lifetime)))
        self.image.set_alpha(max(0, alpha))

    def deactivate(self):
        self.kill()
        self.pool.return_arrow(self)