__author__ = 'mysteq'
import socket


class MySocketIO:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._receiveBufferSize = 1024
        self._responseData = ""
        return

    def setReceiveBufferSize(self, sizeInBytes):
        if sizeInBytes > 0:
            self._receiveBufferSize = sizeInBytes
        else:
            raise BufferError('WHY U TRYING TO SET BUFFER TO ZERO?!')

    def sendDataToSpecifiedHost(self, data):
        try:
            self._sock.connect((self._host, self._port))
            self._sock.sendall(data)
            self._responseData = self._sock.recv(self._receiveBufferSize)
        finally:
            self._sock.close()

    def getResponseDataAndFlush(self):
        response = self._responseData
        self._responseData = ""
        return response



