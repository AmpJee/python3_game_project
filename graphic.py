import pygame
import sys
import math

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

        # Colors
        self.BACKGROUND_COLOR = (240, 240, 240)
        self.FOOD_COLOR = (255, 215, 0)
        self.TEXT_COLOR = (50, 50, 50)
        self.GRID_COLOR = (220, 220, 220)

        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Visual effects
        self.flash_start = 0
        self.flash_duration = 200
        self.show_fps = True
        
        # Score tracking
        self.scores = {}

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
                elif event.key == pygame.K_f and pressed:
                    self.show_fps = not self.show_fps

        return True

    def update_game_state(self, state):
        """Update game state from server"""
        if not state:
            return
            
        self.game_state = state
        
        # Handle events if they exist
        events = state.get('events', {})
        
        # Handle collision events
        if events.get('collision'):
            self.flash_start = pygame.time.get_ticks()
            
            # Update scores for collided players
            for player_id in events['collision']:
                pid = str(player_id)
                self.scores[pid] = self.scores.get(pid, 0) + 10
        
        # Update scores from game state
        for player_id, ball_data in state.get('ball', {}).items():
            if 'score' in ball_data:
                self.scores[player_id] = ball_data['score']

    def draw_background(self):
        """Draw the game background with grid"""
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Draw grid
        grid_spacing = 40
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 0), (x, self.height))
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.width, y))

    def draw_food(self, food_data):
        """Draw food with glowing effect"""
        if not food_data:
            return
            
        x, y = int(food_data["x"]), int(food_data["y"])
        radius = food_data["radius"]
        
        # Draw glow effect
        for i in range(3):
            glow_radius = radius + (3 - i) * 2
            alpha = 100 - i * 30
            s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.FOOD_COLOR, alpha), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(s, (x - glow_radius, y - glow_radius))
        
        # Draw main food
        pygame.draw.circle(self.screen, self.FOOD_COLOR, (x, y), radius)

    def draw_player(self, player_id, ball_data):
        """Draw a player ball with direction indicator and score"""
        x, y = int(ball_data["x"]), int(ball_data["y"])
        radius = ball_data["radius"]
        color = ball_data["color"]
        direction = ball_data["direction"]
        
        # Draw the ball
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Draw direction indicator
        end_x = x + math.cos(math.radians(direction)) * (radius + 10)
        end_y = y + math.sin(math.radians(direction)) * (radius + 10)
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (end_x, end_y), 2)
        
        # Draw player label and score
        score = self.scores.get(str(player_id), 0)
        label = f"P{player_id} ({score})"
        if player_id == self.client.player_id:
            label += " (YOU)"
        
        text = self.font_small.render(label, True, self.TEXT_COLOR)
        text_rect = text.get_rect(center=(x, y - radius - 15))
        self.screen.blit(text, text_rect)

    def draw_scoreboard(self):
        """Draw scoreboard in the top-right corner"""
        if not self.scores:
            return
            
        # Sort scores
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        
        # Draw background
        padding = 10
        entry_height = 30
        board_width = 200
        board_height = len(sorted_scores) * entry_height + padding * 3
        
        board_surface = pygame.Surface((board_width, board_height))
        board_surface.fill((255, 255, 255))
        board_surface.set_alpha(200)
        
        # Draw title
        title = self.font_large.render("Scoreboard", True, self.TEXT_COLOR)
        board_surface.blit(title, (padding, padding))
        
        # Draw scores
        y = padding * 2 + self.font_large.get_height()
        for player_id, score in sorted_scores:
            text = f"Player {player_id}: {score}"
            if str(player_id) == str(self.client.player_id):
                text += " (YOU)"
            score_text = self.font_small.render(text, True, self.TEXT_COLOR)
            board_surface.blit(score_text, (padding, y))
            y += entry_height
        
        self.screen.blit(board_surface, (self.width - board_width - padding, padding))

    def draw_controls(self):
        """Draw control instructions"""
        controls = [
            "Controls:",
            "W - Move forward",
            "A - Turn left",
            "D - Turn right",
            "F - Toggle FPS"
        ]
        
        y = self.height - (len(controls) * 25 + 10)
        for text in controls:
            rendered_text = self.font_small.render(text, True, self.TEXT_COLOR)
            self.screen.blit(rendered_text, (10, y))
            y += 25

    def draw_fps(self):
        """Draw FPS counter"""
        if self.show_fps:
            fps = int(self.clock.get_fps())
            fps_text = self.font_small.render(f"FPS: {fps}", True, self.TEXT_COLOR)
            self.screen.blit(fps_text, (10, 10))

    def draw_collision_flash(self):
        """Draw collision flash effect"""
        current_time = pygame.time.get_ticks()
        if current_time - self.flash_start < self.flash_duration:
            alpha = int(255 * (1 - (current_time - self.flash_start) / self.flash_duration))
            flash_surface = pygame.Surface((self.width, self.height))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(alpha)
            self.screen.blit(flash_surface, (0, 0))

    def draw(self):
        """Main draw method"""
        if not self.game_state:
            return

        self.draw_background()
        
        # Draw game elements
        if "foods" in self.game_state:
            self.draw_food(self.game_state["foods"])
        
        for player_id, ball_data in self.game_state.get("ball", {}).items():
            self.draw_player(int(player_id), ball_data)
        
        # Draw UI elements
        self.draw_scoreboard()
        self.draw_controls()
        self.draw_fps()
        self.draw_collision_flash()
        
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running and self.client.running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(60)

        pygame.quit()