import os
import sys
import pygame


class _ParallaxLayer:
    __slots__ = ("image", "speed", "offset_x", "width", "draw_y")

    def __init__(self, image, speed, screen_height):
        self.image = image
        self.speed = float(speed)  # Pixels per second
        self.offset_x = 0.0
        self.width = image.get_width()
        self.draw_y = screen_height - image.get_height()

    def update(self, dt):
        # Move left over time; wrap by one image width for seamless tiling.
        self.offset_x = (self.offset_x + self.speed * dt) % self.width

    def draw(self, surface):
        x0 = -int(self.offset_x)
        surface.blit(self.image, (x0, self.draw_y))
        surface.blit(self.image, (x0 + self.width, self.draw_y))


class ParallaxBackground:
    BASE_PATH = os.path.join("assets", "backgrounds", "bg1", "parts")

    # Required layers from the assignment brief.
    LAYER_FILES = (
        "landscape_0004_5_clouds.png",   # Slowest
        "landscape_0003_4_mountain.png", # Medium
        "landscape_0000_1_trees.png",    # Fastest
    )

    # Speeds in pixels / second (leftward movement).
    LAYER_SPEEDS = (25.0, 45.0, 90.0)

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = int(screen_width)
        self.screen_height = int(screen_height)
        self.sky_color = (198, 204, 212)
        self.layers = []

        for filename, speed in zip(self.LAYER_FILES, self.LAYER_SPEEDS):
            image = self._load_layer_image(filename)
            image = self._scale_to_screen_height(image)
            self.layers.append(_ParallaxLayer(image, speed, self.screen_height))

    def _load_layer_image(self, filename):
        path = os.path.join(self.BASE_PATH, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            raise FileNotFoundError(f"Could not load background layer: {path}") from exc

    def _scale_to_screen_height(self, image):
        if image.get_height() == self.screen_height:
            return image

        scale = self.screen_height / float(image.get_height())
        target_width = max(1, int(image.get_width() * scale))
        return pygame.transform.smoothscale(image, (target_width, self.screen_height))

    def update(self, dt):
        for layer in self.layers:
            layer.update(dt)

    def draw(self, surface):
        # Fill the full screen first, then draw transparent parallax layers.
        surface.fill(self.sky_color)
        for layer in self.layers:
            layer.draw(surface)


class _SeaScrollLayer:
    __slots__ = ("image", "speed", "offset_x", "width")

    def __init__(self, image, speed):
        self.image = image
        self.speed = float(speed)
        self.offset_x = 0.0
        self.width = image.get_width()

    def update(self, dt):
        self.offset_x = (self.offset_x + self.speed * dt) % self.width

    def draw(self, surface):
        x0 = -int(self.offset_x)
        # Draw exactly twice side-by-side for seamless horizontal looping.
        surface.blit(self.image, (x0, 0))
        surface.blit(self.image, (x0 + self.width, 0))


class ParallaxSeaView:
    BASE_PATH = os.path.join("assets", "backgrounds", "bg2")

    # Required files from the assignment brief.
    SKY_FILE = "seaview_sky.png"
    CLOUDS_FILE = "seaview_clouds.png"       # Slowest
    SEA_FILE = "seaview_sea.png"             # Medium
    FOREGROUND_FILE = "seaview_foreground.png"  # Fastest

    # Pixels / second, ordered by depth.
    SPEED_CLOUDS = 18.0
    SPEED_SEA = 35.0
    SPEED_FOREGROUND = 72.0

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = int(screen_width)
        self.screen_height = int(screen_height)

        sky = self._load_image(self.SKY_FILE)
        clouds = self._load_image(self.CLOUDS_FILE)
        sea = self._load_image(self.SEA_FILE)
        foreground = self._load_image(self.FOREGROUND_FILE)

        # Keep a single target size so layers line up perfectly on the screen.
        target_size = (self.screen_width, self.screen_height)
        self.sky = pygame.transform.smoothscale(sky, target_size)
        clouds_scaled = pygame.transform.smoothscale(clouds, target_size)
        sea_scaled = pygame.transform.smoothscale(sea, target_size)
        foreground_scaled = pygame.transform.smoothscale(foreground, target_size)

        self.clouds_layer = _SeaScrollLayer(clouds_scaled, self.SPEED_CLOUDS)
        self.sea_layer = _SeaScrollLayer(sea_scaled, self.SPEED_SEA)
        self.foreground_layer = _SeaScrollLayer(foreground_scaled, self.SPEED_FOREGROUND)

    def _load_image(self, filename):
        path = os.path.join(self.BASE_PATH, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            raise FileNotFoundError(f"Could not load background image: {path}") from exc

    def update(self, dt):
        # deltaTime-based movement for stable speed across frame rates.
        self.clouds_layer.update(dt)
        self.sea_layer.update(dt)
        self.foreground_layer.update(dt)

    def draw(self, surface):
        # Painter's Algorithm order:
        # 1) static sky, 2) clouds, 3) sea, 4) foreground
        surface.blit(self.sky, (0, 0))
        self.clouds_layer.draw(surface)
        self.sea_layer.draw(surface)
        self.foreground_layer.draw(surface)


class ParallaxForest:
    BASE_PATH = os.path.join("assets", "backgrounds", "bg3")

    SKY_FILE = "forest_background_sky.png"
    CLOUDS_FILE = "forest_background_clouds.png"               # Slowest
    MOUNTAINS_FILE = "forest_background_mountains_2.png"       # Medium
    TREES_FILE = "forest_background_trees.png"                 # Fastest

    SPEED_CLOUDS = 16.0
    SPEED_MOUNTAINS = 34.0
    SPEED_TREES = 78.0

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = int(screen_width)
        self.screen_height = int(screen_height)

        sky = self._load_image(self.SKY_FILE)
        clouds = self._load_image(self.CLOUDS_FILE)
        mountains = self._load_image(self.MOUNTAINS_FILE)
        trees = self._load_image(self.TREES_FILE)

        target_size = (self.screen_width, self.screen_height)
        self.sky = pygame.transform.smoothscale(sky, target_size)
        clouds_scaled = pygame.transform.smoothscale(clouds, target_size)
        mountains_scaled = pygame.transform.smoothscale(mountains, target_size)
        trees_scaled = pygame.transform.smoothscale(trees, target_size)

        self.clouds_layer = _SeaScrollLayer(clouds_scaled, self.SPEED_CLOUDS)
        self.mountains_layer = _SeaScrollLayer(mountains_scaled, self.SPEED_MOUNTAINS)
        self.trees_layer = _SeaScrollLayer(trees_scaled, self.SPEED_TREES)

    def _load_image(self, filename):
        path = os.path.join(self.BASE_PATH, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            raise FileNotFoundError(f"Could not load background image: {path}") from exc

    def update(self, dt):
        self.clouds_layer.update(dt)
        self.mountains_layer.update(dt)
        self.trees_layer.update(dt)

    def draw(self, surface):
        # Painter's Algorithm order:
        # 1) static sky, 2) clouds, 3) mountains, 4) trees
        surface.blit(self.sky, (0, 0))
        self.clouds_layer.draw(surface)
        self.mountains_layer.draw(surface)
        self.trees_layer.draw(surface)


if __name__ == "__main__":
    # Standalone sample loop showing deltaTime usage at 60 FPS.
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Parallax SeaView Demo")
    clock = pygame.time.Clock()

    # Swap to ParallaxBackground(width, height) if you want to test bg1.
    background = ParallaxSeaView(width, height)

    running = True
    while running:
        # dt is in seconds; movement remains stable across machines.
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        background.update(dt)

        # Draw
        background.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()