import pygame

class SpriteSheetManager:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet {filename}: {e}")
            self.sheet = None

    def get_image(self, x, y, width, height):
        if not self.sheet:
            image = pygame.Surface((width, height))
            image.fill((255, 0, 255))
            return image
            
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image


class UIButton:
    def __init__(self, x, y, width, height, text, callback, font_size=64):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        
        self.font = pygame.font.SysFont(None, font_size)
        self.color_normal = (100, 100, 100)
        self.color_hover = (150, 150, 150)
        self.color_active = (50, 150, 50)
        self.color_text = (255, 255, 255)
        
        self.is_hovered = False
        self.is_active = False

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered and self.callback:
                    self.callback()

    def draw(self, surface):
        # Prioritize the active green color, then hover, then normal
        if self.is_active:
            current_color = self.color_active
        else:
            current_color = self.color_hover if self.is_hovered else self.color_normal
            
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        
        text_surf = self.font.render(self.text, True, self.color_text)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class UISlider:
    def __init__(self, x, y, width, height, min_val, max_val, start_val, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.text = text
        
        self.font = pygame.font.SysFont(None, 48)
        self.is_dragging = False
        self.handle_radius = height // 2 + 10
        self.handle_x = self._get_handle_x()

    def _get_handle_x(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Calculate the exact distance to the center of the circular handle
                dx = mouse_pos[0] - self.handle_x
                dy = mouse_pos[1] - self.rect.centery
                distance_squared = (dx ** 2) + (dy ** 2)
                
                # Only drag if we clicked the track OR inside the exact radius of the handle
                if self.rect.collidepoint(mouse_pos) or distance_squared <= (self.handle_radius ** 2):
                    self.is_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging = False

        if self.is_dragging:
            # Clamp the drag inside the track
            new_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
            ratio = (new_x - self.rect.x) / self.rect.width
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            self.handle_x = new_x

    def draw(self, surface):
        # Draw Label & Value
        text_surf = self.font.render(f"{self.text}: {int(self.value * 100)}%", True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x, self.rect.y - 40))
        
        # Draw Background Track
        pygame.draw.rect(surface, (80, 80, 80), self.rect, border_radius=self.rect.height//2)
        
        # Draw Filled Track
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_x - self.rect.x, self.rect.height)
        pygame.draw.rect(surface, (100, 200, 100), fill_rect, border_radius=self.rect.height//2)
        
        # Draw Handle
        pygame.draw.circle(surface, (255, 255, 255), (self.handle_x, self.rect.centery), self.handle_radius)