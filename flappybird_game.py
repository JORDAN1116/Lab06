import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Colors
SKY_BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)

# Game Physics Constants
GRAVITY = 0.5
FLAP_STRENGTH = -8
PIPE_SPEED = 4
PIPE_GAP = 180
PIPE_WIDTH = 80
PIPE_FREQUENCY = 1500  # milliseconds

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.width = 40
        self.height = 30
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y

    def draw(self, screen):
        # Body (Yellow rectangle)
        pygame.draw.rect(screen, YELLOW, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Eye (Small white/black square)
        eye_rect = pygame.Rect(self.rect.right - 12, self.rect.top + 5, 8, 8)
        pygame.draw.rect(screen, WHITE, eye_rect)
        pygame.draw.rect(screen, BLACK, eye_rect, 1)
        pupil_rect = pygame.Rect(self.rect.right - 8, self.rect.top + 8, 3, 3)
        pygame.draw.rect(screen, BLACK, pupil_rect)
        
        # Beak (Orange rectangle)
        beak_rect = pygame.Rect(self.rect.right, self.rect.top + 15, 12, 10)
        pygame.draw.rect(screen, ORANGE, beak_rect)
        pygame.draw.rect(screen, BLACK, beak_rect, 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 100 - PIPE_GAP)
        self.width = PIPE_WIDTH
        self.passed = False
        
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - (self.gap_y + PIPE_GAP))

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        # Main pipe body
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, BLACK, self.top_rect, 3)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        pygame.draw.rect(screen, BLACK, self.bottom_rect, 3)
        
        # Pipe caps
        cap_height = 35
        top_cap = pygame.Rect(self.x - 5, self.gap_y - cap_height, self.width + 10, cap_height)
        bottom_cap = pygame.Rect(self.x - 5, self.gap_y + PIPE_GAP, self.width + 10, cap_height)
        pygame.draw.rect(screen, GREEN, top_cap)
        pygame.draw.rect(screen, BLACK, top_cap, 3)
        pygame.draw.rect(screen, GREEN, bottom_cap)
        pygame.draw.rect(screen, BLACK, bottom_cap, 3)

class FlappyBirdGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("8-Bit Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Courier', 32, bold=True)
        self.large_font = pygame.font.SysFont('Courier', 64, bold=True)
        
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_active = False
        self.game_over = False
        self.paused = False
        self.last_pipe_time = pygame.time.get_ticks()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not self.game_active and not self.game_over:
                        self.game_active = True
                    if self.game_active and not self.paused:
                        self.bird.flap()
                
                if event.key == pygame.K_p:
                    if self.game_active and not self.game_over:
                        self.paused = not self.paused
                
                if event.key == pygame.K_r:
                    if self.game_over:
                        self.reset_game()

    def update(self):
        if self.game_active and not self.paused:
            # Update Bird
            self.bird.update()
            
            # Check collisions with boundaries
            if self.bird.rect.top <= 0 or self.bird.rect.bottom >= SCREEN_HEIGHT:
                self.game_over = True
                self.game_active = False

            # Manage Pipes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe_time > PIPE_FREQUENCY:
                self.pipes.append(Pipe(SCREEN_WIDTH))
                self.last_pipe_time = current_time

            for pipe in self.pipes[:]:
                pipe.update()
                
                # Collision detection
                if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                    self.game_over = True
                    self.game_active = False
                
                # Scoring
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    self.pipes.remove(pipe)

    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        # Draw Pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw Ground/Ceiling decoration
        pygame.draw.rect(self.screen, BROWN, (0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))
        
        # Draw Bird
        self.bird.draw(self.screen)
        
        # Draw Score
        score_surface = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        # Draw a small shadow for score to make it pop
        shadow_surface = self.font.render(f"Score: {self.score}", True, BLACK)
        shadow_rect = shadow_surface.get_rect(topright=(SCREEN_WIDTH - 18, 22))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(score_surface, score_rect)
        
        # Game Over Message
        if self.game_over:
            over_surface = self.large_font.render("GAME OVER", True, BLACK)
            over_rect = over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(over_surface, over_rect)
            
            final_score_surface = self.font.render(f"Final Score: {self.score}", True, BLACK)
            final_score_rect = final_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(final_score_surface, final_score_rect)
            
            restart_surface = self.font.render("Press 'R' to Restart", True, BLACK)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
            self.screen.blit(restart_surface, restart_rect)
            
        # Start Message
        elif not self.game_active and not self.game_over:
            start_surface = self.font.render("Press SPACE to Start", True, BLACK)
            start_rect = start_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(start_surface, start_rect)
            
        # Pause Message
        if self.paused:
            pause_surface = self.large_font.render("PAUSED", True, BLACK)
            pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_surface, pause_rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()
