import pygame
import random
from config import (
    BOAT_SPAWN_POINTS, BOAT_SIZE, ZOMBIE_SIZE, CREEPER_SIZE, SPIDER_SIZE,
    MOB_ZOMBIE, MOB_CREEPER, MOB_SPIDER,
    FADE_DURATION, HIT_DURATION, SPAWN_ANIMATION_DURATION,
    SPIDER_FALL_SPEED, SPIDER_START_Y, SCREEN_WIDTH
)


class Mob:
    """Base class for all mobs (zombie, creeper, spider)"""
    
    def __init__(self, mob_type, spawn_point, surf):
        self.mob_type = mob_type
        self.surf = surf
        self.spawn_point = spawn_point
        
        # Position
        self.rect = self.surf.get_rect(center=spawn_point)
        
        # State
        self.alpha = 0  # Start invisible for fade-in
        self.spawn_time = pygame.time.get_ticks()
        self.is_spawning = True  # Fade-in animation
        
        self.is_hit = False
        self.hit_time = 0
        
        self.is_fading = False
        self.fade_start = 0
        
        self.is_active = True  # Still in play
        self.should_remove = False  # Mark for removal
        
    def trigger_hit(self):
        """Called when mob is hit by player"""
        self.is_hit = True
        self.is_spawning = False
        self.hit_time = pygame.time.get_ticks()
        
    def start_fading(self):
        """Start fade-out animation (missed)"""
        self.is_fading = True
        self.is_spawning = False
        self.fade_start = pygame.time.get_ticks()
        
    def update(self, current_time, ttl):
        """Update mob state. Returns event string or None."""
        # Spawn animation (fade-in)
        if self.is_spawning:
            elapsed = current_time - self.spawn_time
            if elapsed < SPAWN_ANIMATION_DURATION:
                self.alpha = int((elapsed / SPAWN_ANIMATION_DURATION) * 255)
            else:
                self.alpha = 255
                self.is_spawning = False
            return None
            
        # Hit animation
        if self.is_hit:
            if current_time - self.hit_time >= HIT_DURATION:
                self.should_remove = True
                return "hit_complete"
            return None
            
        # Fade-out animation
        if self.is_fading:
            elapsed = current_time - self.fade_start
            if elapsed < FADE_DURATION:
                self.alpha = 255 - int((elapsed / FADE_DURATION) * 255)
                self.alpha = max(0, self.alpha)
            else:
                self.should_remove = True
                return "fade_complete"
            return None
            
        # Check TTL (time to live)
        time_alive = current_time - self.spawn_time
        if time_alive >= ttl:
            return self.on_timeout()
            
        return None
        
    def on_timeout(self):
        """Called when TTL expires. Override in subclasses."""
        self.start_fading()
        return "miss"
        
    def draw(self, screen):
        """Draw the mob"""
        if self.is_hit:
            # Shake and red tint effect
            temp_surf = self.surf.copy()
            temp_surf.fill((255, 50, 50), special_flags=pygame.BLEND_MULT)
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            screen.blit(temp_surf, (self.rect.x + offset_x, self.rect.y + offset_y))
        else:
            temp_surf = self.surf.copy()
            temp_surf.set_alpha(self.alpha)
            screen.blit(temp_surf, self.rect)


class Zombie(Mob):
    """Standard zombie - spawns at boat, disappears on timeout"""
    
    def __init__(self, spawn_point, surf):
        super().__init__(MOB_ZOMBIE, spawn_point, surf)


