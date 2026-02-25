import pygame
import random
import math


class Target:
    """A circular target with concentric red and white rings"""
    
    def __init__(self, screen_width, screen_height, radius, ttl, min_y=0):
        """
        Initialize a target
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            radius: Outer radius of the target
            ttl: Time-to-live in milliseconds
            min_y: Minimum y-coordinate for spawning (to avoid HUD area)
        """
        self.radius = radius
        self.ttl = ttl
        
        # Random position using formula: r < x < (Width - r) and min_y + r < y < (Height - r)
        self.x = random.randint(radius, screen_width - radius)
        self.y = random.randint(max(radius, min_y + radius), screen_height - radius)
        
        # Timing
        self.spawn_time = pygame.time.get_ticks()
        self.alive = True
        
        # Animation
        self.spawn_scale = 0.0
        self.spawn_duration = 200  # ms
        
    def update(self):
        """Update target state and check if expired"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.spawn_time
        
        # Update spawn animation
        if elapsed < self.spawn_duration:
            self.spawn_scale = elapsed / self.spawn_duration
        else:
            self.spawn_scale = 1.0
        
        if elapsed >= self.ttl:
            self.alive = False # Check if TTL expired
            
    def draw(self, surface):
        """Draw the target with concentric circles"""
        if not self.alive:
            return
            
        # Apply spawn animation scale
        current_radius = int(self.radius * self.spawn_scale)
        
        if current_radius < 5:
            return
        
        # Draw concentric circles (from outside to inside)
        pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), current_radius)
        
        white_radius = int(current_radius * 0.8)
        if white_radius > 0:
            pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), white_radius)
        
        red2_radius = int(current_radius * 0.6)
        if red2_radius > 0:
            pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), red2_radius)
        
        white2_radius = int(current_radius * 0.4)
        if white2_radius > 0:
            pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), white2_radius)
        
        center_radius = int(current_radius * 0.2)
        if center_radius > 0:
            pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), center_radius)
    
    def check_hit(self, mouse_pos):
        """
        Check if mouse position hits the target
        
        Returns:
            bool: True if hit, False otherwise
        """
        if not self.alive or self.spawn_scale < 1.0:
            return False
            
        # Calculate distance from center
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= self.radius
    
    def get_reaction_time(self):
        """
        Get the reaction time (time since spawn) in milliseconds
        
        Returns:
            int: Reaction time in ms
        """
        return pygame.time.get_ticks() - self.spawn_time
