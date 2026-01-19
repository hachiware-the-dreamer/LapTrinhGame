import pygame


class Button:
    def __init__(
        self, x, y, width, height, text, font, text_color, bg_color, hover_color
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 3)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class ScreenStart:
    def __init__(self, screen_width, screen_height):
        # Background
        self.background_surf = pygame.image.load("assets/screen/screen_start.png").convert()
        self.background_surf = pygame.transform.scale(
            self.background_surf, (screen_width, screen_height)
        )

        # Logo
        self.logo_surf = pygame.image.load("assets/logo.png").convert_alpha()
        logo_w = int(screen_width * 0.6)
        logo_h = int(self.logo_surf.get_height() * (logo_w / self.logo_surf.get_width()))
        self.logo_surf = pygame.transform.smoothscale(self.logo_surf, (logo_w, logo_h))
        self.logo_rect = self.logo_surf.get_rect(center=(screen_width // 2, 100))

        self.title_font = pygame.font.Font("font/Pixeltype.ttf", 80)
        self.button_font = pygame.font.Font("font/Pixeltype.ttf", 40)

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.button_color = (100, 100, 100)
        self.button_hover = (150, 150, 150)
        self.text_color = (255, 255, 255)

        button_width = 300
        button_height = 60
        button_x = screen_width // 2 - button_width // 2

        self.start_button = Button(
            button_x,
            200,
            button_width,
            button_height,
            "START",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.difficulty_button = Button(
            button_x,
            280,
            button_width,
            button_height,
            "DIFFICULTY: NORMAL",
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

        self.difficulty_levels = ["EASY", "NORMAL", "HARD"]
        self.current_difficulty = 1

    def draw(self, screen):
        screen.blit(self.background_surf, (0, 0))
        screen.blit(self.logo_surf, self.logo_rect)

        self.start_button.draw(screen)
        self.difficulty_button.draw(screen)
        self.quit_button.draw(screen)

    def handle_event(self, event, mouse_pos):
        """
        Returns: 'start', 'quit', or None
        """
        self.start_button.check_hover(mouse_pos)
        self.difficulty_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.is_clicked(mouse_pos):
                return "start"
            elif self.difficulty_button.is_clicked(mouse_pos):
                self.cycle_difficulty()
            elif self.quit_button.is_clicked(mouse_pos):
                return "quit"

        return None

    def cycle_difficulty(self):
        self.current_difficulty = (self.current_difficulty + 1) % len(
            self.difficulty_levels
        )
        difficulty_text = self.difficulty_levels[self.current_difficulty]
        self.difficulty_button.text = f"DIFFICULTY: {difficulty_text}"

    def get_difficulty_name(self):
        """Returns current difficulty name for config lookup"""
        return self.difficulty_levels[self.current_difficulty]


class ScreenEnd:
    def __init__(self, screen_width, screen_height):
        self.background_surf = pygame.image.load("assets/screen/screen_end.png").convert()
        self.background_surf = pygame.transform.scale(
            self.background_surf, (screen_width, screen_height)
        )
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.title_font = pygame.font.Font("font/Pixeltype.ttf", 80)
        self.stats_font = pygame.font.Font("font/Pixeltype.ttf", 50)
        self.button_font = pygame.font.Font("font/Pixeltype.ttf", 40)

        self.bg_color = (50, 50, 50)
        self.button_color = (100, 100, 100)
        self.button_hover = (150, 150, 150)
        self.text_color = (255, 255, 255)

        button_width = 300
        button_height = 60
        button_x = screen_width // 2 - button_width // 2

        self.play_again_button = Button(
            button_x,
            320,
            button_width,
            button_height,
            "PLAY AGAIN",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.quit_button = Button(
            button_x,
            400,
            button_width,
            button_height,
            "QUIT",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.hits = 0
        self.misses = 0
        self.accuracy = 0
        self.best_accuracy = 0
        self.game_over_reason = "win" 

    def set_stats(self, hits, misses, reason="win"):
        """Update the stats to display"""
        self.hits = hits
        self.misses = misses
        self.game_over_reason = reason
        total = hits + misses
        self.accuracy = (hits / total * 100) if total > 0 else 0
        if self.accuracy > self.best_accuracy:
            self.best_accuracy = self.accuracy

    def draw(self, screen):
        screen.blit(self.background_surf, (0, 0))

        # Title based on game over reason
        if self.game_over_reason == "explode":
            title = "BOOM! Creeper Exploded!"
            color = (255, 100, 0)
        elif self.game_over_reason == "misses":
            title = "Game Over!"
            color = (255, 50, 50)
        else:
            title = "You Win!"
            color = (50, 255, 50)

        # Draw frame/panel for stats
        frame_width = 800
        frame_height = 275
        frame_x = self.screen_width // 2 - frame_width // 2
        frame_y = 40
        
        # Semi-transparent background
        frame_surf = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame_surf.fill((0, 0, 0, 180))
        screen.blit(frame_surf, (frame_x, frame_y))
        
        # Frame border
        pygame.draw.rect(screen, (255, 255, 255), (frame_x, frame_y, frame_width, frame_height), 4)
        pygame.draw.rect(screen, color, (frame_x + 4, frame_y + 4, frame_width - 8, frame_height - 8), 2)

        title_surf = self.title_font.render(title, True, color)
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_surf, title_rect)

        hits_surf = self.stats_font.render(f"Hits: {self.hits}", True, (0, 255, 0))
        hits_rect = hits_surf.get_rect(center=(self.screen_width // 2, 130))
        screen.blit(hits_surf, hits_rect)

        misses_surf = self.stats_font.render(
            f"Misses: {self.misses}", True, (255, 100, 100)
        )
        misses_rect = misses_surf.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(misses_surf, misses_rect)

        accuracy_surf = self.stats_font.render(
            f"Accuracy: {self.accuracy:.1f}%", True, self.text_color
        )
        accuracy_rect = accuracy_surf.get_rect(center=(self.screen_width // 2, 230))
        screen.blit(accuracy_surf, accuracy_rect)

        best_accuracy_surf = self.stats_font.render(
            f"Best Accuracy: {self.best_accuracy:.1f}%", True, self.text_color
        )
        best_accuracy_rect = best_accuracy_surf.get_rect(
            center=(self.screen_width // 2, 280)
        )
        screen.blit(best_accuracy_surf, best_accuracy_rect)

        self.play_again_button.draw(screen)
        self.quit_button.draw(screen)

    def handle_event(self, event, mouse_pos):
        """
        Returns: 'play_again', 'quit', or None
        """
        self.play_again_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_again_button.is_clicked(mouse_pos):
                return "play_again"
            elif self.quit_button.is_clicked(mouse_pos):
                return "quit"

        return None


class ScreenPause:
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
