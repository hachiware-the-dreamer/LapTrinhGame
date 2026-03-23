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
        self.color_text = (255, 255, 255)
        self.is_hovered = False

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_hovered and self.callback:
                    self.callback()

    def draw(self, surface):
        current_color = self.color_hover if self.is_hovered else self.color_normal
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        
        text_surf = self.font.render(self.text, True, self.color_text)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)