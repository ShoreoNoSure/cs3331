from socket import *
from threading import Thread
import sys, select

# Command line arguments
if len(sys.argv) != 4:
    print('Usage: python3 server.py SERVER_PORT BLOCK_DURATION TIMEOUT')
    exit(0)
server_host = '127.0.0.1'
server_port = int(sys.argv[1])
server_address = (server_host, server_port)
block_duration = int(sys.argv[2])
timeout = int(sys.argv[3])

server = socket(AF_INET, SOCK_STREAM)
server.bind(server_address)
server.listen()

# Active client sockets
clients = []

# Active clients - usernames
usernames = []

# Blocked clients - block timers
blocked = []


def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} left the chat'.encode())
            usernames.remove(username)
            break

def authenticate(username):
    
        
    return ''

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')
        
        authenticated = False
        while not authenticated:
            client.send('username'.encode())
            username = client.recv(1024).decode()
            # User is already active
            if username in usernames:
                client.send('active'.encode())
            # User is blocked
            elif any(username in b for b in blocked):
                client.send('blocked'.encode())
            else:
                # Authenticate
                authenticated = True
                # match_password = authenticate(username) 
            
        usernames.append(username)
        clients.append(client)
        
        print(f'Username of the client is {username}')
        broadcast(f'{username} joined the chat!'.encode())
        client.send('Connected to the server!'.encode())
        
        thread = Thread(target=handle, args=(client,))
        thread.start()

print(f'Server is listening at {server_host}:{server_port}...')
receive()