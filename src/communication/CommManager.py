import socket
from ..static.Constants import SPLITTER

# HOST = '127.0.0.1'  # (localhost)
HOST = '192.168.5.5'  # Standard loopback interface address (localhost)
PORT = 5555  # Port to listen on
BUFFER_SIZE = 4096


class CommManager:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @classmethod
    def connect(cls):
        try:
            cls.client.connect((HOST, PORT))
            print("Connected to the socket-server")
        except socket.error as e:
            print("Couldn't connect to the socket-server: ", str(e))

    @classmethod
    def disconnect(cls):
        cls.client.close()

    # dataArr: an array to hold data to send
    @classmethod
    def sendMsg(cls, commandType, data=None):
        try:
            msg = commandType.value
            if data is not None:
                if isinstance(data, list):
                    for item in data:
                        msg += SPLITTER + str(item)
                else:
                    msg += SPLITTER + str(data)
            msg += "\n"  # At \n to end the command
            cls.client.send(str.encode(msg))
            print('Send msg:', msg)
        except socket.error as e:
            print("Error while sending msg:" + str(e))

    """ Receive an array of message """
    @classmethod
    def recvMsg(cls):
        try:
            msg = cls.client.recv(BUFFER_SIZE)
            msgArr = []
            if msg:
                msg = msg.decode("utf-8")
                msg = msg.replace("\r", "")
                msgArr = msg.split("\n")
                if "" in msgArr:
                    msgArr.remove("")
            for msg in msgArr:
                print('Receive msg:', msg)
            return msgArr
        except socket.error as e:
            print("Error while receiving msg:" + str(e))

    @classmethod
    def sendNormalMsg(cls, msg):
        try:
            # msg = commandType.value
            # if data is not None:
            #     if isinstance(data, list):
            #         for item in data:
            #             msg += SPLITTER + str(item)
            #     else:
            #         msg += SPLITTER + str(data)
            # msg += "\n"  # At \n to end the command
            cls.client.send(str.encode(msg))
            print('Send msg:', msg)
        except socket.error as e:
            print("Error while sending msg:" + str(e))
