import pygame

import config


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
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class ScreenStart:
    """Start screen with main menu buttons"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.title_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 120)
        self.button_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 50)

        self.bg_color = (173, 216, 230)
        self.button_color = (70, 130, 180)
        self.button_hover = (100, 149, 237)
        self.text_color = (255, 255, 255)

        button_width = 400
        button_height = 70
        button_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 50

        self.start_button = Button(
            button_x,
            start_y,
            button_width,
            button_height,
            "START GAME",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.instruction_button = Button(
            button_x,
            start_y + 90,
            button_width,
            button_height,
            "INSTRUCTIONS",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.settings_button = Button(
            button_x,
            start_y + 180,
            button_width,
            button_height,
            "SETTINGS",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.quit_button = Button(
            button_x,
            start_y + 270,
            button_width,
            button_height,
            "EXIT GAME",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

    def draw(self, screen):
        screen.fill(self.bg_color)
        
        # Title
        title_text = self.title_font.render("AIM TRAINER", True, (30, 60, 120))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 40)
        subtitle_text = subtitle_font.render("Test Your Reflexes", True, (60, 60, 60))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 280))
        screen.blit(subtitle_text, subtitle_rect)

        self.start_button.draw(screen)
        self.instruction_button.draw(screen)
        self.settings_button.draw(screen)
        self.quit_button.draw(screen)

    def handle_event(self, event, mouse_pos):
        """
        Returns: 'start', 'instructions', 'settings', 'quit', or None
        """
        self.start_button.check_hover(mouse_pos)
        self.instruction_button.check_hover(mouse_pos)
        self.settings_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.is_clicked(mouse_pos):
                return "start"
            elif self.instruction_button.is_clicked(mouse_pos):
                return "instructions"
            elif self.settings_button.is_clicked(mouse_pos):
                return "settings"
            elif self.quit_button.is_clicked(mouse_pos):
                return "quit"

        return None


class ScreenResults:
    """Results screen showing comprehensive session statistics"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.title_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 100)
        self.stats_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 50)
        self.button_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 45)

        self.bg_color = (173, 216, 230)
        self.button_color = (70, 130, 180)
        self.button_hover = (100, 149, 237)
        self.text_color = (20, 20, 20)

        button_width = 350
        button_height = 65
        button_x = screen_width // 2 - button_width // 2

        self.play_again_button = Button(
            button_x,
            screen_height - 220,
            button_width,
            button_height,
            "PLAY AGAIN",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.menu_button = Button(
            button_x,
            screen_height - 140,
            button_width,
            button_height,
            "MAIN MENU",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        # Stats
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.accuracy = 0
        self.avg_reaction = 0
        self.best_reaction = 0

    def set_stats(self, score, hits, misses, avg_reaction, best_reaction):
        """Update the stats to display"""
        self.score = score
        self.hits = hits
        self.misses = misses
        self.avg_reaction = avg_reaction
        self.best_reaction = best_reaction
        
        total = hits + misses
        self.accuracy = (hits / total * 100) if total > 0 else 0

    def draw(self, screen):
        screen.fill(self.bg_color)

        # Title
        title = "SESSION COMPLETE!"
        title_surf = self.title_font.render(title, True, (100, 255, 100))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 120))
        screen.blit(title_surf, title_rect)

        # Stats frame
        frame_width = 900
        frame_height = 500
        frame_x = self.screen_width // 2 - frame_width // 2
        frame_y = 220
        
        # Frame background
        pygame.draw.rect(screen, (150, 190, 220), (frame_x, frame_y, frame_width, frame_height))
        pygame.draw.rect(screen, (30, 60, 120), (frame_x, frame_y, frame_width, frame_height), 4)

        # Display stats
        y_offset = frame_y + 50
        line_spacing = 75

        # Score (largest)
        score_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 70)
        score_surf = score_font.render(f"SCORE: {self.score}", True, (200, 120, 0))
        score_rect = score_surf.get_rect(center=(self.screen_width // 2, y_offset))
        screen.blit(score_surf, score_rect)
        y_offset += 90

        # Hits
        hits_surf = self.stats_font.render(f"Hits: {self.hits}", True, (0, 150, 0))
        hits_rect = hits_surf.get_rect(center=(self.screen_width // 2, y_offset))
        screen.blit(hits_surf, hits_rect)
        y_offset += line_spacing

        # Misses
        misses_surf = self.stats_font.render(f"Misses: {self.misses}", True, (200, 0, 0))
        misses_rect = misses_surf.get_rect(center=(self.screen_width // 2, y_offset))
        screen.blit(misses_surf, misses_rect)
        y_offset += line_spacing

        # Accuracy
        accuracy_surf = self.stats_font.render(f"Accuracy: {self.accuracy:.1f}%", True, (20, 20, 20))
        accuracy_rect = accuracy_surf.get_rect(center=(self.screen_width // 2, y_offset))
        screen.blit(accuracy_surf, accuracy_rect)
        y_offset += line_spacing

        # Average reaction time
        avg_surf = self.stats_font.render(f"Avg Reaction: {self.avg_reaction:.0f}ms", True, (30, 60, 120))
        avg_rect = avg_surf.get_rect(center=(self.screen_width // 2, y_offset))
        screen.blit(avg_surf, avg_rect)
        y_offset += line_spacing

        # Best reaction time
        best_surf = self.stats_font.render(f"Best Reaction: {self.best_reaction:.0f}ms", True, (120, 60, 150))
        best_rect = best_surf.get_rect(center=(self.screen_width // 2, y_offset))
        screen.blit(best_surf, best_rect)

        self.play_again_button.draw(screen)
        self.menu_button.draw(screen)

    def handle_event(self, event, mouse_pos):
        """
        Returns: 'play_again', 'menu', or None
        """
        self.play_again_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_again_button.is_clicked(mouse_pos):
                return "play_again"
            elif self.menu_button.is_clicked(mouse_pos):
                return "menu"

        return None


class ScreenPause:
    """Pause screen overlay"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height

        self.title_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 100)
        self.button_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 45)

        self.button_color = (70, 130, 180)
        self.button_hover = (100, 149, 237)
        self.text_color = (255, 255, 255)

        button_width = 350
        button_height = 65
        button_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 50

        self.resume_button = Button(
            button_x,
            start_y,
            button_width,
            button_height,
            "RESUME",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

        self.restart_button = Button(
            button_x,
            start_y + 85,
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
            start_y + 170,
            button_width,
            button_height,
            "MAIN MENU",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )

    def draw(self, surface):
        # Dark overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 250))
        surface.blit(title, title_rect)

        self.resume_button.draw(surface)
        self.restart_button.draw(surface)
        self.menu_button.draw(surface)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        self.resume_button.check_hover(mouse_pos)
        self.restart_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.resume_button.is_clicked(mouse_pos):
                return "resume"
            if self.restart_button.is_clicked(mouse_pos):
                return "restart"
            if self.menu_button.is_clicked(mouse_pos):
                return "menu"

        return None


class ScreenInstructions:
    """Instructions screen"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        self.title_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 90)
        self.text_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 40)
        self.button_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 45)
        
        self.bg_color = (173, 216, 230)
        self.button_color = (70, 130, 180)
        self.button_hover = (100, 149, 237)
        self.text_color = (20, 20, 20)
        
        # Back button
        button_width = 300
        button_height = 65
        self.back_button = Button(
            screen_width // 2 - button_width // 2,
            screen_height - 120,
            button_width,
            button_height,
            "BACK",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )
    
    def draw(self, screen):
        screen.fill(self.bg_color)
        
        # Title
        title = self.title_font.render("INSTRUCTIONS", True, (30, 60, 120))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        screen.blit(title, title_rect)
        
        # Instructions text
        instructions = [
            "• Click on targets as quickly as possible",
            "• Each target has a limited lifetime (TTL)",
            "• Score points based on speed and accuracy",
            "• Game becomes harder over time",
            "• Press ESC to pause during gameplay",
            "",
            "Scoring Formula:",
            "  Score = 100 + Reflex Bonus",
            "  Reflex Bonus = (TTL - Reaction Time) / TTL * 50",
            "",
            "Good luck!",
        ]
        
        y = 220
        for line in instructions:
            text_surf = self.text_font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(center=(self.width // 2, y))
            screen.blit(text_surf, text_rect)
            y += 55
        
        self.back_button.draw(screen)
    
    def handle_event(self, event, mouse_pos):
        self.back_button.check_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(mouse_pos):
                return "back"
        
        return None


class ScreenSettings:
    """Settings screen for gameplay parameters"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        self.title_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 90)
        self.text_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 40)
        self.button_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 45)
        self.value_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 40)
        
        self.bg_color = (173, 216, 230)
        self.button_color = (70, 130, 180)
        self.button_hover = (100, 149, 237)
        self.text_color = (20, 20, 20)
        
        # Preset buttons
        preset_width = 220
        preset_height = 60
        preset_y = 190
        preset_gap = 30
        total_width = preset_width * 3 + preset_gap * 2
        preset_x = screen_width // 2 - total_width // 2

        self.preset_buttons = {
            "easy": Button(
                preset_x,
                preset_y,
                preset_width,
                preset_height,
                "EASY",
                self.button_font,
                self.text_color,
                self.button_color,
                self.button_hover,
            ),
            "medium": Button(
                preset_x + preset_width + preset_gap,
                preset_y,
                preset_width,
                preset_height,
                "MEDIUM",
                self.button_font,
                self.text_color,
                self.button_color,
                self.button_hover,
            ),
            "hard": Button(
                preset_x + (preset_width + preset_gap) * 2,
                preset_y,
                preset_width,
                preset_height,
                "HARD",
                self.button_font,
                self.text_color,
                self.button_color,
                self.button_hover,
            ),
        }

        # Settings rows
        self.setting_rows = []
        row_start_y = 300
        row_gap = 70
        label_x = 220
        value_x = 1050
        button_size = 50
        button_gap = 18

        row_defs = [
            {
                "key": "game_duration",
                "label": "Game Duration",
                "unit": "ms",
                "step": 5000,
            },
            {
                "key": "initial_target_radius",
                "label": "Initial Target Size",
                "unit": "px",
                "step": 2,
            },
            {
                "key": "min_target_radius",
                "label": "Minimum Target Size",
                "unit": "px",
                "step": 2,
            },
            {
                "key": "initial_ttl",
                "label": "Initial TTL",
                "unit": "ms",
                "step": 100,
            },
            {
                "key": "ttl_decrease_amount",
                "label": "TTL Decrease",
                "unit": "ms",
                "step": 10,
            },
            {
                "key": "radius_decrease_amount",
                "label": "Size Decrease",
                "unit": "px",
                "step": 1,
            },
        ]

        for index, row in enumerate(row_defs):
            y = row_start_y + index * row_gap
            minus_button = Button(
                value_x + 110,
                y - button_size // 2,
                button_size,
                button_size,
                "-",
                self.button_font,
                self.text_color,
                self.button_color,
                self.button_hover,
            )
            plus_button = Button(
                value_x + 110 + button_size + button_gap,
                y - button_size // 2,
                button_size,
                button_size,
                "+",
                self.button_font,
                self.text_color,
                self.button_color,
                self.button_hover,
            )
            row["y"] = y
            row["label_x"] = label_x
            row["value_x"] = value_x
            row["minus_button"] = minus_button
            row["plus_button"] = plus_button
            self.setting_rows.append(row)

        # Back button
        button_width = 300
        button_height = 65
        self.back_button = Button(
            screen_width // 2 - button_width // 2,
            screen_height - 120,
            button_width,
            button_height,
            "BACK",
            self.button_font,
            self.text_color,
            self.button_color,
            self.button_hover,
        )
    
    def draw(self, screen):
        screen.fill(self.bg_color)
        
        # Title
        title = self.title_font.render("SETTINGS", True, (30, 60, 120))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        screen.blit(title, title_rect)

        subtitle = self.text_font.render("Presets", True, (60, 60, 60))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 150))
        screen.blit(subtitle, subtitle_rect)

        for button in self.preset_buttons.values():
            button.draw(screen)

        # Settings rows
        for row in self.setting_rows:
            label_surf = self.text_font.render(row["label"], True, self.text_color)
            label_rect = label_surf.get_rect(midleft=(row["label_x"], row["y"]))
            screen.blit(label_surf, label_rect)

            value = config.SETTINGS[row["key"]]
            value_text = f"{value}{row['unit']}"
            value_surf = self.value_font.render(value_text, True, (30, 60, 120))
            value_rect = value_surf.get_rect(center=(row["value_x"], row["y"]))
            screen.blit(value_surf, value_rect)

            row["minus_button"].draw(screen)
            row["plus_button"].draw(screen)

        self.back_button.draw(screen)
    
    def handle_event(self, event, mouse_pos):
        self.back_button.check_hover(mouse_pos)
        for button in self.preset_buttons.values():
            button.check_hover(mouse_pos)
        for row in self.setting_rows:
            row["minus_button"].check_hover(mouse_pos)
            row["plus_button"].check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(mouse_pos):
                return "back"

            for name, button in self.preset_buttons.items():
                if button.is_clicked(mouse_pos):
                    preset = config.PRESETS.get(name)
                    if preset:
                        config.apply_settings(preset)
                    return None

            for row in self.setting_rows:
                key = row["key"]
                current = config.SETTINGS[key]
                if row["minus_button"].is_clicked(mouse_pos):
                    config.apply_settings({key: current - row["step"]})
                    return None
                if row["plus_button"].is_clicked(mouse_pos):
                    config.apply_settings({key: current + row["step"]})
                    return None

        return None
