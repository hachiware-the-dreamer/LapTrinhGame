import pygame
from start_screen import Button


class PauseScreen:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height

        self.title_font = pygame.font.Font("font/Pixeltype.ttf", 80)
        self.button_font = pygame.font.Font("font/Pixeltype.ttf", 40)

        self.button_color = (100, 100, 100)
        self.button_hover = (150, 150, 150)
        self.text_color = (255, 255, 255)

        button_width = 300
        button_height = 60
        button_x = screen_width // 2 - button_width // 2

        self.restart_button = Button(
            button_x,
            200,
            button_width,
            button_height,
            "RESTART",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.menu_button = Button(
            button_x,
            280,
            button_width,
            button_height,
            "MAIN MENU",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.quit_button = Button(
            button_x,
            360,
            button_width,
            button_height,
            "QUIT",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

    def draw(self, surface):

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        surface.blit(title, title_rect)

        self.restart_button.draw(surface)
        self.menu_button.draw(surface)
        self.quit_button.draw(surface)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        self.restart_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_button.is_clicked(mouse_pos):
                return "restart"
            if self.menu_button.is_clicked(mouse_pos):
                return "menu"
            if self.quit_button.is_clicked(mouse_pos):
                return "quit"

        return None
