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
    def __init__(self, x, y, width, height, text, callback, font_size=56, color=(70, 130, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        
        self.font = pygame.font.SysFont("Segoe UI", font_size, bold=True)
        self.base_color = pygame.Color(*color)
        
        # Safer color calculation to avoid wrap-around
        h, s, l, a = self.base_color.hsla
        self.hover_color = pygame.Color(0, 0, 0)
        self.hover_color.hsla = (h, s, min(100, l + 10), a)
        
        self.active_color = pygame.Color(50, 200, 50)
        self.text_color = (255, 255, 255)
        
        self.is_hovered = False
        self.is_active = False
        self.animation_scale = 1.0
        self.target_scale = 1.0

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        self.target_scale = 1.05 if self.is_hovered else 1.0
        # Smooth scaling animation
        self.animation_scale += (self.target_scale - self.animation_scale) * 0.15

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered and self.callback:
                    self.callback()

    def draw(self, surface):
        # Scale button rect for animation
        scaled_w = int(self.rect.width * self.animation_scale)
        scaled_h = int(self.rect.height * self.animation_scale)
        draw_rect = pygame.Rect(0, 0, scaled_w, scaled_h)
        draw_rect.center = self.rect.center

        # Draw shadow (using a separate surface for true alpha if needed, but simple rect is fine)
        shadow_rect = draw_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(surface, (20, 20, 20), shadow_rect, border_radius=15)

        # Dynamic color based on state
        current_color = self.active_color if self.is_active else (self.hover_color if self.is_hovered else self.base_color)
        
        # Draw main button body
        pygame.draw.rect(surface, current_color, draw_rect, border_radius=15)
        
        # Highlight top half for 3D look
        highlight_surface = pygame.Surface((draw_rect.width, draw_rect.height // 2), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, (255, 255, 255, 40), (0, 0, draw_rect.width, draw_rect.height // 2), 
                         border_top_left_radius=15, border_top_right_radius=15)
        surface.blit(highlight_surface, (draw_rect.x, draw_rect.y))

        # Draw border
        pygame.draw.rect(surface, (255, 255, 255, 100), draw_rect, width=2, border_radius=15)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

class UISlider:
    def __init__(self, x, y, width, height, min_val, max_val, start_val, text, is_int=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.text = text
        self.is_int = is_int
        
        self.font = pygame.font.SysFont("Segoe UI", 36, bold=True)
        self.is_dragging = False
        self.handle_radius = height // 2 + 10
        self.handle_x = self._get_handle_x()

    def _get_handle_x(self):
        val_range = self.max_val - self.min_val
        if val_range == 0: return self.rect.x
        ratio = (self.value - self.min_val) / val_range
        return int(self.rect.x + ratio * self.rect.width)

    def set_value(self, new_val):
        """Programmatically snaps the slider to a new value."""
        self.value = max(self.min_val, min(new_val, self.max_val))
        self.handle_x = self._get_handle_x()

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        # Check if mouse is hovering over the handle
        dx = mouse_pos[0] - self.handle_x
        dy = mouse_pos[1] - self.rect.centery
        is_over_handle = (dx ** 2) + (dy ** 2) <= (self.handle_radius ** 2)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(mouse_pos) or is_over_handle:
                    self.is_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging = False

        if self.is_dragging:
            # Clamp the drag inside the track
            new_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
            ratio = (new_x - self.rect.x) / max(1, self.rect.width)
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            self.handle_x = new_x

    def draw(self, surface):
        # Format text based on flag
        if self.is_int:
            display_str = f"{int(self.value)}"
        else:
            display_str = f"{int(self.value * 100)}%"

        text_surf = self.font.render(f"{self.text}: {display_str}", True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x, self.rect.y - 40))

        # Draw Background Track
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=self.rect.height//2)
        # Draw Filled Track
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_x - self.rect.x, self.rect.height)
        pygame.draw.rect(surface, (70, 130, 180), fill_rect, border_radius=self.rect.height//2)

        # Draw Handle with glow if dragging
        handle_color = (255, 255, 255) if not self.is_dragging else (200, 230, 255)
        pygame.draw.circle(surface, handle_color, (self.handle_x, self.rect.centery), self.handle_radius)
        if self.is_dragging:
            pygame.draw.circle(surface, (255, 255, 255, 50), (self.handle_x, self.rect.centery), self.handle_radius + 5, 2)