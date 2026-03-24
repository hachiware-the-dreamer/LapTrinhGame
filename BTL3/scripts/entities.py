import pygame
import random
from scripts.settings import WIDTH, HEIGHT


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, image=None):
        super().__init__()
        self.image = image if image else pygame.Surface((80, 80))
        if not image:
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = speed_x

    def update(self, dt):
        self.rect.x -= self.speed_x * dt
        if self.rect.right < 0:
            self.kill()


class Obstacle(Entity):
    pass


from scripts.coin_anim import CoinAnimation


class Collectible(Entity):
    def __init__(self, x, y, speed_x, size=(48, 48), points=1):
        super().__init__(x, y, speed_x)
        self.points = points
        self.anim = CoinAnimation("assets/sprites/coin", size=size)
        self.image = self.anim.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        super().update(dt)
        self.anim.update(dt)
        self.image = self.anim.get_image()


class SmallCoin(Collectible):
    def __init__(self, x, y, speed_x):
        # Small coin: size 32x32, gives 2 points
        super().__init__(x, y, speed_x, size=(32, 32), points=2)


class BigCoin(Collectible):
    def __init__(self, x, y, speed_x):
        # Big coin: size 64x64, gives 5 points
        super().__init__(x, y, speed_x, size=(64, 64), points=5)


class TunnelPart(Entity):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        speed_x,
        base_image=None,
        is_cap=False,
        point_down=False,
        overlap=0,
    ):
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
                            current_y -= scaled_h - overlap
                    else:
                        # Tile Top-Down (so it connects cleanly to the bottom cap)
                        current_y = 0
                        while current_y < height:
                            self.image.blit(scaled_img, (0, current_y))
                            current_y += scaled_h - overlap
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((34, 139, 34))

        self.rect = self.image.get_rect(topleft=(x, y))


class ScoreZone(Entity):
    def __init__(self, x, y, width, height, speed_x):
        super().__init__(x, y, speed_x)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Invisible box
        self.rect = self.image.get_rect(topleft=(x, y))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game_mode):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))

        self.game_mode = game_mode

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
            if self.velocity_y > 550.0:
                self.velocity_y = 550.0
            if self.velocity_y < -550.0:
                self.velocity_y = -550.0
        else:  # Flappy
            self.velocity_y += self.flappy_gravity * dt

        self.rect.y += self.velocity_y * dt

        self.animation_timer += dt
        if self.velocity_y < 0:
            self.state = "active/flapping"
        else:
            self.state = "idle/falling"

    def flap(self, game):
        if self.game_mode == "Swing":
            self.gravity_dir *= -1.0
            game.play_sfx(game.sfx_swing)
        else: # Flappy
            self.velocity_y = self.flap_power
            game.play_sfx(game.sfx_flap)



class SpawnerManager:
    def __init__(
        self,
        tunnels_group,
        score_zones_group,
        collectibles_group,
        start_gap,
        min_gap,
        shrink_rate,
    ):
        self.tunnels_group = tunnels_group
        self.score_zones_group = score_zones_group
        self.collectibles_group = collectibles_group
        self.spawn_timer = 0.0

        # Difficulty scaling settings
        self.current_gap_size = start_gap
        self.min_gap_size = min_gap
        self.gap_shrink_rate = shrink_rate

        self.tunnels_spawned = 0

        # Mixi food jar
        try:
            raw_img = pygame.image.load("assets/sprites/tunnel.png").convert_alpha()

            # 1. Find the smallest box that contains the actual visible pixels
            bbox = raw_img.get_bounding_rect()

            # 2. Create a new, perfectly cropped image using that box
            self.tunnel_img = raw_img.subsurface(bbox).copy()

        except pygame.error:
            print("Warning: Could not load assets/sprites/tunnel.png")
            self.tunnel_img = None

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= 2.0:
            self.spawn_timer = 0.0
            self.spawn_tunnel_pair()

    def spawn_tunnel_pair(self):
        gap_size = int(self.current_gap_size)
        gap_y = random.randint(200, HEIGHT - 200 - gap_size)

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
            gap_y - cap_h - pillar_h + connection_sink,  # Shifted Down
            pillar_w,
            pillar_h,
            speed,
            self.tunnel_img,
            is_cap=False,
            point_down=True,
            overlap=overlap_amount,
        )
        top_cap = TunnelPart(
            x_pos, gap_y - cap_h, cap_w, cap_h, speed, self.tunnel_img, is_cap=True
        )

        # --- SPAWN BOTTOM TUNNEL ---
        bottom_cap = TunnelPart(
            x_pos, gap_y + gap_size, cap_w, cap_h, speed, self.tunnel_img, is_cap=True
        )
        bottom_pillar = TunnelPart(
            x_pos + pillar_offset,
            gap_y + gap_size + cap_h - connection_sink,  # Shifted Up
            pillar_w,
            pillar_h,
            speed,
            self.tunnel_img,
            is_cap=False,
            point_down=False,
            overlap=overlap_amount,
        )

        score_zone = ScoreZone(x_pos + cap_w, gap_y, 20, gap_size, speed)

        # Add pillars FIRST so the caps draw on top of them and hide the seams
        self.tunnels_group.add(top_pillar, bottom_pillar, top_cap, bottom_cap)
        self.score_zones_group.add(score_zone)

        self.tunnels_spawned += 1
        if self.tunnels_spawned > 3:
            if self.current_gap_size > self.min_gap_size:
                self.current_gap_size -= self.gap_shrink_rate

        # --- SPAWN COINS ---
        # 60% SmallCoin (2 points), 20% BigCoin (5 points), 20% None
        rand_val = random.random()
        if rand_val < 0.8:
            if rand_val < 0.2:  # Big Coin (increased from 0.1)
                side = random.choice(["top", "bottom"])
                if side == "top":
                    # Gap is from gap_y to gap_y + gap_size
                    # top_cap is at gap_y - cap_h
                    # Place it just below the top cap (hard position)
                    coin_y = gap_y + 10 
                else:
                    # Place it just above the bottom cap (hard position)
                    coin_y = gap_y + gap_size - 74 
                coin = BigCoin(x_pos + cap_w + 10, coin_y, speed)
            else:  # Small Coin
                coin_y = gap_y + random.randint(30, gap_size - 62)
                coin = SmallCoin(x_pos + cap_w + 30, coin_y, speed)
            self.collectibles_group.add(coin)
