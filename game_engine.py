import math
import random

class Ball:
    def __init__(self, radius, color, x, y):
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
        self.speed = 0
        self.direction = 0
        self.score = 0

    def move_forward(self, max_speed=10):
        self.speed = min(self.speed + 1, max_speed)
    
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

        # Boundary checking
        self.x = min(max(self.x, self.radius), 800 - self.radius)
        self.y = min(max(self.y, self.radius), 600 - self.radius)

class Food:
    def __init__(self):
        self.radius = 5
        self.respawn()

    def respawn(self):
        margin = self.radius * 2
        self.x = random.randint(margin, 800 - margin)
        self.y = random.randint(margin, 600 - margin)

class Game_logic:
    def __init__(self):
        # Initialize with random starting positions for players
        self.players = {
            1: Ball(15, (255, 0, 0), random.randint(50, 750), random.randint(50, 550)),
            2: Ball(15, (0, 255, 0), random.randint(50, 750), random.randint(50, 550))
        }
        self.control = {
            1: {'w': False, 'a': False, 'd': False},
            2: {'w': False, 'a': False, 'd': False}
        }
        self.food = Food()
        self.frame = 0
        self.respawn_time = 100
        self.scores = {1: 0, 2: 0}
    
    def set_control(self, player, key, state):
        if player in self.control and key in self.control[player]:
            self.control[player][key] = state
    
    def check_collision(self, ball, food):
        distance = math.sqrt((ball.x - food.x) ** 2 + (ball.y - food.y) ** 2)
        return distance < (ball.radius + food.radius)

    def update(self):
        self.frame += 1
        game_event = {"collision": [], "respawn": []}
        
        # Update player positions and check collisions
        for player_id, ball in self.players.items():
            control = self.control[player_id]
            
            # Handle movement
            if control['w']:
                ball.move_forward()
            else:
                ball.stop_moving()
            
            if control['a']:
                ball.turn_left()
            
            if control['d']:
                ball.turn_right()
            
            ball.move()

            # Check collision with food
            if self.check_collision(ball, self.food):
                game_event['collision'].append(player_id)
                self.scores[player_id] += 1
                ball.score = self.scores[player_id]
                self.food.respawn()

        # Periodic food respawn
        if self.frame % self.respawn_time == 0:
            self.food.respawn()
            game_event['respawn'].append(1)
        
        return game_event
    
    def get_game_data(self):
        return {
            "ball": {
                str(pid): {
                    "radius": ball.radius,
                    "color": ball.color,
                    "x": ball.x,
                    "y": ball.y,
                    "speed": ball.speed,
                    "direction": ball.direction,
                    "score": self.scores[pid]
                }
                for pid, ball in self.players.items()
            },
            "foods": {
                "radius": self.food.radius,
                "x": self.food.x,
                "y": self.food.y
            },
            "frame": self.frame
        }
