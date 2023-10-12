import socket
import threading
import json
import base64
from PIL import Image
import re
from io import BytesIO
from PIL import Image
import os
import uuid

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to {host}:{port}")
    return client_socket

def save_image_in_current_folder(image):
    try:
        # Get the current directory where the script/exe is located
        current_directory = os.path.dirname(os.path.realpath(__file__))
        
        # Generate a random filename
        random_filename = str(uuid.uuid4())[:8]  # You can adjust the length of the random filename

        # Determine the file format based on the image format
        file_extension = "jpg" if image.format == "JPEG" else "png"

        # Create the full path to save the image in the current directory
        save_path = os.path.join(current_directory, f"{random_filename}.{file_extension}")

        # Save the image
        image.save(save_path)

        print(f"Image saved as {save_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
def extract_path(upload_string):
    # Define the regular expression pattern to extract the path
    pattern = r"upload\('(.+?)'\)"

    # Use re.search to find the match
    match = re.search(pattern, upload_string)

    if match:
        path = match.group(1)
        return path
    else:
        return None
    
def decode_base64_image(base64_string):
    try:
        # Decode the Base64 string into bytes
        image_bytes = base64.b64decode(base64_string)

        # Create a BytesIO object to work with Pillow
        image_buffer = BytesIO(image_bytes)

        # Open the image using Pillow
        img = Image.open(image_buffer)

        return img
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
def load_image_by_path(path):
    try:
        img = Image.open(path)
        return(img)
    except FileNotFoundError:
        print(f"Image not found at the specified path: {path}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def is_upload_string(upload_string):
    # Define the regular expression pattern to match the format
    pattern = r"^upload\('(.+?)'\)$"

    # Use re.match to check if the string matches the pattern
    match = re.match(pattern, upload_string)

    return match is not None

def is_download_string(download_string):
    # Define the regular expression pattern to match the format
    pattern = r"^download$"

    # Use re.match to check if the string matches the pattern
    match = re.match(pattern, download_string)

    return match is not None

def image_to_base64(img):
    try:
        
        if isinstance(img, Image.Image):
            img_bytes = img.tobytes()
            base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
            return base64_encoded
        else:
            print("Input is not a Pillow Image object.")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
def receive_messages(client_socket):
    upload=[]
    while True:
        try:
            data = client_socket.recv(680000).decode('utf-8')
            if not data:
                break

            message = json.loads(data)
            
            handle_message(message,upload)
            
            
        except Exception as e:
            print(f"Error receiving messages: {e}")
            break

def handle_message(message,upload):
    message_type = message.get("type")
    payload = message.get("payload")
    base64_image=''
    if message_type == "connect_ack":
        connect_message = payload.get("message")
        print(f"\nServer: {connect_message}")
        print("\nEnter a message (or 'exit' to quit): ")
    elif message_type == "message":
        sender = payload.get("sender")
        room = payload.get("room")
        text = payload.get("text")
        base64_image=payload.get("image")
        #print(base64_image)
        upload.append(base64_image)    
        if is_download_string(text.lower()):
                print('123')
                print(upload[0])
                image=decode_base64_image(upload[0])
                save_image_in_current_folder(image)
                print('Saved')
        print(f"\n{sender} in '{room}': {text}")
        print("\nEnter a message (or 'exit' to quit): ")
    elif message_type == "notification":
        notification_message = payload.get("message")
        print(f"Notification: {notification_message}")
    else:
        print("Unknown message type")

def send_message(client_socket,room,name):
    while True:
        base64_image=''
        message = input("\nEnter a message (or 'exit' to quit or 'upload'): ")

        if message.lower() == 'exit':
            break
        if is_upload_string(message.lower()):
            path=extract_path(message)
            image=load_image_by_path(path)
            base64_image=image_to_base64(image)
            
            
           
        message_data = {
            "type": "message",
            "payload": {
                "sender": name,
                "room": room,
                "text": message,
                "image":base64_image
            }
        }
        client_socket.send(json.dumps(message_data).encode('utf-8'))

    client_socket.close()
def connect_room(client_socket,room,name):
        message_data = {
            "type": "connect",
            "payload": {
                "sender": name,
                "room": room,
                "text": 'connected to room'
            }
        }
        client_socket.send(json.dumps(message_data).encode('utf-8'))
    
        
if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 12345

    client_socket = connect_to_server(HOST, PORT)
    name=input("Enter a name:")
    room=input("Enter a room:")
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    connect_room(client_socket,room,name)
    send_message(client_socket,room,name)
