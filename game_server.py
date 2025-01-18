import socket
import sys
import threading
import json
import time
from game_engine import Game_logic

class GameServer:
    def __init__(self, host='0.0.0.0', port=21002):
        self.host = host
        self.port = port
        self.socket = None
        self.clients = []
        self.client_ids = {}
        self.clients_lock = threading.Lock()
        self.game_logic = Game_logic()
        self.running = True

    def broadcast(self, game_data):
        with self.clients_lock:
            disconnected_clients = []
            for client in self.clients:
                try:
                    client.sendall((json.dumps(game_data) + "\n").encode())
                except:
                    print("Error sending data to client")
                    disconnected_clients.append(client)
            
            for client in disconnected_clients:
                self.remove_client(client)

    def remove_client(self, client_socket):
        with self.clients_lock:
            if client_socket in self.clients:
                player_id = self.client_ids.get(client_socket)
                self.clients.remove(client_socket)
                if client_socket in self.client_ids:
                    del self.client_ids[client_socket]
                if player_id in self.game_logic.players:
                    del self.game_logic.players[player_id]
                if player_id in self.game_logic.control:
                    del self.game_logic.control[player_id]
                print(f"Player {player_id} disconnected.")
        
        try:
            client_socket.close()
        except:
            pass

    def handle_client(self, client_socket, player_id):
        with self.clients_lock:
            self.clients.append(client_socket)
            self.client_ids[client_socket] = player_id
        
        try:
            init_message = json.dumps({"player_id": player_id}) + "\n"
            client_socket.sendall(init_message.encode())
            
            buffer = ""
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    try:
                        control_data = json.loads(message)
                        if control_data["type"] == "input":
                            self.game_logic.set_control(
                                player_id,
                                control_data["key"],
                                control_data["state"]
                            )
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from player {player_id}")
                        continue
        except:
            print(f"Connection error with Player {player_id}")
        finally:
            self.remove_client(client_socket)

    def game_loop(self):
        while self.running:
            try:
                game_events = self.game_logic.update()
                game_data = self.game_logic.get_game_data()
                game_data['events'] = game_events
                self.broadcast(game_data)
                time.sleep(0.016)  # ~60 FPS
            except Exception as e:
                print(f"Error in game loop: {e}")

    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"Server listening on {self.host}:{self.port}")

            game_thread = threading.Thread(target=self.game_loop, daemon=True)
            game_thread.start()

            player_id = 1
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()
                    print(f"New connection from {addr}")
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, player_id),
                        daemon=True
                    )
                    client_thread.start()
                    player_id += 1
                except socket.error:
                    break

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False
            if self.socket:
                self.socket.close()
            print("Server shutdown complete")

if __name__ == "__main__":
    server = GameServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")