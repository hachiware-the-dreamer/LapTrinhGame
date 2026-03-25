import pygame
import random
from scripts.settings import WIDTH, HEIGHT
from scripts.coin_anim import CoinAnimation

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
    def __init__(self, x, y, speed_x, size=(48, 48), points=1):
        super().__init__(x, y, speed_x)
        self.points = points
        self.anim = CoinAnimation("assets/sprites/coin/1.png", size=size)
        self.image = self.anim.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        super().update(dt)
        self.anim.update(dt)
        self.image = self.anim.get_image()


class SmallCoin(Collectible):
    def __init__(self, x, y, speed_x):
        super().__init__(x, y, speed_x, size=(48, 48), points=2)


class BigCoin(Collectible):
    def __init__(self, x, y, speed_x):
        super().__init__(x, y, speed_x, size=(88, 88), points=5)

class TunnelPart(Entity):
    def __init__(self, x, y, width, height, speed_x, base_image=None, is_cap=False, point_down=False, overlap=0):
        super().__init__(x, y, speed_x)
        
        if base_image:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if is_cap:
                # Caps are rotated sideways and stretched to fit exactly
                img_to_scale = pygame.transform.rotate(base_image, 90)
                scaled_img = pygame.transform.scale(img_to_scale, (width, height))
                self.image.blit(scaled_img, (0, 0))
            else:
                img_to_scale = base_image
                if point_down:
                    # Rotate 180 degrees so the jar hangs upside down
                    img_to_scale = pygame.transform.rotate(base_image, 180)

                ratio = width / img_to_scale.get_width()
                scaled_h = int(img_to_scale.get_height() * ratio)
                
                if scaled_h > 0:
                    scaled_img = pygame.transform.scale(img_to_scale, (width, scaled_h))
                    
                    if point_down:
                        # Tile Bottom-Up (so it connects cleanly to the top cap)
                        current_y = height - scaled_h
                        while current_y > -scaled_h:
                            self.image.blit(scaled_img, (0, current_y))
                            current_y -= (scaled_h - overlap)
                    else:
                        # Tile Top-Down (so it connects cleanly to the bottom cap)
                        current_y = 0
                        while current_y < height:
                            self.image.blit(scaled_img, (0, current_y))
                            current_y += (scaled_h - overlap)
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((34, 139, 34)) 
            
        self.rect = self.image.get_rect(topleft=(x, y))

class ScoreZone(Entity):
    def __init__(self, x, y, width, height, speed_x):
        super().__init__(x, y, speed_x)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Invisible box
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game_mode, char_idx=0):
        super().__init__()
        
        self.game_mode = game_mode
        self.char_idx = char_idx
        
        # Determine the image path based on the selected character index
        if self.char_idx == 0:
            img_path = "assets/sprites/bird1.png"
        elif self.char_idx == 1:
            img_path = "assets/sprites/bird2.png"
        else: # self.char_idx == 2
            img_path = "assets/sprites/helicopter.png"
            
        try:
            # Load the image and scale it if necessary
            raw_img = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(raw_img, (60, 45)) # Adjust size as needed
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load {img_path}. Using placeholder.")
            self.image = pygame.Surface((60, 60))
            if self.char_idx == 0:
                self.image.fill((255, 255, 0)) # Yellow for Bird 1
            elif self.char_idx == 1:
                self.image.fill((255, 0, 0))   # Red for Bird 2
            else:
                self.image.fill((0, 0, 255))   # Blue for Helicopter
                
        self.rect = self.image.get_rect(center=(x, y))
        
        self.velocity_y = 0.0
        
        # --- PHYSICS TUNING ---
        # Flappy mode uses normal gravity and impulse flapping
        self.flappy_gravity = 1620.0        
        self.flap_power = -600.0    
        
        # Swing mode uses extreme gravity for tight, smooth turnarounds without snapping
        self.swing_gravity = 1800.0
        self.gravity_dir = 1.0       
        
        self.animation_timer = 0.0
        self.state = "idle" 

    def update(self, dt):
        if self.game_mode == "Swing":
            self.velocity_y += (self.swing_gravity * self.gravity_dir) * dt
            
            # Capped terminal velocity -> won't break the sound barrier
            if self.velocity_y > 550.0: self.velocity_y = 550.0
            if self.velocity_y < -550.0: self.velocity_y = -550.0
        else: # Flappy
            self.velocity_y += self.flappy_gravity * dt

        self.rect.y += self.velocity_y * dt

        self.animation_timer += dt
        if self.velocity_y < 0:
            self.state = "active/flapping"
        else:
            self.state = "idle/falling"

    def flap(self):
        if self.game_mode == "Swing":
            self.gravity_dir *= -1.0
        else: # Flappy
            self.velocity_y = self.flap_power

