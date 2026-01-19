import pygame


class Button:
    def __init__(self, x, y, width, height, text, font, text_color, bg_color, hover_color):
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


class StartScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.title_font = pygame.font.Font("font/Pixeltype.ttf", 80)
        self.button_font = pygame.font.Font("font/Pixeltype.ttf", 40)
        
        self.bg_color = (34, 139, 34)  # Forest green
        self.button_color = (100, 100, 100)
        self.button_hover = (150, 150, 150)
        self.text_color = (255, 255, 255)
        
        button_width = 300
        button_height = 60
        button_x = screen_width // 2 - button_width // 2
        
        self.start_button = Button(
            button_x, 200, button_width, button_height,
            "START", self.button_font, self.text_color,
            self.button_color, self.button_hover
        )
        
        self.difficulty_button = Button(
            button_x, 280, button_width, button_height,
            "DIFFICULTY: NORMAL", self.button_font, self.text_color,
            self.button_color, self.button_hover
        )
        
        self.quit_button = Button(
            button_x, 360, button_width, button_height,
            "QUIT", self.button_font, self.text_color,
            self.button_color, self.button_hover
        )
        
        self.difficulty_levels = ["EASY", "NORMAL", "HARD"]
        self.current_difficulty = 1
    
    def draw(self, screen):
        screen.fill(self.bg_color)
        
        title_surf = self.title_font.render("WHACK-A-ZOMBIE", True, (255, 0, 0))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_surf, title_rect)
        
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
                return 'start'
            elif self.difficulty_button.is_clicked(mouse_pos):
                self.cycle_difficulty()
            elif self.quit_button.is_clicked(mouse_pos):
                return 'quit'
        
        return None
    
    def cycle_difficulty(self):
        self.current_difficulty = (self.current_difficulty + 1) % len(self.difficulty_levels)
        difficulty_text = self.difficulty_levels[self.current_difficulty]
        self.difficulty_button.text = f"DIFFICULTY: {difficulty_text}"
    
    def get_difficulty_settings(self):
        """
        Returns TTL and zombie count based on difficulty
        """
        if self.current_difficulty == 0:  # Easy
            return 1500, 2  # TTL, zombie_count
        elif self.current_difficulty == 1:  # Normal
            return 1200, 2
        else:  # Hard
            return 800, 2
