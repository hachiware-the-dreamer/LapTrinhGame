import pygame
import os
import math


class CoinAnimation:
    def __init__(self, folder_path, size=(48, 48)):
        self.frames = []
        self.size = size
        if os.path.exists(folder_path):
            files = sorted(os.listdir(folder_path))
            for filename in files:
                if filename.endswith(".png"):
                    img = pygame.image.load(
                        os.path.join(folder_path, filename)
                    ).convert_alpha()
                    img = pygame.transform.scale(img, self.size)
                    self.frames.append(img)

        self.length = len(self.frames)
        self.index = 0
        self.timer = 0.0
        self.fps = 12
        self.rotation_angle = 0.0  # Used for single-frame rotation fallback

    def update(self, dt):
        if self.length > 1:
            self.timer += dt
            if self.timer >= 1.0 / self.fps:
                self.timer = 0.0
                self.index = (self.index + 1) % self.length
        else:
            # Fallback for single frame: rotate by scaling width
            self.rotation_angle += 5.0 * dt  # Radians per second roughly

    def get_image(self):
        if self.length == 0:
            # Placeholder if no frames found
            surf = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 215, 0), (24, 24), 20)
            return surf

        if self.length > 1:
            return self.frames[self.index]
        else:
            # Single frame rotation effect (squash/stretch width)
            base_img = self.frames[0]
            width = base_img.get_width()
            height = base_img.get_height()

            # Use sine to oscillate width between -width and +width
            scale_factor = math.sin(self.rotation_angle * 2.0)
            scaled_w = max(1, int(abs(scale_factor) * width))

            # If scale_factor is negative, we could flip it, but for a coin it doesn't matter much
            scaled_img = pygame.transform.scale(base_img, (scaled_w, height))

            # Center it back on a surface of original size to avoid jitter
            final_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            x_offset = (width - scaled_w) // 2
            final_surf.blit(scaled_img, (x_offset, 0))
            return final_surf
