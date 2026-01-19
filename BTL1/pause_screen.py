import pygame


class PauseScreen:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.Font("font/Pixeltype.ttf", 50)
        self.title_font = pygame.font.Font("font/Pixeltype.ttf", 80)


        center_x = screen_width // 2

 
        self.restart_rect = pygame.Rect(0, 0, 200, 50)
        self.restart_rect.center = (center_x, screen_height // 2 - 60)


        self.menu_rect = pygame.Rect(0, 0, 200, 50)
        self.menu_rect.center = (center_x, screen_height // 2)


        self.quit_rect = pygame.Rect(0, 0, 200, 50)
        self.quit_rect.center = (center_x, screen_height // 2 + 60)

    def draw(self, surface):

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)  
        overlay.fill((0, 0, 0))  
        surface.blit(overlay, (0, 0))


        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        surface.blit(title, title_rect)


        self._draw_button(surface, "Restart", self.restart_rect, (50, 200, 50))
        self._draw_button(surface, "Main Menu", self.menu_rect, (50, 50, 200))
        self._draw_button(surface, "Quit Game", self.quit_rect, (200, 50, 50))

    def _draw_button(self, surface, text, rect, color):
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            color = (
                min(color[0] + 30, 255),
                min(color[1] + 30, 255),
                min(color[2] + 30, 255),
            )

        pygame.draw.rect(surface, color, rect, border_radius=10)
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_rect.collidepoint(event.pos):
                return "restart"
            if self.menu_rect.collidepoint(event.pos):
                return "menu"
            if self.quit_rect.collidepoint(event.pos):
                return "quit"
        return None
