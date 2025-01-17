import math
import time
import random

class Ball:
    def __init__(self, x, y,):
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
    
    def get_status(self):
        print(f"Ball position: {self.x}, {self.y} ball speed: {self.speed} ball direction: {self.direction}")

class Food:
    def __init__(self, x, y):
        self.x = random.randint(0 + 5, 800 - 5)
        self.y = random.randint(0 + 5, 600 - 5)

    def respawn(self):
        self.x = random.randint(0 + 5, 800 - 5)      # +5,-5 -> I don't want it to spawn on the edge
        self.y = random.randint(0 + 5, 600 - 5)

def test_ball():
    ball = Ball(400, 300)
    food = Food(400, 300)
    frame = 0
    
    try:
        while True:
            input_player1 = random.choice([[], ['w'], ['a'], ['d'], ['w', 'a'], ['w', 'd']])
            input_player2 = random.choice([[], ['w'], ['a'], ['d'], ['w', 'a'], ['w', 'd']])
            if 'w' in input_player1:
                ball.move_forward()
            else:
                ball.stop_moving()
                
            if 'a' in input_player1:
                ball.turn_left()
            if 'd' in input_player1:
                ball.turn_right()
           
            ball.move()
            
            frame += 1
            print("\nFrame", frame)
            print(ball.get_status())
            print("food position: ", food.x, food.y)
            if frame % 10 == 0:
                food.respawn()
                print("food respawned")

            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pass
    
    print("\nTest ended")

    
    

if __name__ == "__main__":
    test_ball()



    

