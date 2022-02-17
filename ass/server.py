# COMP3331 Assignment
# Author: Jiaqi Zhu
# Python 3.7.3
# References: Wei Song's Multi-threading video and Multi-threaded Code (Python) 
from socket import *
from threading import Thread
from time import time
import sys, select

# Command line arguments
if len(sys.argv) != 4:
    print('Usage: python3 server.py SERVER_PORT BLOCK_DURATION TIMEOUT')
    exit(0)
serverHost = '127.0.0.1'
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)
# block_duration: the duration in seconds for which a user should be blocked after
block_duration = int(sys.argv[2])
# timeout: the duration in seconds of inactivity after which a user is logged off by the server.
timeout = int(sys.argv[3])

# User class
class User:
    def __init__(self, username, password, block_duration, timeout):
        self.__username = username
        self.__password = password
        self.__block_duration = block_duration
        self.__timeout = timeout
        self.__online = False
        self.__blocked = False
        self.__blocked_since = 0
        self.__last_active = time()

    def is_blocked(self):
        return self.__blocked
    
    def start_block_duration(self):
        self.__blocked = True
        self.__blocked_since = time()

    def update_block_duration(self):
        if self.__blocked_since + self.__blocked_duration < time():
            self.__blocked_since = 0
            self.__blocked = False
    
    def is_online(self):
        return self.__online

    def set_online(self):
        self.__online = True
    
    def set_offline(self):
        self.__online = False

    def password_matches(self, password):
        if self.__password == password:
            return True
        else:
            return False
        
    def update_timeout(self):
        if self.is_online() and self.__last_active + self.__timeout < time():
            self.set_offline()
            return True
        return False
    
    def refresh_timeout(self):
        self.__last_active = time()
        