class Creeper(Mob):
    """Creeper - spawns at boat, EXPLODES on timeout (game over)"""
    
    def __init__(self, spawn_point, surf):
        super().__init__(MOB_CREEPER, spawn_point, surf)
        self.is_exploding = False
        
    def on_timeout(self):
        """Creeper explodes - game over!"""
        self.is_exploding = True
        self.should_remove = True
        return "explode"  # Signals game over
        
    def draw(self, screen):
        """Draw creeper with flashing effect near timeout"""
        current_time = pygame.time.get_ticks()
        time_alive = current_time - self.spawn_time
        
        if not self.is_hit and not self.is_fading and not self.is_spawning:
            # Flash warning when close to exploding (last 1 second)
            if time_alive > 1500:  # After 1.5 seconds, start flashing
                flash = (current_time // 100) % 2 == 0
                if flash:
                    temp_surf = self.surf.copy()
                    temp_surf.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                    screen.blit(temp_surf, self.rect)
                    return
                    
        super().draw(screen)


class Spider(Mob):
    """Spider - falls from sky, disappears on timeout"""
    
    def __init__(self, surf, screen_width):
        # Random x position, starts above screen
        x = random.randint(50, screen_width - 100)
        spawn_point = (x, SPIDER_START_Y)
        super().__init__(MOB_SPIDER, spawn_point, surf)
        
        self.target_y = random.randint(150, 350)  # Where spider stops falling
        self.is_falling = True
        self.alpha = 255  # Spider is visible immediately
        self.is_spawning = False  # No fade-in, just fall
        
    def update(self, current_time, ttl):
        """Update spider - handle falling"""
        # Falling animation
        if self.is_falling:
            self.rect.y += SPIDER_FALL_SPEED
            if self.rect.centery >= self.target_y:
                self.rect.centery = self.target_y
                self.is_falling = False
                self.spawn_time = current_time  # Reset spawn time when landed
            return None
            
        return super().update(current_time, ttl)
        
    def draw(self, screen):
        """Draw spider with web line while falling"""
        if self.is_falling:
            # Draw web line from top of screen
            pygame.draw.line(
                screen, 
                (200, 200, 200), 
                (self.rect.centerx, 0), 
                (self.rect.centerx, self.rect.top),
                2
            )
        super().draw(screen)


class MobManager:
    """Manages all mobs in the game"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.mobs = []
        self.boats = BOAT_SPAWN_POINTS.copy()
        self.available_boats = list(range(len(self.boats)))
        
        # Load surfaces
        self.zombie_surf = None
        self.creeper_surf = None
        self.spider_surf = None
        self.boat_surf = None
        
        self.last_spawn_time = 0
        
        # Config (set by difficulty)
        self.ttl = 1500
        self.spawn_interval = 1200
        self.max_mobs = 4
        self.creeper_rate = 0.15
        self.spider_rate = 0.2
        
    def load_assets(self):
        """Load mob sprites"""
        self.zombie_surf = pygame.image.load("assets/zombie/zombie.png").convert_alpha()
        self.zombie_surf = pygame.transform.scale(self.zombie_surf, ZOMBIE_SIZE)
        
        self.creeper_surf = pygame.image.load("assets/zombie/creeper.png").convert_alpha()
        self.creeper_surf = pygame.transform.scale(self.creeper_surf, CREEPER_SIZE)
        
        self.spider_surf = pygame.image.load("assets/zombie/spider.png").convert_alpha()
        self.spider_surf = pygame.transform.scale(self.spider_surf, SPIDER_SIZE)
        
        self.boat_surf = pygame.image.load("assets/boat.png").convert_alpha()
        self.boat_surf = pygame.transform.scale(self.boat_surf, BOAT_SIZE)
        
    def set_difficulty(self, config):
        """Set difficulty parameters from config dict"""
        self.ttl = config["ttl"]
        self.spawn_interval = config["spawn_interval"]
        self.max_mobs = config["max_mobs"]
        self.creeper_rate = config["creeper_rate"]
        self.spider_rate = config["spider_rate"]
        
    def reset(self):
        """Reset for new game"""
        self.mobs = []
        self.available_boats = list(range(len(self.boats)))
        self.last_spawn_time = pygame.time.get_ticks()
        
    def spawn_mob(self):
        """Spawn a new mob based on rates"""
        current_time = pygame.time.get_ticks()
        
        # Check spawn interval
        if current_time - self.last_spawn_time < self.spawn_interval:
            return
            
        # Check max mobs
        active_mobs = [m for m in self.mobs if not m.should_remove]
        if len(active_mobs) >= self.max_mobs:
            return
            
        # Determine mob type
        roll = random.random()
        
        if roll < self.spider_rate:
            # Spawn spider (falls from sky)
            mob = Spider(self.spider_surf, self.screen_width)
            self.mobs.append(mob)
        elif roll < self.spider_rate + self.creeper_rate:
            # Spawn creeper at boat
            if self.available_boats:
                boat_idx = random.choice(self.available_boats)
                self.available_boats.remove(boat_idx)
                spawn_point = self.boats[boat_idx]
                mob = Creeper(spawn_point, self.creeper_surf)
                mob.boat_idx = boat_idx
                self.mobs.append(mob)
        else:
            # Spawn zombie at boat
            if self.available_boats:
                boat_idx = random.choice(self.available_boats)
                self.available_boats.remove(boat_idx)
                spawn_point = self.boats[boat_idx]
                mob = Zombie(spawn_point, self.zombie_surf)
                mob.boat_idx = boat_idx
                self.mobs.append(mob)
                
        self.last_spawn_time = current_time
        
    def update(self):
        """Update all mobs. Returns dict of events."""
        current_time = pygame.time.get_ticks()
        events = {"hits": 0, "misses": 0, "explode": False}
        
        # Try to spawn new mob
        self.spawn_mob()
        
        # Update existing mobs
        for mob in self.mobs:
            result = mob.update(current_time, self.ttl)
            
            if result == "miss":
                events["misses"] += 1
            elif result == "explode":
                events["explode"] = True
                
            # Return boat to available pool when mob is removed
            if mob.should_remove and hasattr(mob, 'boat_idx'):
                if mob.boat_idx not in self.available_boats:
                    self.available_boats.append(mob.boat_idx)
                    
        # Remove dead mobs
        self.mobs = [m for m in self.mobs if not m.should_remove]
        
        return events
        
    def check_hit(self, mouse_pos):
        """Check if click hits any mob. Returns mob_type string or None."""
        for mob in self.mobs:
            if (mob.rect.collidepoint(mouse_pos) 
                and not mob.is_fading 
                and not mob.is_hit
                and not mob.is_spawning):
                mob.trigger_hit()
                
                # Return boat to available pool
                if hasattr(mob, 'boat_idx'):
                    if mob.boat_idx not in self.available_boats:
                        self.available_boats.append(mob.boat_idx)
                        
                return mob.mob_type  # Return the type of mob hit
        return None
        
    def draw_boats(self, screen):
        """Draw all boat spawn points"""
        for point in self.boats:
            rect = self.boat_surf.get_rect(center=point)
            screen.blit(self.boat_surf, rect)
            
    def draw_mobs(self, screen):
        """Draw all mobs"""
        for mob in self.mobs:
            mob.draw(screen)
            
    def draw(self, screen):
        """Draw boats and mobs"""
        self.draw_boats(screen)
        self.draw_mobs(screen)
        
    def adjust_for_pause(self, pause_duration):
        """Adjust timers after pause"""
        for mob in self.mobs:
            mob.spawn_time += pause_duration
            if mob.is_hit:
                mob.hit_time += pause_duration
            if mob.is_fading:
                mob.fade_start += pause_duration
        self.last_spawn_time += pause_duration
