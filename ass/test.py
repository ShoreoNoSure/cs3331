import sys

def get_password():
    f = open('credentials.txt', 'r')
    lines = f.readlines()
    f.close()
    for l in lines:
        user = l.strip('\n').split(' ')
        print(user)

if __name__ == "__main__":
    get_password()
