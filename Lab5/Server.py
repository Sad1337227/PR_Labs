import socket
import threading
import json
import base64

def create_server_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server is listening on {host}:{port}")
    return server_socket

def handle_client(server_socket, clients, rooms):
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    print(f"Accepted connection from {client_address}")
    
    while True:
        try:
            data = client_socket.recv(680000).decode('utf-8')
            if not data:
                break
            
            message = json.loads(data)
            handle_message(message, client_socket, rooms)
        
        except Exception as e:
            print(f"Error handling client: {e}")
            break
    
def handle_message(message, client_socket, rooms):
    message_type = message.get("type")
    payload = message.get("payload")
    if message_type == "connect":
        
        name = payload.get("sender")
        room = payload.get("room")
        if room not in rooms:
            rooms[room] = []
        rooms[room].append(client_socket)
        print(f"{name} has joined the room '{room}'")

        response = {
            "type": "connect_ack",
            "payload": {
                "message": "Connected to the room."
            }
        }
        client_socket.send(json.dumps(response).encode('utf-8'))
    elif message_type == "message":
        print(message)
        sender = payload.get("sender")
        room = payload.get("room")
        text = payload.get("text")
        base64_image=payload.get("image")
        
        print(f"Received from {sender} in '{room}': {text} {base64_image}")
        # Broadcast the message to clients in the same room
        if room in rooms:
            for client in rooms[room]:
                if client != client_socket:
                    client.send(json.dumps(message).encode('utf-8'))                
    else:
        print("Unknown message type")

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 12345

    server_socket = create_server_socket(HOST, PORT)
    clients = []
    rooms = {}  # Dictionary to store room information

    while True:
        
        client_thread = threading.Thread(target=handle_client, args=(server_socket, clients, rooms))
        client_thread.start()
        
        
        
