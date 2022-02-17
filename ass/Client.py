# COMP3331 Assignment
# Author: Jiaqi Zhu
# Python 3.7.3
# References: 
# - Wei Song's Multi-threading video and Multi-threaded Code (Python) 
# - Simple TCP Chat Room in Python (video tutorial): https://www.youtube.com/watch?v=3UOyky9sEQY
from socket import *
from threading import Thread
import sys
import time

if len(sys.argv) < 1:
    print('\n===== Error usage, python3 client.py SERVER_PORT ======\n')
    exit(0)
serverHost = '127.0.0.1'
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(serverAddress)

# Thread for sending request to server
def write():
    while True:
        try:
            message = input('')
            clientSocket.send(message.encode())
            if message == 'logout':
                break
        except:
            print('User disconnected!')
            clientSocket.close()
            break

# Thread for receiving messages from server
def receive():
    while True:
        try:
            message = clientSocket.recv(1024).decode()
            if message == 'username':
                print('Username: ', end='')
            elif message == 'password':
                print('Password: ', end='')
            elif message == 'new password':
                print('This is a new user. Enter a password: ', end='')
            elif message == 'invalid password':
                print('Invalid password. Please try again.')
                print('Password: ', end='')
            elif message == 'active':
                print('This user has already logged in.')
            elif message == 'blocked':
                print('Invalid Password. Your account has been blocked. Please try again later.\n')
                clientSocket.close()
                break
            elif message == 'still blocked':
                print('Your account is blocked due to multiple login failures. Please try again later.\n')
                clientSocket.close()
                break
            elif message == 'logged in':
                print('Login success! Welcome!')
            elif message == 'logout success':
                print('User has logged out.')
                clientSocket.close()
                break
            else:
                print(message)
        except:
            print('An error occurred!')
            clientSocket.close()
            break

write_thread = Thread(target=write)
write_thread.start()

receive_thread = Thread(target=receive)
receive_thread.start()
