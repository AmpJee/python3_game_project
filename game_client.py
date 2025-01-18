import socket
import sys
import threading
import json
import pygame
from graphic import GameWindow

class GameClient:
    def __init__(self, host="127.0.0.1", port=21002):
        self.host = host
        self.port = port
        self.socket = None
        self.playerA_id = None
        self.running = True
        self.window = None
        self.receive_thread = None
        self.BUFFER_SIZE = 1024
        self.input_queue = []
        self.input_lock = threading.Lock()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            init_data = json.loads(self.socket.recv(self.BUFFER_SIZE).decode())
            self.player_id = init_data["player_id"]
            print(f"Connected as Player {self.player_id}")
            
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
            self.receive_thread.start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            if self.socket:
                self.socket.close()
            return False

    def send_input(self, key, state):
        if not self.socket or not self.running:
            return
            
        with self.input_lock:
            message = json.dumps({
                "type": "input",
                "key": key,
                "state": state
            }) + "\n"
            try:
                self.socket.sendall(message.encode())
            except:
                self.running = False

    def receive_data(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(self.BUFFER_SIZE).decode()
                if not data:
                    break
                    
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    game_state = json.loads(message)
                    if self.window:
                        self.window.update_game_state(game_state)
            except:
                break
        
        self.running = False

    def run(self):
        if not self.connect():
            return
            
        try:
            self.window = GameWindow(self)
            self.window.run()
        finally:
            self.running = False
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    client = GameClient()
    client.run()