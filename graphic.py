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
        self.BACKGROUND_COLOR = (240, 240, 240)  # Light gray
        self.FOOD_COLOR = (255, 215, 0)  # Golden
        self.TEXT_COLOR = (50, 50, 50)  # Dark gray

        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Initialize flash effect for collision
        self.flash_start = 0
        self.flash_duration = 200  # milliseconds

        # Score tracking
        self.scores = {}

        # FPS toggle
        self.show_fps = True

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
                    # Toggle FPS display
                    self.show_fps = not self.show_fps

        return True

    def update_game_state(self, state, events):
        """Update game state from server"""
        self.game_state = state
        if not self.game_state:
            return

        # Debug: Check the structure of 'events'
        print(f"events['collision'] type: {type(events['collision'])}")
        print(f"events['collision'] value: {events.get('collision')}")

        # Handle collision events
        if events.get('collision'):
            self.flash_start = pygame.time.get_ticks()

            # If it's not a list, we can't iterate over it
            if isinstance(events['collision'], list):
                # Update scores for both players (make sure it's broadcasting properly)
                for player_id in events['collision']:
                    self.scores[str(player_id)] = self.scores.get(str(player_id), 0) + 10  # 10 points per food
                    print(f"Player {player_id} score updated to {self.scores[str(player_id)]}")
            else:
                print(f"Collision data is not a list: {events['collision']}")

        events = {
    'collision': [1, 2]  # Both Player 1 and Player 2 collected food
}

    def draw_background(self):
        """Draw the game background with grid"""
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw grid
        grid_color = (220, 220, 220)
        grid_spacing = 40

        # Vertical and Horizontal lines
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y))

    def draw_food(self, food_data):
        """Draw food with a glowing effect"""
        if isinstance(food_data, dict):  # Check if food_data is a single dictionary
            x, y = int(food_data["x"]), int(food_data["y"])
            radius = food_data["radius"]

            # Draw food with dynamic glow
            for i in range(5, 0, -1):
                glow_radius = radius + i * 3
                alpha = 30 * i
                pygame.draw.circle(self.screen, (*self.FOOD_COLOR, alpha), (x, y), glow_radius, width=1)
            
            pygame.draw.circle(self.screen, self.FOOD_COLOR, (x, y), radius)
        elif isinstance(food_data, list):  # Handle food_data as a list
            for food in food_data:
                if isinstance(food, dict):
                    x, y = int(food["x"]), int(food["y"])
                    radius = food["radius"]
                    # Draw food with dynamic glow
                    for i in range(5, 0, -1):
                        glow_radius = radius + i * 3
                        alpha = 30 * i
                        pygame.draw.circle(self.screen, (*self.FOOD_COLOR, alpha), (x, y), glow_radius, width=1)
                    pygame.draw.circle(self.screen, self.FOOD_COLOR, (x, y), radius)
                else:
                    print(f"Expected food to be a dict, but got {type(food)}")
        else:
            print(f"Expected food_data to be a dict or list, but got {type(food_data)}")


    def check_food_collision(self, player_data, food_data):
        """Check if a player has collided with food"""
        player_x, player_y = int(player_data["x"]), int(player_data["y"])
        player_radius = player_data["radius"]
        
        food_x, food_y = int(food_data["x"]), int(food_data["y"])
        food_radius = food_data["radius"]

        # Check if player collides with food
        distance = math.sqrt((player_x - food_x) ** 2 + (player_y - food_y) ** 2)
        if distance < player_radius + food_radius:
            return True
        return False

    def draw_player(self, player_id, ball_data):
        """Draw a player ball with direction indicator and name"""
        x, y = int(ball_data["x"]), int(ball_data["y"])
        color = ball_data["color"]
        radius = ball_data["radius"]

        # Draw the ball
        pygame.draw.circle(self.screen, color, (x, y), radius)

        # Draw direction indicator
        direction = ball_data["direction"]
        end_x = x + math.cos(math.radians(direction)) * (radius + 10)
        end_y = y + math.sin(math.radians(direction)) * (radius + 10)
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (end_x, end_y), 2)

        # Draw player ID and score
        score = self.scores.get(player_id, 0)
        player_text = f"P{player_id} (Score: {score})"
        if player_id == str(self.client.player_id):
            player_text += " (YOU)"

        text_surface = self.font_small.render(player_text, True, self.TEXT_COLOR)
        self.screen.blit(text_surface, (x - radius, y - radius - 20))

    def draw_scoreboard(self):
        """Draw scoreboard in the top-right corner"""
        if not self.game_state:
            return

        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        # Scoreboard container
        scoreboard_width = 200
        scoreboard_height = len(sorted_scores) * 30 + 50
        scoreboard_surface = pygame.Surface((scoreboard_width, scoreboard_height))
        scoreboard_surface.set_alpha(200)
        scoreboard_surface.fill((255, 255, 255))

        # Title
        title = self.font_large.render("Scoreboard", True, self.TEXT_COLOR)
        scoreboard_surface.blit(title, (10, 10))

        # Player scores
        y_offset = 50
        for player_id, score in sorted_scores:
            player_text = f"Player {player_id}: {score}"
            if player_id == str(self.client.player_id):
                player_text += " (YOU)"
            score_text = self.font_small.render(player_text, True, self.TEXT_COLOR)
            scoreboard_surface.blit(score_text, (10, y_offset))
            y_offset += 30

        # Draw to screen
        self.screen.blit(scoreboard_surface, (self.width - scoreboard_width - 10, 10))

    def draw_controls(self):
        """Draw control instructions"""
        controls = [
            "Controls:",
            "W - Move forward",
            "A - Turn left",
            "D - Turn right",
            "F - Toggle FPS display",
        ]

        y_offset = self.height - (len(controls) * 25 + 10)
        for text in controls:
            control_text = self.font_small.render(text, True, self.TEXT_COLOR)
            self.screen.blit(control_text, (10, y_offset))
            y_offset += 25

    def draw_fps(self):
        """Draw the current frames per second"""
        fps = int(self.clock.get_fps())
        fps_text = self.font_small.render(f"FPS: {fps}", True, self.TEXT_COLOR)
        self.screen.blit(fps_text, (10, 10))

    def draw(self):
        """Draw the game state"""
        if not self.game_state:
            return

        self.draw_background()

        # Draw food
        self.draw_food(self.game_state["foods"])

        # Draw all players
        for player_id, ball_data in self.game_state["ball"].items():
            self.draw_player(player_id, ball_data)

        # Draw UI elements
        self.draw_scoreboard()
        self.draw_controls()

        # Draw FPS
        if self.show_fps:
            self.draw_fps()

        # Draw collision flash effect
        current_time = pygame.time.get_ticks()
        if current_time - self.flash_start < self.flash_duration:
            alpha = max(0, 255 - int(255 * (current_time - self.flash_start) / self.flash_duration))
            flash_surface = pygame.Surface((self.width, self.height))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(alpha)
            self.screen.blit(flash_surface, (0, 0))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running and self.client.running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
