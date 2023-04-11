from headers import Headers, Flag
import socket, json

class Client:

    def __init__(self, host="0.0.0.0", port=18000):
        self.HOST = host
        self.PORT = port
        self.initSocket()
    
    def initSocket(self):
        self.SOCKET = socket.socket(
            socket.AF_INET,     # IPv4 Network Interface
            socket.SOCK_STREAM  # Socket Type for TCP Protocl
        )
        self.SOCKET.connect((self.HOST, self.PORT))

    def displayMenu(self):
        while True:
            print(f'''Please select one of the following options:
            1   Get a report of the chatroom from the server.
            2   Request to join the chatroom.
            3   Quit the program.''')
            if (isinstance(choice := int(input('Your Choice: ')), int)):
                if choice == 1:
                    pass
                elif choice == 2:
                    username = input('Please enter a username: ')
                    self.new_user_request(username)
                    break
                elif choice == 3:
                    exit(0)
            else:
                print('Invalid Choice...')

    
    def listen_live(self):
        while True:
            if not (data := self.SOCKET.recv(1024)): break
            print(f'Message Received: {data.decode("utf-8")}')
        self.disconnect()

    def disconnect(self):
        print(f'Destroying Connection To {self.HOST}:{self.PORT}')
        self.SOCKET.close()
    
    def new_user_request(self, username):
        request = Headers()
        request.set(Flag.JOIN_REQUEST_FLAG, 1)
        request.set(Flag.USERNAME, username)
        self.SOCKET.send(request.encoded())
        response = self.SOCKET.recv(1024).decode('utf-8')
        print(Headers(**json.loads(response)).generate())
        self.listen_live()

if __name__ == '__main__':
    try:
        client = Client()
        client.displayMenu()
    except KeyboardInterrupt:
        client.disconnect()