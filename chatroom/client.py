from server_address import ServerAddress
from message import Message, MessageDecoder
import threading
import asyncio
import json
import os
import base64

class ChatroomClient:

    def __init__(self, server_address: ServerAddress = ServerAddress()):
        self.server_addr: ServerAddress = server_address
        self.isConnected: bool = False
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None
        self.username = None
        self.loop = asyncio.get_event_loop()

    async def run(self):
        while not self.isConnected:
            await self.display_menu()

    async def display_menu(self):
        print(  '---------------------------------------------\n' \
                '| Please Choose From The Following Options: |\n' \
                '| 1) Server/Chatroom Status                 |\n' \
                '| 2) Join The Chatroom                      |\n' \
                '| 3) Quit                                   |\n' \
                '---------------------------------------------\n' )
        try:
            if not isinstance((selection := int(input("Option: "))), int) or 3 < selection < 1:
                print('Invalid Response Received, Please Try Again.')
                self.displayMenu()
            elif selection == 3: exit(0)
            elif selection == 1:
                initial_message = Message()
                initial_message.is_status_request = True
                await self.connect(initial_message)
            elif selection == 2:
                username = input("Please enter your desired username: ")
                if len(username) <= 0: print("A username is required to join the chatroom.");
                initial_message = Message()
                initial_message.is_join_request = True
                initial_message.username = username.strip()
                await self.connect(initial_message)
        except KeyboardInterrupt:
            print("\nForce Exitting!"); exit(1)
    
    async def connect(self, initial_message: Message):
        self.reader, self.writer = await asyncio.open_connection(
            host=self.server_addr.host,
            port=self.server_addr.port
        )
        self.writer.write(initial_message.serialize())
        await self.writer.drain()
        await self.listener()

    async def disconnect(self):
        print('Goodbye :)')
        self.writer.close()
        await self.writer.wait_closed()
        self.writer = None
        self.reader = None
        self.username = None
        self.isConnected = False
        exit(0);
    
    async def listener(self):
        while True:
            data = (await self.reader.readline()).decode('utf-8')
            if not (data): return
            message = json.loads(data, cls=MessageDecoder)
            await self.process(message)
    
    def user_input(self):
        while True:
            try:
                content = input('')
                message = Message(username = self.username)
                if content.strip().lower() == ':q':
                    message.is_quit_request = True
                elif content.strip().lower().startswith(':a '):
                    if (filename := content.strip()[3:]) and os.path.exists(filename):
                        with open(filename, 'rb') as f:
                            message.content = base64.b64encode(f.read()).decode()
                            message.filename = os.path.basename(filename)
                    else:
                        message.content = content
                else:
                    message.content = content.strip()
                self.writer.write(message.serialize())
                asyncio.run_coroutine_threadsafe(self.writer.drain(), self.loop)
            except KeyboardInterrupt:
                pass

    async def process(self, message: Message):
        if message.is_status_response:
            print(f'There Is {message.user_count} Active User(s) in the Chat Room.')
            print(message.content)
        elif message.is_join_accept:
            self.username = message.username
            self.isConnected = True
            await self.display(message)
            input_thread = threading.Thread(target=self.user_input)
            input_thread.daemon = True
            input_thread.start()
        elif message.is_join_reject:
            await self.display(message)
        elif message.is_quit_accept:
            print(message.content)
            if message.username == self.username: await self.disconnect()
        else:
            await self.display(message)

    async def display(self, message: Message):
        if message.is_join_accept:
            self.username = message.username
            print(message.content) # Print Server's Pre-Formatted Chat History.
        elif message.filename is not None:
            file_contents = base64.b64decode(message.content)
            print(f'[{message.timestamp}] @{message.username}: * sent an attachment: `{message.filename}` *')
            if message.username != self.username:
                with open(f'downloads/{message.filename}', 'wb+') as f:
                    f.write(file_contents)
                    print(f'----\nAttachment Saved To `downloads/{message.filename}`\n----')
            print(f'----\nFile Contents\n----\n{file_contents.decode()}')
        else:
            # Format The Message Ourself.
            print(f'[{message.timestamp}] @{message.username}: {message.content}')

if __name__ == '__main__':
    client = ChatroomClient()
    asyncio.run(client.run())