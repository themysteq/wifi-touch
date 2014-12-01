#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'mysteq'
import apihelper
import logging
import socket
import random
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    action_id = "default_action"
    command = "/ip/address/print"
    if len(sys.argv) < 3 :
        #print "Za mało argumentów"
        print "api_sender.py [action_id] [command]"
    else:
        action_id = sys.argv[1]
    	command = sys.argv[2]
	#args = {"host": "192.168.10.200", "request_id": "", "credentials":("admin",""),"query_type":"ORDER"}i
    #args["command"] = {"/interface/wireless/print":{}}
    args = {"query_type": apihelper.API_COMMAND_PUT_QUERY,
            "status": "TEST_API_SENDER",
            "query_body":
                { "command": command,
                 "args": {}},
                "opt1": {"credentials": ("admin", ""),
                "host": "192.168.10.200"}}

    apireq = apihelper.APIQuery(**args)
    apireq.query_action = action_id
    apireq.activate()

    logger.debug("__dict__ of apireq : %s", apireq)
    logger.debug(apireq)

    logger.debug("Creating socket")

    s = socket.socket()
    #apireq.host = "192.168.10.200"
   # apireq.request_id = "aa9f3a02684e4a7b32ae6333a6f713eb"
    apireq_to_send = apihelper.serialize(apireq)
    s.connect(("localhost", apihelper.API_SERVER_PORT))
    logger.info("Socket connected!")

    s.send(apireq_to_send)
    logger.info("sent!")
    response = s.recv(4096)
    s.close()
    print response
    logger.info("done!")
