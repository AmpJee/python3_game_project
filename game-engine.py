import math
import random


game_data = {}

class Ball:
    def __init__(self, radius, color, x, y,):
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
        self.speed = 0
        self.direction = 0

    def move_forward(self, max_speed=10):
        self.speed = min(self.speed + 1, max_speed) 
    
    def stop_moving(self,):
        self.speed = max(self.speed - 0.3, 0)
    
    def turn_left(self):
        self.direction = (self.direction + 5) % 360
    
    def turn_right(self):
        self.direction = (self.direction - 5) % 360
    
    def move(self):
        angle = math.radians(self.direction)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

        self.x = min(max(self.x, 0), 800)
        self.y = min(max(self.y, 0), 600)

    

class Food:
    def __init__(self,):
        self.radius = 5
        self.x = random.randint(0 + 5, 800 - 5)
        self.y = random.randint(0 + 5, 600 - 5)

    def respawn(self):
        self.x = random.randint(0 + 5, 800 - 5)      # +5,-5 -> I don't want it to spawn on the edge
        self.y = random.randint(0 + 5, 600 - 5)

class Game_logic:
    def __init__(self):
        self.players = {
            1 : Ball(15, (255, 0, 0), 400, 300),
            2 : Ball(15, (0, 255, 0), 400, 300)
        }
        self.control = {
            1 : {'w': False, 'a': False, 'd': False},
            2 : {'w': False, 'a': False, 'd': False}
        }
        self.food = Food()
        self.frame = 0
        self.respawn_time = 100
    
    def set_control(self, player, key, state):       #set the control of the player
        if player in self.players and key in self.control[player]:    # player = 1 or 2, key = 'w', 'a', 'd'
            self.control[player][key] = state       # state = True or False
    
    def check_collision(self, ball, food):          # check if the ball and food collide
        for player in self.players.values():        # player = 1 or 2
            distance = math.sqrt((player.x - self.food.x) ** 2 + (player.y - self.food.y) ** 2)
            return distance < (ball.radius + food.radius)

    def update(self):       # update the game - move the ball, check collision, respawn food
        self.frame += 1
        game_event = {"collision": [], "respawn": []}
        for player_id, ball in self.players.items():
            control = self.control[player_id]
            if control['w']:
                ball.move_forward()
            else:
                ball.stop_moving()
            
            if control['a']:
                ball.turn_left()
            
            if control['d']:
                ball.turn_right()
            
            ball.move()

            if self.check_collision(self.players[1], self.food):
                game_event['collision'].append(1)
                self.players[1].speed += 1
                self.food.respawn()

        if self.frame % self.respawn_time == 0:
            self.food.respawn()
            game_event['respawn'].append(1)
        
        return game_event
    
    def get_game_data(self):       # get the game data
         return {
            "ball":{
            pids:{ 
                "radius": ball.radius,
                "color": ball.color,
                "x": ball.x,
                "y": ball.y,
                "speed": ball.speed,
                "direction": ball.direction,
                }
                for pids, ball in self.players.items()
                },
            "foods": {
                "radius": self.food.radius,
                "x": self.food.x,
                "y": self.food.y     
            },
            "frame": self.frame
            }

          
    