# Store all valid users 
valid_users = []
valid_usernames = []
try:
    f = open('credentials.txt', 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        username, password = line.strip('\n').split(' ')
        user = User(username, password, block_duration, timeout)
        valid_users.append(user)
        valid_usernames.append(username)
except:
    print('Error reading credentials.txt')
    exit(1)

# Check if user is valid
def user_is_valid(username):
    for u in valid_usernames:
        if u == username:
            return True
    return False

# List of client sockets
client_sockets = [None for _ in range(len(valid_usernames))]

# References of clients and the users they blocked
blacklist = [ [] for _ in range(len(valid_usernames))]

def create_user(username, password):
    user = User(username, password, block_duration, timeout)
    valid_users.append(user)
    valid_usernames.append(username)
    # Add blacklist
    blacklist.append([])
    # Add details to credentials.txt
    credential = username + ' ' + password
    try:
        f = open('credentials.txt', 'a')
        f.write('\n')
        f.write(credential)
        f.close()
        print(credential)
    except:
        print('Error reading credentials.txt')
        exit(1)

# Set up main TCP connection
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)
        
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        
        print('===== New connection created for: ', clientAddress)
        self.clientAlive = True
        
    def run(self):
        message = ''
        while self.clientAlive:
            try:
                # use recv() to receive message from the client
                message = self.clientSocket.recv(1024).decode()
                # handle message from the client
                if message == 'login':
                    print('[recv] New login request')
                    self.process_login()
                elif message == 'logout':
                    print('[recv] New logout request')
                    self.process_logout()
                elif message == 'whoelse':
                    print('[recv] ' + message)
                    self.process_whoelse()
                elif message.split(' ')[0] == 'message':
                    print('[recv] ' + message)
                    recipient_name = message.split(' ')[1]
                    if recipient_name not in valid_usernames:
                        msg = 'Error. Invalid user.'
                        self.clientSocket.send(msg.encode())
                    else:
                        recipient_index = valid_usernames.index(recipient_name)
                        sender_index = client_sockets.index(self.clientSocket)
                        if recipient_index == sender_index:
                            msg = 'You cannot message yourself.'
                            self.clientSocket.send(msg.encode())
                        else:
                            if valid_users[recipient_index].is_online:
                                sender_name = valid_usernames[sender_index]
                                if sender_name in blacklist[recipient_index]:
                                    msg = 'Your message could not be delivered as the recipient has blocked you.'
                                    self.clientSocket.send(msg.encode())
                                else:
                                    msg = sender_name + ': ' + message.split(' ', 2)[2]
                                    client_sockets[recipient_index].send(msg.encode())
                            #else: offline delivery
                elif message.split(' ')[0] == 'broadcast':
                    print('[recv] ' + message)
                    index = client_sockets.index(self.clientSocket)
                    msg = valid_usernames[index] + ': ' + message.split(' ', 1)[1]
                    self.broadcast(msg.encode()) 
                elif message.split(' ')[0] == 'block':
                    print('[recv] ' + message)
                    target = message.split(' ')[1]
                    index = client_sockets.index(self.clientSocket)
                    if valid_usernames[index] == target:
                        msg = 'You cannot block yourself!'
                        self.clientSocket.send(msg.encode())
                    else:
                        if target in blacklist[index]:
                            msg = 'You have already blocked ' + target + '.'
                            self.clientSocket.send(msg.encode())
                        else:
                            blacklist[index].add(target)
                            msg = 'You have successfully blocked ' + target + '.'
                            self.clientSocket.send(msg.encode())
                elif message.split(' ')[0] == 'unblock':
                    print('[recv] ' + message)
                    target = message.split(' ')[1]
                    index = client_sockets.index(self.clientSocket)
                    if valid_usernames[index] == target:
                        msg = 'You cannot unblock yourself!'
                        self.clientSocket.send(msg.encode())
                    else:
                        if target in blacklist[index]:
                            blacklist[index].remove(target)
                            msg = 'You have successfully unblocked ' + target + '.'
                            self.clientSocket.send(msg.encode())
                        else:
                            msg = 'Error. You cannot unblock ' + target + ' because they are not blocked by you.'
                            self.clientSocket.send(msg.encode())
                elif message.split(' ')[0] == 'whoelsesince':
                    print('[recv] ' + message)
                    start = message.split(' ')[1]
                else:
                    print('[recv] ' + message)
                    print('[send] Cannot understand this message')
                    message = 'Cannot understand this message'
                    self.clientSocket.send(message.encode())
            except:
                # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
                self.clientAlive = False
                print('===== the user disconnected - ', self.clientAddress)
                # Broadcast user logout for all clients
                break

    def broadcast(self, message):
        index = client_sockets.index(self.clientSocket)
        print(index)
        for s in client_sockets:
            # Check if socket is sender
            i = client_sockets.index(s)
            recipient = valid_users[i]
            if recipient.is_online() and s != self.clientSocket:
                # Check if client has blocked sender
                b = blacklist[i]
                if b == []:
                    s.send(message)
                elif valid_usernames[index] not in b:
                    s.send(message)
    
    def process_login(self):
        # Request user input username
        message = 'username'
        print('[send] ' + message)
        self.clientSocket.send(message.encode())
        # Receive username
        username = self.clientSocket.recv(1024).decode()
        print('[recv] username: ' + username)
        print(user_is_valid(username))
        # New user
        if not user_is_valid(username):
            # Request for new password
            message = 'new password'
            print('[send] ' + message)
            self.clientSocket.send(message.encode())
            # Receive new password
            new_password = self.clientSocket.recv(1024).decode()
            # Create new user 
            print(new_password)
            create_user(username, new_password)
            # Add client socket
            client_sockets.append(self.clientSocket)
            print('user created')
            message = 'login success'
            print('[send] ' + message)
            self.clientSocket.send(message.encode())
        else:
            processed = False
            print(processed)
            index = valid_usernames.index(username)
            print(index)
            print(valid_users[index].is_online())
            print(valid_users[index].is_blocked())
            # User exists
            if valid_users[index].is_online():
                # User is online
                message = 'active'
                print('[send] ' + message)
                self.clientSocket.send(message.encode())
                processed = True
            elif valid_users[index].is_blocked():
                # User is blocked
                # Check if block duration has passed
                valid_users[index].update_block_duration()
                if valid_users[index].is_blocked():
                    message = 'still blocked'
                    print('[send] ' + message)
                    self.clientSocket.send(message.encode())
                    processed = True
            #print(processed)
            if not processed:
                message = 'password'
                print('[send] ' + message)
                self.clientSocket.send(message.encode())
                password = self.clientSocket.recv(1024).decode()
                # Check password
                count = 3
                while count > 1:
                    if not valid_users[index].password_matches(password):
                        message = 'invalid password'
                        print('[send] ' + message)
                        self.clientSocket.send(message.encode())
                        password = self.clientSocket.recv(1024).decode()
                    else:
                        break
                    count -= 1
                #print(count)
                if count > 1:
                    valid_users[index].set_online()
                    client_sockets[index] = self.clientSocket
                    message = 'logged in'
                    print('[send] ' + message)
                    self.clientSocket.send(message.encode())
                    message = username + ' has logged in!'
                    print('[broadcast] ' + message)
                    self.broadcast(message.encode())
                else:
                    print('User password fails 3 times')
                    valid_users[index].start_block_duration()
                    message = 'blocked'
                    print('[send] ' + message)
                    self.clientSocket.send(message.encode())

    def process_logout(self):
        index = client_sockets.index(self.clientSocket)
        # Broadcast logout msg
        message = valid_usernames[index] + ' has logged out!'
        print('[broadcast] ' + message)
        self.broadcast(message.encode())
        # Inform client logout success
        message = 'logout success'
        print('[send] ' + message)
        self.clientSocket.send(message.encode())
        # Set socket inactive
        self.clientAlive = False
        # Set user offline
        client_sockets[index] = None
        valid_users[index].set_offline()
        print('===== User disconnected - ', self.clientAddress)

    def process_whoelse(self):
        index = client_sockets.index(self.clientSocket)
        print(index)
        whoelse = []
        message = ''
        for user in valid_usernames:
            print(user)
            if valid_usernames.index(user) != index and user not in blacklist[index]:
                whoelse.add(user)
        message = '\n'.join(whoelse)
        print('[send] ' + message)
        self.clientSocket.send(message.encode())

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

while True:
    try:
        serverSocket.listen()
        clientSocket, clientAddress = serverSocket.accept()
        clientThread = ClientThread(clientAddress, clientSocket)
        clientThread.start()
    except KeyboardInterrupt:
        print('\n===== Server is closed =====')
        sys.exit()