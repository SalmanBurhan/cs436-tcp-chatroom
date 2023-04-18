from message import Message, MessageDecoder
from server_address import ServerAddress
from connection import Connection
from typing import List, Dict
import datetime
import asyncio
import json
import logging
import base64

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s:%(levelname)s:%(name)s - %(message)s'
)

class ChatroomServer:

    def __init__(self, address: ServerAddress = ServerAddress()):
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        self.event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.address = address
        self.users: Dict[str, Connection] = {}
        self.chat_history: List[Message] = []

        self.logger.debug('ChatroomServer class initialized.')

    def startup(self):
        self.server_task = self.event_loop.create_task(self._run(), name='Server')
        self.event_loop.run_forever()
        
        #self.server = await asyncio.start_server(self.awk, self.address.host, self.address.port)
        #await self.server.serve_forever()

    async def _run(self):
        self.server = await asyncio.start_server(self.awk, host=self.address.host, port=self.address.port)
        async with self.server:
            self.logger.info(f'Listening on {self.address.host}:{self.address.port}')
            await self.server.serve_forever()

    async def broadcast(self, message: Message):
        self.chat_history.append(message)
        serialized_message = message.serialize()
        for username, user in self.users.items():
            self.logger.info(f'Forwarding Content From @{message.username} to @{username}.')
            user.writer.write(serialized_message)
            await user.writer.drain()

    async def server_status(self, connection: Connection):
        message = Message()
        message.is_status_response = True
        message.user_count = len(self.users)
        content = ''
        for i, (username, user) in enumerate(self.users.items()):
            content += f'{i+1}) @{username} is Connected at {user.host}:{user.port}\n'
        message.content = content
        self.logger.info('Sending Server Status and Statistics')
        connection.writer.write(message.serialize())
        await connection.writer.drain()
        connection.writer.close()
        await connection.writer.wait_closed()

    async def listener(
        self,
        connection: Connection
    ):
        while True:
            data = (await connection.reader.readline()).decode('utf-8')
            if not data:
                self.logger.info('Empty Data Received. Killing Connection.')
                connection.writer.close()
                await connection.writer.wait_closed()
                break
            self.logger.debug(f'Recieved Client Message: {data.strip()}')
            message = json.loads(data, cls=MessageDecoder)

            if message.is_join_request:
                self.logger.info(f'Received New User Join Request From User @{message.username}.')
                await self.new_user(username=message.username, connection=connection)
            elif message.is_status_request:
                self.logger.info('Received Server Status Request.')
                await self.server_status(connection)
            elif message.is_quit_request:
                self.logger.info(f'Received Quit Request From User @{message.username}.')
                await self.disconnect_user(message.username)
            else:
                if not self.is_user_connected(message.username):
                    self.logger.info('Received Unknown Request Type. Killing Connection.')
                    connection.writer.close()
                    await connection.writer.wait_closed()
                await self.broadcast(message)

    async def awk(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ):
        ip, port = writer.get_extra_info('peername')
        connection = Connection(reader, writer, ip, port)
        await self.listener(connection)


    async def new_user(self, username: str, connection: Connection):

        self.logger.debug(f'Currently Connected Users: {list(self.users.keys())}')
        
        if len(self.users) >= 2:
            self.logger.info('Rejecting New User Join Request. Reason: Maximum Capacity.')
            connection.writer.write(
                Message(
                    join_reject=True,
                    content=f'Sorry @{username}, The Server Is At Maximum Capacity.'
                ).serialize()
            )
            await connection.writer.drain()
            connection.writer.close()
            await connection.writer.wait_closed()

        elif username in list(self.users.keys()):
            self.logger.info('Rejecting New User Join Request. Reason: User Exists.')
            connection.writer.write(
                Message(
                    join_reject=True,
                    content=f'A User By The Name @{username} Is Already In This Chatroom.'
                ).serialize()
            )
            await connection.writer.drain()
            connection.writer.close()
            await connection.writer.wait_closed()

        else:
            self.logger.info('Accepting New User Join Request.')
            self.users[username] = connection
            self.logger.info('Sending Chat History To New User.')
            connection.writer.write(
                Message(
                    join_accept=True,
                    username=username,
                    content=self.formatted_chat_history
                ).serialize()
            )
            await connection.writer.drain()
            self.logger.info('Broadcasting New User Announcement.')
            await self.broadcast(
                Message(
                    join_announce=True,
                    username='Server',
                    content=f'@{username} Has Joined The Chat.'
                )
            )

        self.logger.debug(f'Currently Connected Users: {list(self.users.keys())}')

    def is_user_connected(self, username: str) -> bool:
        return username.lower() in list(map(lambda s: s.lower(), list(self.users.keys())))
    
    async def disconnect_user(self, username: str):
        if (connection := self.users.get(username)):
            try:
                self.logger.info(f'Accepting Quit Request From @{username}')
                message = Message(
                    quit_accept = True,
                    content=f'@{username} Has Left The Chat.',
                    username=username
                )
                await self.broadcast(message)
                self.users.pop(username) # AKA True
            except KeyError:
                return
        return

    @property
    def formatted_chat_history(self):
        message_history = ""
        for message in self.chat_history:
            if message.filename is not None:
                file_contents = base64.b64decode(message.content).decode()
                message_history += f'[{message.timestamp}] @{message.username}: * sent an attachment: `{message.filename}`\n'
                message_history += f'----\nFile Contents\n----\n{file_contents}\n'
            else:
                message_history += f'[{message.timestamp}] @{message.username}: {message.content.strip()}\n'
        return message_history

if __name__ == '__main__':
    server = ChatroomServer()
    server.startup()
