import pygame
import sys

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
        
        # Font for score display
        self.font = pygame.font.Font(None, 36)
    
    def handle_input(self):
        """Handle keyboard input"""
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
    
    def update_game_state(self, state, events):
        """Update game state from server"""
        self.game_state = state
    
    def draw(self):
        """Draw the game state"""
        if not self.game_state:
            return
            
        # Clear screen
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw food
        food_data = self.game_state["foods"]
        pygame.draw.circle(
            self.screen,
            (255, 255, 0),  # Yellow color for food
            (int(food_data["x"]), int(food_data["y"])),
            food_data["radius"]
        )
        
        # Draw balls
        for player_id, ball_data in self.game_state["ball"].items():
            # Draw the ball
            pygame.draw.circle(
                self.screen,
                ball_data["color"],
                (int(ball_data["x"]), int(ball_data["y"])),
                ball_data["radius"]
            )
            
            # Draw direction indicator
            import math
            end_x = ball_data["x"] + math.cos(math.radians(ball_data["direction"])) * 20
            end_y = ball_data["y"] + math.sin(math.radians(ball_data["direction"])) * 20
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (ball_data["x"], ball_data["y"]),
                (end_x, end_y),
                2
            )
            
            # Draw speed indicator
            speed_text = self.font.render(f"Speed: {ball_data['speed']:.1f}", True, (0, 0, 0))
            self.screen.blit(
                speed_text,
                (10 if player_id == "1" else self.width - 160, 10)
            )
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running and self.client.running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()