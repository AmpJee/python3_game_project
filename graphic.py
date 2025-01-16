import pygame
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Multiplayer Graphics")


WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BACKGROUND_COLOR = (30, 30, 30)


circle_x, circle_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
circle_radius = 20



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

   
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), circle_radius)  # Player

    
    pygame.display.flip()

pygame.quit()