class SpawnerManager:
    def __init__(self, tunnels_group, score_zones_group, collectibles_group, start_gap, min_gap, shrink_rate):
        self.tunnels_group = tunnels_group
        self.score_zones_group = score_zones_group
        self.collectibles_group = collectibles_group
        self.spawn_timer = 0.0
        
        # Difficulty scaling settings
        self.current_gap_size = start_gap
        self.min_gap_size = min_gap
        self.gap_shrink_rate = shrink_rate
        
        self.tunnels_spawned = 0
        
        # Pre-calculate the upcoming tunnel to safely interpolate coin spawns ahead of time
        self.next_gap_size = int(start_gap)
        self.next_gap_y = random.randint(200, HEIGHT - 200 - self.next_gap_size)

        # Mixi food jar
        try:
            raw_img = pygame.image.load("assets/obstacles/Aile_0040.png").convert_alpha()
            
            # 1. Find the smallest box that contains the actual visible pixels
            bbox = raw_img.get_bounding_rect() 
            
            # 2. Create a new, perfectly cropped image using that box
            self.tunnel_img = raw_img.subsurface(bbox).copy()
            
        except pygame.error:
            print("Warning: Could not load assets/obstacles/Aile_0040.png")
            self.tunnel_img = None
        
    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= 2.0: 
            self.spawn_timer = 0.0
            self.spawn_tunnel_pair()

    def spawn_tunnel_pair(self):
        # Uses the pre-calculated gap for coin spawning
        gap_size = self.next_gap_size
        gap_y = self.next_gap_y
        
        x_pos = WIDTH + 100
        speed = 450.0
        
        cap_w, cap_h = 140, 50
        pillar_w, pillar_h = 80, 800
        pillar_offset = (cap_w - pillar_w) // 2
        
        overlap_amount = 36 
        
        # This forces the vertical pipes to sink 20px inside the caps to hide any gaps!
        connection_sink = 30

        # --- SPAWN TOP TUNNEL ---
        top_pillar = TunnelPart(
            x_pos + pillar_offset, 
            gap_y - cap_h - pillar_h + connection_sink, # Shifted Down
            pillar_w, pillar_h, speed, self.tunnel_img, 
            is_cap=False, point_down=True, overlap=overlap_amount
        )
        top_cap = TunnelPart(
            x_pos, gap_y - cap_h, 
            cap_w, cap_h, speed, self.tunnel_img, 
            is_cap=True
        )
        
        # --- SPAWN BOTTOM TUNNEL ---
        bottom_cap = TunnelPart(
            x_pos, gap_y + gap_size, 
            cap_w, cap_h, speed, self.tunnel_img, 
            is_cap=True
        )
        bottom_pillar = TunnelPart(
            x_pos + pillar_offset, 
            gap_y + gap_size + cap_h - connection_sink, # Shifted Up
            pillar_w, pillar_h, speed, self.tunnel_img, 
            is_cap=False, point_down=False, overlap=overlap_amount
        )
        
        score_zone = ScoreZone(x_pos + cap_w, gap_y, 20, gap_size, speed)
        
        # Add pillars FIRST so the caps draw on top of them and hide the seams
        self.tunnels_group.add(top_pillar, bottom_pillar, top_cap, bottom_cap)
        self.score_zones_group.add(score_zone)
        
        self.tunnels_spawned += 1
        if self.tunnels_spawned > 3: 
            if self.current_gap_size > self.min_gap_size:
                self.current_gap_size -= self.gap_shrink_rate

        # Pre-calculate the next tunnel to predict the coin spawn path
        future_gap_size = int(self.current_gap_size)
        future_gap_y = random.randint(200, HEIGHT - 200 - future_gap_size)

        # Spawn coins based on the path from current tunnel to next future tunnel
        self.spawn_coins_between_tunnels(gap_y, gap_size, future_gap_y, future_gap_size, x_pos, speed)
        
        # Store future tunnel as the 'next' tunnel for when this function fires again
        self.next_gap_size = future_gap_size
        self.next_gap_y = future_gap_y

    def spawn_coins_between_tunnels(self, curr_gap_y, curr_gap_size, next_gap_y, next_gap_size, curr_tunnel_x, speed):
        """
        Spawns coins horizontally between the current tunnel and the next upcoming one.
        The Y position is strictly constrained between their gaps.
        """
        distance_between_tunnels = 2.0 * speed
        coin_x = curr_tunnel_x + (distance_between_tunnels * 0.65)

        # 60% small coin, 20% big coin, 20% none.
        rand_val = random.random()
        if rand_val < 0.8:
            curr_center = curr_gap_y + (curr_gap_size // 2)
            next_center = next_gap_y + (next_gap_size // 2)

            # Calculate the height difference between the gaps
            center_diff = abs(curr_center - next_center)
            
            if center_diff < 120:
                # Gaps are nearly at the same height -> Force coin significantly higher or lower
                offset = random.randint(120, 250)
                direction = random.choice([-1, 1])
                coin_y = curr_center + (offset * direction)
            else:
                # Gaps naturally force movement -> Spawn proportionally bounded between them.
                min_y = min(curr_center, next_center)
                max_y = max(curr_center, next_center)
                
                # Larger buffer for big coins, smaller for standard coins.
                buffer = 60 if rand_val < 0.2 else 30
                min_y -= buffer
                max_y += buffer
                
                coin_y = random.randint(int(min_y), int(max_y))
            
            # Keep safely within accessible screen bounds
            coin_y = max(100, min(HEIGHT - 100, int(coin_y)))
            
            if rand_val < 0.2:
                coin = BigCoin(coin_x, coin_y, speed)
            else:
                coin = SmallCoin(coin_x, coin_y, speed)

            if self.collectibles_group is not None:
                self.collectibles_group.add(coin)