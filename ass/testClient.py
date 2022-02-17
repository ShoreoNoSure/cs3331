from socket import *
from threading import Thread
import sys, select

# Connect to server
if len(sys.argv) < 1:
    print('\n===== Error usage, python3 client.py SERVER_PORT ======\n')
    exit(0)
serverHost = '127.0.0.1'
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)
client = socket(AF_INET, SOCK_STREAM)
client.connect(serverAddress)

username = input('Username: ')

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'username':
                client.send(username.encode())
            elif message == 'active':
                print('This user has already logged in.')
            elif message == 'blocked':
                print('Your account is blocked due to multiple login failures. Please try again later.\n')
                break
            elif message == 'password':
                password = input('Password: ')
                client.send(password.encode())
            else:
                print(message)
        except:
            print('An error occurred!')
            client.close()
            break

def write():
    while True:
        message = f'{username} {input("")}'
        client.send(message.encode())
        
receive_thread = Thread(target=receive)
receive_thread.start()

write_thread = Thread(target=write)
write_thread.start()

