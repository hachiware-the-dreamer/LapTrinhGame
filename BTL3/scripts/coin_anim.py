import pygame


class CoinAnimation:
    def __init__(self, sheet_path, size=(48, 48)):
        self.frames = []
        self.size = size

        sheet = pygame.image.load(sheet_path).convert_alpha()
        total_w, total_h = sheet.get_size()
        frame_width = total_w // 8
        frame_height = total_h

        for i in range(8):
            frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame = sheet.subsurface(frame_rect).copy()
            frame = pygame.transform.scale(frame, self.size)
            self.frames.append(frame)

        self.length = len(self.frames)
        self.index = 0
        self.timer = 0.0
        self.fps = 14

    def update(self, dt):
        self.timer += dt
        frame_step = 1.0 / self.fps
        while self.timer >= frame_step:
            self.timer -= frame_step
            self.index = (self.index + 1) % self.length

    def get_image(self):
        return self.frames[self.index]
