import socket
import json
import re


HOST = '127.0.0.1' 
PORT = 8080 
list_of_ob=[]
with open('web/products.json') as prods:
    list_of_ob=json.load(prods)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f"Listenig on {HOST}:{PORT}")
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]
    status_code=200
    response_content=''
    if path == '/':
        response_content = 'Welcome!'
    elif path== '/home':
        with open('web/homepage.html') as home:
            response_content=home.read()
    elif path== '/about':
        with open('web/aboutpage.html') as about:
            response_content=about.read()
    elif path== '/contact':
        with open('web/contactpage.html') as contact:
            response_content=contact.read()
    elif path== '/products':
        response_content+='List of objects<br>'
        for ob in list_of_ob:
            response_content+=f"<a href='product/{ob['id']}'> Product {ob['name']} </a><br>"
    elif re.match(r"/product/[0-9]+",path):
        id=int(re.split(r"/",path)[2])
        check=0
        p={}
        for ob in list_of_ob:
            if int(ob['id'])==id:
                p=ob
                check+=1
                break
        if check!=0:
            response_content= f"""<p> ID: {p['id']} </p><br>"""+\
                              f"""<p> Name: {p['name']}</p><br>"""+\
                              f"""<p> Author: {p['author']}</p><br>"""+\
                              f"""<p> Price: {p['price']}</p><br>"""+\
                              f"""<p> Description: {p['description']}</p><br>"""
        else:
            response_content='404'
    response = f'HTTP/1.1 200 OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))
    client_socket.close()
