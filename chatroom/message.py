from datetime import datetime
import json

def timestamp() -> str:
    return datetime.datetime.now().strftime('%m-%d-%Y, %I:%M:%S %p')

class Message:
    
    def __init__(self, **kwargs):

        
        # Internal Property     =               JSON Key        Default
        self._status_request    = kwargs.get('status_request',  False)
        self._status_response   = kwargs.get('status_response', False)
        self._user_count        = kwargs.get('user_count',         -1)
        self._join_request      = kwargs.get('join_request',    False)
        self._join_accept       = kwargs.get('join_accept',     False)
        self._join_reject       = kwargs.get('join_reject',     False)
        self._join_announce     = kwargs.get('join_announce',   False)
        self._quit_request      = kwargs.get('quit_request',    False)
        self._quit_accept       = kwargs.get('quit_accept',     False)
        self._username          = kwargs.get('username',        'Server')
        self._filename          = kwargs.get('filename',        None)
        self._content           = kwargs.get('content',         None)
        self._timestamp         = kwargs.get('timestamp',       datetime.now())
    
    @property
    def is_status_request(self):
        """ Get or set whether this message is a request to obtain the Chatroom Status. """
        return self._status_request
    
    @is_status_request.setter
    def is_status_request(self, value: bool):
        self._status_request = value
    
    @property
    def is_status_response(self):
        """ Get or set whether this message is a response to a Status Request. """
        return self._status_response
    
    @is_status_response.setter
    def is_status_response(self, value: bool):
        self._status_response = value
    
    @property
    def user_count(self):
        return self._user_count
    
    @user_count.setter
    def user_count(self, value: int):
        self._user_count = value

    @property
    def is_join_request(self):
        """ Get or set whether this message is a request to join the chatroom. """
        return self._join_request
    
    @is_join_request.setter
    def is_join_request(self, value: bool):
        self._join_request = value
    
    @property
    def is_join_accept(self):
        """ Get or set whether this message is an acceptance of a join request. """
        return self._join_accept
    
    @is_join_accept.setter
    def is_join_accept(self, value: bool):
        self._join_accept = value
    
    @property
    def is_join_reject(self):
        """ Get or set whether this message is a rejection of a join request. """
        return self._join_reject
    
    @is_join_reject.setter
    def is_join_reject(self, value: bool):
        self._join_reject = value
    
    @property
    def is_join_announce(self):
        """ Get or set whether this message is an announcement of a new user. """
        return self._join_announce
    
    @is_join_announce.setter
    def is_join_announce(self, value: bool):
        self._join_announce = value
    
    @property
    def is_quit_request(self):
        """ Get or set whether this message is a request to exit the chatroom. """
        return self._quit_request
    
    @is_quit_request.setter
    def is_quit_request(self, value: bool):
        self._quit_request = value
    
    @property
    def is_quit_accept(self):
        """ Get or set whether this message confirms the exit of a user from the chatroom. """
        return self._quit_accept
    
    @is_quit_accept.setter
    def is_quit_accept(self, value: bool):
        self._quit_accept = value
    
    @property
    def username(self):
        """ Get or set the username of the user sending this message. """
        return self._username
    
    @username.setter
    def username(self, value: str):
        self._username = value
    
    @property
    def filename(self):
        """ Get or set the filename of the attachment associated with this message. """
        return self._filename
    
    @filename.setter
    def filename(self, value: str):
        self._filename = value
    
    @property
    def content(self):
        """ Get or set the contents of this message. """
        return self._content
    
    @content.setter
    def content(self, value: str):
        self._content = value if value else ""
    
    @property
    def content_length(self):
        """ Returns the length of the content of this message. """
        return len(self._content) if self._content else 0
    
    @property
    def timestamp(self):
        return self._timestamp.strftime('%m-%d-%Y, %I:%M:%S %p')
    
    @timestamp.setter
    def formatted_timestamp(self, date_str: str):
        self._timestamp = datetime.strptime(date_str, '%m-%d-%Y, %I:%M:%S %p')

    def to_json(self):
        return json.dumps(self, cls=MessageEncoder, sort_keys=True) + "\n"
    
    def serialize(self):
        return self.to_json().encode('utf-8')

class MessageEncoder(json.JSONEncoder):
    
    def default(self, o: Message):
        if not isinstance(o, Message):
            raise TypeError(f'Unexpected Type: {o.__class__.__name__}')
        return {
            'status_request': o.is_status_request,
            'status_response': o.is_status_response,
            'user_count': o.user_count,
            'join_request': o.is_join_request,
            'join_accept': o.is_join_accept,
            'join_reject': o.is_join_reject,
            'join_announce': o.is_join_announce,
            'quit_request': o.is_quit_request,
            'quit_accept': o.is_quit_accept,
            'username': o.username,
            'filename': o.filename,
            'content': o.content,
            'content_length': o.content_length,
            'timestamp': o.timestamp
        }

class MessageDecoder(json.JSONDecoder):

    def __init__(self, **kwargs):
        kwargs.setdefault("object_hook", self.object_hook)
        super().__init__(**kwargs)

    def object_hook(self, d: dict):
        if (timestamp := d.get('timestamp')):
            timestamp = datetime.strptime(timestamp, '%m-%d-%Y, %I:%M:%S %p')
        else:
            timestamp = datetime.now()

        return Message(
            status_request      = d.get('status_request'),
            status_response     = d.get('status_response'),
            user_count          = d.get('user_count'),
            join_request        = d.get('join_request'),
            join_accept         = d.get('join_accept'),
            join_reject         = d.get('join_reject'),
            join_announce       = d.get('join_announce'),
            quit_request        = d.get('quit_request'),
            quit_accept         = d.get('quit_accept'),
            username            = d.get('username'),
            filename            = d.get('filename'),
            content             = d.get('content'),
            content_length      = d.get('content_length'),
            timestamp           = timestamp
        )