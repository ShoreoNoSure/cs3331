from time import time

valid_users = []
def read_credentials():
    try:
        f = open('credentials.txt', 'r')
        username, password = f.readlines()
        for line in lines:
            username, password = line.strip(' ').split()
            user = {
                'username': username,
                'password': password,
            }
            valid_users.append(user)
        f.close()
    except:
        print('Error reading credentials.text')
        exit(1)
# Initialise valid user list
read_credentials()



class User:
    def __init__(self, username: str, password: str, block_duration: int, timeout: int):
        self.__username: str = username
        self.__password: str = password
        self.__block_duration: int = block_duration
        self.__timeout: int = timeout
        self.__online: bool = False
        self.__blocked: bool = False
        self.__blocked_since: int = 0
        self.__last_active: int = int(time())
        self.__blocked_users = list()
    
    def block(self, username: str):
        self.__blocked_users.add(username)
    
    def unblock(self, username: str):
        if username in seld.__blocked_users:
            self.__blocked_users.remove(username)
    
    def has_blocked(self, username: str):
        return username in self.__blocked_users

    def is_blocked(self):
        return self.__blocked

    def update(self):
        if self.is_blocked() and self.__blocked_since + self.__blocked_duration < time():
            self.__blocked = False
    
    def is_online(self):
        return self.__online

    def update_timeout(self):
        if self.is_online() and self.__last_active + self.__timeout < time():
            self.set_offline()
            return True
        return False
    
    def refresh_timeout(self):
        self.__last_active = time()
        
    def authenticate(self, password: str):
        if self.is_online():
            return 'ACTIVE'
        if self.is_blocked():
            return 'BLOCKED'
        if self.__password != password:
            self.__password_fails += 1
            if self.__password_fails == 3:
                self.__blocked_since = time()
                self.__blocked = True
                self.reset_password_fails()
                return 'INVALID_PASSWORD_BLOCKED'
            return 'INVALID_PASSWORD'
                
    
    
        
    
   