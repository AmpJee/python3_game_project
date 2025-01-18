import pygame
import math
from collections import deque

class GameWindow:
    def __init__(self, client):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"Ball Game - Player {client.player_id}")
        
        self.client = client
        self.game_state = None
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Pre-render common text
        self.speed_text = self.font.render("Speed: ", True, (0, 0, 0))
        self.score_text = self.font.render("Score: ", True, (0, 0, 0))
        
        # Double buffer for smoother rendering
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255, 255, 255))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                pressed = event.type == pygame.KEYDOWN
                
                if event.key == pygame.K_w:
                    self.client.send_input('w', pressed)
                elif event.key == pygame.K_a:
                    self.client.send_input('a', pressed)
                elif event.key == pygame.K_d:
                    self.client.send_input('d', pressed)
        
        return True

    def update_game_state(self, state):
        self.game_state = state

    def draw(self):
        if not self.game_state:
            return
            
        # Clear the background
        self.background.fill((255, 255, 255))
        
        # Draw food
        food_data = self.game_state["foods"]
        pygame.draw.circle(
            self.background,
            (0, 0, 255),
            (int(food_data["x"]), int(food_data["y"])),
            food_data["radius"]
        )
        
        # Draw players
        for player_id, ball_data in self.game_state["ball"].items():
            x = int(ball_data["x"])
            y = int(ball_data["y"])
            
            # Draw ball
            pygame.draw.circle(
                self.background,
                ball_data["color"],
                (x, y),
                ball_data["radius"]
            )
            
            # Draw direction indicator
            direction = math.radians(ball_data["direction"])
            end_x = x + math.cos(direction) * 20
            end_y = y + math.sin(direction) * 20
            pygame.draw.line(
                self.background,
                (0, 0, 0),
                (x, y),
                (int(end_x), int(end_y)),
                2
            )
            
            # Draw speed and score
            speed_value = self.font.render(f"{ball_data['speed']:.1f}", True, (0, 0, 0))
            score_value = self.font.render(f"{ball_data.get('score', 0)}", True, (0, 0, 0))
            
            # Left align for player 1, right align for player 2
            x_pos = 10 if player_id == "1" else self.width - 160
            
            # Speed display
            self.background.blit(self.speed_text, (x_pos, 10))
            self.background.blit(speed_value, (x_pos + 70, 10))
            
            # Score display
            self.background.blit(self.score_text, (x_pos, 50))
            self.background.blit(score_value, (x_pos + 70, 50))
        
        # Flip buffers
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def run(self):
        while self.client.running:
            if not self.handle_input():
                break
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()