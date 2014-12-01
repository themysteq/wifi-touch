#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import logging

import simplejson

from fabrichelper import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
__author__ = 'mysteq'
HOST = "0.0.0.0"
PORT = 10000
server = None

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        outputDict = {}
        req = self.request
        self.data = req.recv(1024).strip()
        recvJSON = simplejson.loads(self.data)
        logger.debug("Received JSON data: %s", recvJSON)
        #dekoduj polecenie
        #powolaj workera

        logger.debug("Calling FabricWorker")
        command = recvJSON['args']['command']
        hosts = recvJSON['hosts']
        for singleHost in hosts:
            logger.debug("sending command '%s' to host '%s'", command, singleHost)
            singleoutput = FabricWorker(singleHost, command)
            outputDict[singleHost] = singleoutput

        #odeslij klientowi ze wszystko spoko
        logger.debug( "FabricWorker exited" )
        dataToSend = simplejson.dumps(outputDict, indent=4, separators=(',', ':'))
        logger.debug("response json: %s", dataToSend)
        self.request.sendall(dataToSend)
        self.request.close()
        return


if __name__ == "__main__":


    logger.info("Starting server on port %s...", PORT )
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    logger.info("Server binded to %s:%s", HOST, PORT)
    server.server_activate()
    server.serve_forever()

