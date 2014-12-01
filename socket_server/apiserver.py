__author__ = 'mysteq'
import SocketServer
import os
import threading
import Queue
import pickle
import apihelper
import logging
import threading as th
import random
import time
import pprint

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
HOST = "localhost"
PORT = 10000
WORKERS = 3
GET_TIMEOUT = 5


def InitializeAndRunServer(container):
    assert isinstance(container, apihelper.IOContainer)
    server = APIServer((HOST, PORT), APIRequestHandler, container)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    logger.debug("Server activated! GOING TO BE SOOO EPIICC")
    server.serve_forever()


class APIServer(SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, _io_container):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate=False)
        self.io_container = _io_container


class APIRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        #http://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
        #czyli ograniczamy do 4KB
        logger.info("Handle...")
        req = self.request
        self.data = req.recv(4096).strip()
        logger.debug("[APIRequestHandler] Data received: %s", self.data)
        api_query_from_client = apihelper.deserialize(self.data)
        logger.debug("[APIRequestHandler] Object deserialized: %s", api_query_from_client)
        assert isinstance(api_query_from_client, apihelper.APIQuery)
        if api_query_from_client.query_id == "":
            raise KeyError("[APIRequestHandler] Query Id Empty Key!")

        if api_query_from_client.query_type == apihelper.API_COMMAND_PUT_QUERY:
            logger.info("[APIRequestHandler] Putting job in queue")
            self.server.io_container.jobs_queue.put(api_query_from_client)
            query_result = apihelper.APIQuery(
                query_id=api_query_from_client.query_id, query_type=apihelper.API_COMMAND_PUT_QUERY_ACK, status="OK",)

        elif api_query_from_client.query_type == apihelper.API_COMMAND_GET_QUERY:
            query_result = self.server.io_container.getFinishedFromIterables(api_query_from_client.query_id)
            assert isinstance(query_result, apihelper.APIQuery)
            query_result.query_type = apihelper.API_COMMAND_GET_QUERY_ACK
        else:
            query_result = apihelper.APIQuery(query_id=api_query_from_client.query_id, status="ERROR", query_body=[ "NOT_YET_IMPLEMENTED", ])
            query_result.query_type = apihelper.API_COMMAND_GET_QUERY_ACK

        assert isinstance(query_result, apihelper.APIQuery)
        query_to_send = apihelper.serialize(query_result)
        self.request.sendall(query_to_send)
        logger.debug("Response sent!")
        self.request.close()
        logger.info("Handle done")


if __name__ =="__main__":

    io_container = apihelper.IOContainer()

    logger.info("Server binded to %s:%s", HOST, PORT)
    server_process = th.Thread(target=InitializeAndRunServer, args=(io_container,))
    #server_thread = threading.Thread(target=InitializeAndRunServer, args=(input_glob, output_glob))
    #server_thread.daemon = True
    #server_thread.start()s
    server_process.daemon = True
    server_process.start()
    WorkersList = []

    for workerCount in range(WORKERS):
        workerProcess = th.Thread(target=apihelper.APIWorker, args=(io_container,))
        workerProcess.daemon = True
        workerProcess.start()
        WorkersList.append(workerProcess)

    while 1:

        option = raw_input("count/get/getbykey/list_all/clear/quit?\n")
        if option == "get":
            logger.debug("getting element from queue")
            try:
                element_from_queue = io_container.results_queue.get(block=False)
                print element_from_queue
                logger.debug("element from queue got!")
            except Queue.Empty:
                logger.info("Results queue is empty!")
        elif option == 'print':
            print io_container

        elif option == "quit":
            logger.debug("Quitting!")
            for worker in WorkersList:
                io_container.jobs_queue.put('STOP')
            for worker in WorkersList:
                worker.join()
            break
        elif option=="list_all":
            for key, val in io_container.f_dict.items():
                print "Result by %s key : %s" % ( key,val)
        elif option =="clear":

            for key,val in io_container.f_dict.items():
                del io_container.f_dict[key]
            if len(io_container.f_dict)==0:
                print "Cleared!"
            else:
                print "Upsss?"

        elif option == "count":
            print "Jobs queue size %s" % io_container.jobs_queue.qsize()
            print "Results queue size %s" % io_container.results_queue.qsize()
            print "Shared IOContainer size %s" % len(io_container.f_dict)
        elif option == "getbykey":
            key = raw_input("Enter key.\n")
            try:
                print "Result by %s key : %s" % (key, io_container.f_dict[key])
            except KeyError:
                print "No such result"
