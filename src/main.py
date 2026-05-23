import pygame
import random
import sys

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/background.mp3")
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
STAR_SIZE = 30
STAR_SPEED = 5
PLAYER_SPEED = 8


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.score = 0

    def move(self, mouse_x):
        self.x = mouse_x - self.width // 2
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.arc(screen, BLUE,
                        (self.x + 10, self.y - 20, self.width - 20, 30),
                        3.14, 6.28, 5)
        pygame.draw.line(screen, WHITE, (self.x, self.y + 15),
                         (self.x + self.width, self.y + 15), 2)
        pygame.draw.line(screen, WHITE, (self.x, self.y + 30),
                         (self.x + self.width, self.y + 30), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH - STAR_SIZE)
        self.y = -STAR_SIZE
        self.size = random.randint(20, 35)
        self.speed = random.randint(3, 8)

        colors = [YELLOW, WHITE, RED, GREEN, PURPLE]
        self.color = random.choice(colors)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2

        points = []
        for i in range(5):
            angle_outer = (i * 72 - 90) * 3.14159 / 180
            x_outer = center_x + (self.size // 2) * math.cos(angle_outer)
            y_outer = center_y + (self.size // 2) * math.sin(angle_outer)
            points.append((x_outer, y_outer))

            angle_inner = ((i + 0.5) * 72 - 90) * 3.14159 / 180
            x_inner = center_x + (self.size // 4) * math.cos(angle_inner)
            y_inner = center_y + (self.size // 4) * math.sin(angle_inner)
            points.append((x_inner, y_inner))

        pygame.draw.polygon(screen, self.color, points)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Star Catcher - Лови звездочки!")
        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2,
                             SCREEN_HEIGHT - 80)
        self.star = Star()

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        try:
            self.catch_sound = pygame.mixer.Sound("assets/catch.wav")
            self.catch_sound.set_volume(0.05)
        except:
            self.catch_sound = None

        self.score = 0
        self.stars_caught = 0
        self.missed = 0
        self.game_over = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_over:
                    self.restart()
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        if self.game_over:
            return

        mouse_x, _ = pygame.mouse.get_pos()
        self.player.move(mouse_x)

        self.star.update()

        if self.player.get_rect().colliderect(self.star.get_rect()):
            self.score += 10
            self.stars_caught += 1

            if self.catch_sound:
                self.catch_sound.play()

            self.star.reset()

        elif self.star.y > SCREEN_HEIGHT:
            self.missed += 1
            self.star.reset()

            if self.missed >= 3:
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.screen.set_at((x, y), WHITE)

        self.player.draw(self.screen)
        self.star.draw(self.screen)

        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        missed_text = self.font.render(f"Пропущено: {self.missed}/3", True, RED)
        self.screen.blit(missed_text, (10, 50))

        caught_text = self.font.render(f"Поймано: {self.stars_caught}", True, GREEN)
        self.screen.blit(caught_text, (10, 90))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.big_font.render("GAME OVER", True, RED)
            score_text_big = self.big_font.render(f"Счет: {self.score}", True, YELLOW)
            restart_text = self.font.render("Нажмите ПРОБЕЛ чтобы начать заново", True, WHITE)

            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            score_rect = score_text_big.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(score_text_big, score_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def restart(self):
        self.score = 0
        self.stars_caught = 0
        self.missed = 0
        self.game_over = False
        self.star.reset()
        self.player.score = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    import math

    game = Game()
    game.run()