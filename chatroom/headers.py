import enum
import json

class Flag(enum.Enum):
    REPORT_REQUEST_FLAG = 0
    REPORT_RESPONSE_FLAG = 0
    JOIN_REQUEST_FLAG = 0
    JOIN_REJECT_FLAG = 0
    JOIN_ACCEPT_FLAG = 0
    NEW_USER_FLAG = 0
    QUIT_REQUEST_FLAG = 0
    QUIT_ACCEPT_FLAG = 0
    ATTACHMENT_FLAG = 0
    NUMBER = 0
    USERNAME = None
    FILENAME = None
    PAYLOAD = ''
    PAYLOAD_LENGTH = ''

class Headers:

    def __init__(self, **kwargs):
        self.REPORT_REQUEST_FLAG =     int(kwargs.get('REPORT_REQUEST_FLAG', 0))
        self.REPORT_RESPONSE_FLAG =    int(kwargs.get('REPORT_RESPONSE_FLAG', 0))
        self.JOIN_REQUEST_FLAG =       int(kwargs.get('JOIN_REQUEST_FLAG', 0))
        self.JOIN_REJECT_FLAG =        int(kwargs.get('JOIN_REJECT_FLAG', 0))
        self.JOIN_ACCEPT_FLAG =        int(kwargs.get('JOIN_ACCEPT_FLAG', 0))
        self.NEW_USER_FLAG =           int(kwargs.get('NEW_USER_FLAG', 0))
        self.QUIT_REQUEST_FLAG =       int(kwargs.get('QUIT_REQUEST_FLAG', 0))
        self.QUIT_ACCEPT_FLAG =        int(kwargs.get('QUIT_ACCEPT_FLAG', 0))
        self.NUMBER =                  int(kwargs.get('NUMBER', 0))
        self.USERNAME =                kwargs.get('USERNAME', None)
        self.FILENAME =                kwargs.get('FILENAME', None)
        self.PAYLOAD =                 kwargs.get('PAYLOAD', '')
        self.PAYLOAD_LENGTH =          len(kwargs.get('PAYLOAD', ''))

    def set(self, flag: Flag, value: any):
        setattr(self, flag.name, value)

    def get(self, flag: Flag):
        return getattr(self, flag.name)
    
    def generate(self):
        return self.__dict__
    
    def encoded(self):
        return json.dumps(self.generate()).encode('utf-8')
