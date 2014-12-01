__author__ = 'mysteq'

import rosapi
import socket
import apihelper
import logging
import json
import pprint
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



if __name__ == "__main__":

    command = "/ip/address/print"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.10.200", apihelper.API_PORT))
    api = rosapi.ApiRos(sock)
    api.login("admin", "")
    result = api.talk([command, "?.id=20" ])

    logger.debug(result)
    sock.close()
    print "-"*20
    print pprint.pprint(apihelper.parseApiFromRouter(result))