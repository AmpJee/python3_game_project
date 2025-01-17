import socket
import sys
import threading
import json
import time
from test_game_engine import Game_logic

HOST = '0.0.0.0'
PORT = 21002
s = None
clients = []
client_ids = {}
clients_lock = threading.Lock()
game_logic = Game_logic()


def broadcast(game_data):

    with clients_lock:
        disconnected_clients = []
        for client in clients:
            try:
                client.sendall((json.dumps(game_data) + "\n").encode())

            except ConnectionError:
                print("Error sending data to client")
                disconnected_clients.append(client)
        for client in disconnected_clients:
            clients.remove(client)


def remove_client(client_socket):
    with clients_lock:
        if client_socket in clients:
            player_id = client_ids.get(client_socket)
            clients.remove(client_socket)
            if client_socket in client_ids:
                del client_ids[client_socket]
            if player_id in game_logic.players:
                del game_logic.players[player_id]
            if player_id in game_logic.controls:
                del game_logic.controls[player_id]
    try:
        client_socket.close()
    except ConnectionError:
        print("Error closing client socket")
    print(f"Player {player_id} disconnected.")


def handle_client(client_socket, player_id):
    with clients_lock:
        clients.append(client_socket)
        client_ids[client_socket] = player_id
    init_message = json.dumps({"player_id": player_id}) + "\n"
    client_socket.sendall(json.dumps({"player_id": player_id}).encode())
    buffer = ""
    while True:
        try:
            data = client_socket.recv(32).decode()
            if not data:
                print(f"Player {player_id} disconnected.")
                break
            buffer += data
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                control_data = json.loads(message)
                if control_data["type"] == "input":
                    game_logic.set_control(
                        player_id, control_data["key"], control_data["state"])
        except ConnectionError:
            print(f"Connection error with Player {player_id}.")
            break

    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in client_ids:
            del client_ids[client_socket]
    client_socket.close()
    print(f"Player {player_id} disconnected.")
    remove_client(client_socket)


def game_loop():
    while True:
        game_events = game_logic.update()
        game_data = game_logic.get_game_data()
        game_data['events'] = game_events
        broadcast(game_data)
        time.sleep(0.05)


def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket created")
    except OSError as msg:
        s = None
        print(f"Error creating socket: {msg}")
        exit(1)

    try:
        s.bind((HOST, PORT))
        s.listen()
        print("Socket bound and listening")
    except OSError as msg:
        print("Error binding/listening!")
        s.close()
        exit(1)

    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    player_id = 1
    while True:
        try:
            conn, addr = s.accept()
            print(f"Connected to {addr}")
            client_thread = threading.Thread(
                target=handle_client, args=(conn, player_id), daemon=True)
            client_thread.start()
            player_id += 1
        except KeyboardInterrupt:
            print("Closing server")
            s.close()
            break
    if s:
        s.close()
        print("Server closed")


if __name__ == "__main__":
    main()
