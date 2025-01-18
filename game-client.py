import socket
import sys
import threading
import json
import pygame
from graphic import GameWindow


HOST = '127.0.0.1'
PORT = 21001
s = None
running = True


class Client:
    def __init__(self):
        self.socket = None
        self.player_id = None
        self.running = True
        self.window = None
        self.recieve_thread = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            print("Connected to server")
            init_data = self.receive_message()
            if not init_data:
                raise ConnectionError("Failed to connect to server")
            self.player_id = init_data["player_id"]
            print(f"Player {self.player_id} connected")
            self.recieve_thread = threading.Thread(
                target=self.recieve_data, daemon=True)
            self.recieve_thread.start()
            return True
        except ConnectionError as e:
            print(f"Connection error: {e}")
            if self.socket:
                self.socket.close()
            return False

    def receive_message(self):
        data = self.socket.recv(32).decode()
        if not data:
            return None
        return json.loads(data)

    def send_input(self, key, state):
        if not self.socket:
            return
        message = {
            "type": "input",
            "key": key,
            "state": state
        }
        self.socket.sendall((json.dumps(message) + "\n").encode())

    def recieve_data(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(32).decode()
                if not data:
                    print("Connection lost!")
                    break
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    game_state = json.loads(message)
                    if self.window:
                        self.window.update_game_state(
                            game_state, game_state.get("events", []))
            except ConnectionError:
                print("Server disconnected")
                break
        self.disconnect()
        

    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None

    def run(self):
        if not self.connect():
            return
        try:
            self.window = GameWindow(self)
            self.window.run()
        finally:
            self.disconnect()


def main():
    client = Client()
    client.run()
    print("Client finished")


if __name__ == "__main__":
    main()