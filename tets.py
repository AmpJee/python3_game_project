import pygame
import math

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball Simulation")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.direction = 0

    def move_forward(self, max_speed=10):
        self.speed = min(self.speed + 0.5, max_speed)

    def stop_moving(self):
        self.speed = max(self.speed - 0.3, 0)

    def turn_left(self):
        self.direction = (self.direction + 5) % 360

    def turn_right(self):
        self.direction = (self.direction - 5) % 360

    def move(self):
        angle = math.radians(self.direction)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

        self.x = min(max(self.x, 0), SCREEN_WIDTH)
        self.y = min(max(self.y, 0), SCREEN_HEIGHT)

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 15)

    def get_status(self):
        return f"Ball position: ({self.x:.2f}, {self.y:.2f}), Speed: {self.speed}, Direction: {self.direction}"

def test_ball():
    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            ball.move_forward()
        else:
            ball.stop_moving()

        if keys[pygame.K_a]:
            ball.turn_left()
        if keys[pygame.K_d]:
            ball.turn_right()

        ball.move()
        ball.draw(screen)

        # Display status
        font = pygame.font.SysFont(None, 24)
        status_text = font.render(ball.get_status(), True, BLACK)
        screen.blit(status_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    test_ball()