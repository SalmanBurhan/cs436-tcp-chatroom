from headers import Headers, Flag
from typing import NamedTuple
import socket
import json
import datetime

class User(NamedTuple):
    username: str
    client: socket.socket

class Server:

    def __init__(self, host="0.0.0.0", port=18000):
        self.HOST = host
        self.PORT = port
        self.ACTIVE_USERS = []
        self.CHAT_HISTORY = []
        self.initSocket()

    def initSocket(self):
        self.SOCKET = socket.socket(
            socket.AF_INET,     # IPv4 Network Interface
            socket.SOCK_STREAM  # Socket Type for TCP Protocol
        )
    
    def listen(self):
        self.SOCKET.bind((self.HOST, self.PORT))
        self.SOCKET.listen()
        self.ACTIVE_USERS.append(User(username='Server', client=self.SOCKET))
        print(f'Listening For Connections on {self.HOST}:{self.PORT}')
        while True:
            client, address = self.SOCKET.accept()
            print(f'Connection Established With {address[0]}:{address[1]}')
            if not (data := client.recv(1024).decode('utf-8')): break
            response = Headers(**json.loads(data))
            self.parse_response(client, response)
            #client.sendall(data)
            
        self.destroySocket()

    def destroySocket(self):
        print(f'Stopping All Listening Activity On *:{self.PORT}')
        self.SOCKET.close()
    
    def chat_entry(self, message: str, user: User):
        timestamp = datetime.datetime.strftime('%m-%d-%Y, %I:%M:%S:%p')
        self.CHAT_HISTORY.append(
            f'[{timestamp}] {user.username} - {message}'
        )
        response = Headers(PAYLOAD="\n".join(self.CHAT_HISTORY))
        self.SOCKET.send(response)

    def parse_response(self, client: socket.socket, response: Headers):
        # print(response.generate())
        # print(f'Flag.JOIN_REQUEST_FLAG = {response.JOIN_REQUEST_FLAG}')
        # print(f'Flag.USERNAME = {response.USERNAME}')
        if response.get(Flag.JOIN_REQUEST_FLAG) == 1:
            self.new_user(User(username = response.get(Flag.USERNAME), client=client))
        else:
            pass

    def announce_new_user(self, user: User):
        response = Headers()
        response.set(Flag.NEW_USER_FLAG, 1)
        response.set(Flag.USERNAME, user.username)
        response.set(Flag.PAYLOAD, f'{user.username} has joined the chatroom!')
        user.client.send(response.encoded())

    def new_user(self, user: User):
        response = Headers()
        response.set(Flag.JOIN_REQUEST_FLAG, 0)
        if user in self.ACTIVE_USERS:
            response.set(Flag.JOIN_REJECT_FLAG, 1)
            response.set(Flag.PAYLOAD, f'Unable To Join, Another User Exists With The Username: {user.username}')
            user.client.send(response.encoded())
        elif len(self.ACTIVE_USERS) > 2:
            response.set(Flag.JOIN_REJECT_FLAG, 1)
            response.set(Flag.PAYLOAD, f'Unable To Join. Currently At Maximum Capacity')
            user.client.send(response.encoded())
        else:
            response.set(Flag.JOIN_ACCEPT_FLAG, 1)
            response.set(Flag.USERNAME, user.username)
            response.set(Flag.PAYLOAD, "\n".join(self.CHAT_HISTORY))
            user.client.send(response.encoded())
            self.announce_new_user(user)
        
if __name__ == '__main__':
    try:
        server = Server()
        server.listen()
    except KeyboardInterrupt:
        server.destroySocket()