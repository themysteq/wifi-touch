#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mysteq'
import pickle
import hashlib
import time
import random
import logging
import socket
import simplejson
import os
import rosapi
import Queue
import threading as th
import httplib

logger = logging.getLogger(__name__)
API_PORT = 8728
API_SERVER_PORT=10000
WEBHOOK_PORT=8108
API_COMMAND_PUT_QUERY = "PUT_QUERY"
API_COMMAND_GET_QUERY = "GET_QUERY"
API_COMMAND_GET_QUERY_ACK = "GET_QUERY_ACK"
API_COMMAND_PUT_QUERY_ACK = "PUT_QUERY_ACK"

def cleanBody(in_body):
    out_body = {}
    for key, val in in_body.items():
               out_body[key[1:]] = val

    return out_body

def parseApiFromRouter(router_response):

    result = {}
    result["length"] = str(len(router_response))
    result["content"] = []
    for (type, body) in router_response:
        logger.debug("[parseApiFromRouter] type,body : %s,%s",type,body)
        if type == "!re":
            #jest dobrze
            result["content"].append(cleanBody(body))
            result["status"] = "OK"
        elif type == "!trap":
            #cos nie tak poszlo
            result["status"] = "ERROR"
            result["content"] = cleanBody(body)
            logger.debug("[parseApiFromRouter]: result: %s",result)
        elif type =="!done":
            pass
        else:
            #kod odpowiedzi nieznany
            raise Exception("parseAPI unspecified response type!")

    if result["length"] == "1":
        result["status"] = "EMPTY"
    return result


def serialize(obj_to_serialize):
    assert isinstance(obj_to_serialize, APIQuery)
    logger.debug("APIQuery: %s", obj_to_serialize)
    json_data = simplejson.dumps(obj_to_serialize.__dict__)
    return json_data


def deserialize(serialized_obj):
    obj = APIQuery()
    obj.__dict__ = simplejson.loads(serialized_obj)
    assert isinstance(obj, APIQuery)
    return obj


def apiQueryDevice(apireq):
    assert isinstance(apireq, APIQuery)
    logger.debug("Calling apiQueryDevice")
    sock = socket.socket()
    apiresponse = APIQuery(query_type=API_COMMAND_GET_QUERY_ACK)
    try:
        sock.connect((apireq.opt1["host"], API_PORT))
       # logger.debug("Querying device, query: %s", apireq)
        api = rosapi.ApiRos(sock)
        (user, password) = apireq.opt1["credentials"]
        logger.debug("[apiQueryDevice] : login: %s password: %s", user, password)
        raw_login_response = api.login(user, password)
        logger.debug("[apiQueryDevice] login response: %s", raw_login_response)
        parsed_login = parseApiFromRouter(raw_login_response)
        logger.debug("[apiQueryDevice] parsed login: %s", parsed_login)
        if parsed_login["status"] == "ERROR":
            apiresponse.query_action = apireq.query_action
            apiresponse.query_id = apireq.query_id
            apiresponse.query_body = parsed_login["content"]["message"]
            apiresponse.status = "ERROR"
            return apiresponse

        #logger.debug("[apiQueryDevice] parsed login: %s",parsed_login)
        command = apireq.query_body["command"]
        arguments = apireq.query_body["args"]
        #logger.debug("[apiQueryDevice] command: %s ; arguments: %s", command, arguments)
        #logger.debug("[apiQueryDevice] trying to talk")
        api_talk_args = list()
        api_talk_args.append(command)
        api_talk_args.extend(arguments)
        logger.debug("[apiQueryDevice] api_talk_args: %s", api_talk_args)
        raw_result = api.talk(api_talk_args)
        #logger.debug("[apiQueryDevice] She told me...")
        parsed_result = parseApiFromRouter(raw_result)
        logger.debug("[apiQueryDevice] parsed result: %s", parsed_result)
        sock.close()
        #logger.debug("[apiQueryDevice] API query result: %s", parsed_result)
        apiresponse = APIQuery(query_id=apireq.query_id,
                               query_type=API_COMMAND_GET_QUERY_ACK,
                               status="OK",
                               query_body=[parsed_result],
                               query_action=apireq.query_action)
    except socket.error, e:
        logger.debug("Socket error %s:", e.strerror)
        apiresponse.query_id = apireq.query_id
        apiresponse.query_action = apireq.query_action
        apiresponse.status = "ERROR"
        apiresponse.query_body = e.strerror
    except RuntimeError as e:
        #logger.debug("[apiQueryDevice] WEIRD EXCEPTION?! %s", e.strerror)
        apiresponse.query_id = apireq.query_id
        apiresponse.query_action = apireq.query_action
        apiresponse.status = "ERROR"
        apiresponse.query_body = e.message
    finally:
        return apiresponse


class APIQuery:
    def __init__(self,
                 query_type=API_COMMAND_GET_QUERY,
                 query_id="",
                 status="",
                 query_body={},
                 opt1={},
                 query_action=""):

        self.query_type = query_type
        self.query_id = query_id
        self.status = status
        self.query_body = query_body
        self.query_action = query_action
        self.opt1 = opt1

    def activate(self):
        m = hashlib.md5()
        m.update(str(random.random())[2:]+str(time.time()))
        self.query_id = m.hexdigest()
        return self.query_id

    def __unicode__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class IOContainer:

    def __init__(self, jobs_queue=Queue.Queue(), results_queue=Queue.Queue(), lock=th.Lock(), finished_queue={}):
        logger.debug("IOContainer constructor called")
        self.jobs_queue = jobs_queue
        self.results_queue = results_queue
        self.lock = lock
        self.f_dict = finished_queue

    def __str__(self):
        return str(self.__dict__)

    def putFinishedAsIterable(self, key, obj):
        assert isinstance(obj, APIQuery)
        if key == "":
            raise KeyError("Empty Key!")
        self.lock.acquire()
        logger.debug("at key %s putting %s", key, obj)
        self.f_dict[key] = obj
        logger.debug("Finished looks like: %s", self.f_dict)
        self.lock.release()

    def getFinishedFromIterables(self, key):
        logger.debug("Getting result by key %s", key)
        self.lock.acquire()
        try:
            response = self.f_dict[key]
            del self.f_dict[key]
        except KeyError:
            logger.debug("[getFinishedFromIterables] List length: %s,elements: %s", len(self.f_dict), str(self.f_dict))
            response = APIQuery(
                                query_type=API_COMMAND_GET_QUERY_ACK,
                                query_id=key,
                                status="ERROR",
                                query_body=["NOT_FINISHED"])

        #assert isinstance(response, APIResponse)
        self.lock.release()
        logger.debug("Getting from iterables: %s", response)
        return response


def APIWorker(io_container):
    logger.debug("[%s] Worker starting...", os.getpid())
    apiresponse = None
    assert isinstance(io_container, IOContainer)
    try:
        for item in iter(io_container.jobs_queue.get, 'STOP'):
            assert isinstance(item, APIQuery)
            logger.debug("[%s] Doing job", os.getpid())
            try:
                logger.debug("[APIWorker] Got job: %s", item)
                apiresponse = apiQueryDevice(item)
            except socket.error, e:
                logger.debug("Socket error %s:", e.strerror)
                apiresponse = APIQuery(query_type=API_COMMAND_GET_QUERY_ACK,
                                       query_id=item.query_id,
                                       status="ERROR",
                                       query_body=[e.strerror, ])

                logger.debug(apiresponse)
            except:
                logger.debug("[APIWorker] GOT WEIRD EXCEPTION?!")
            finally:
                io_container.putFinishedAsIterable(apiresponse.query_id, apiresponse)
                #io_container.results_queue.put(apiresponse)
                """ Wypada powiadomić webhookiem, że skończyliśmy i może sobie wrzucić do bazy"""
                logger.debug("Calling webhook")
                conn = httplib.HTTPConnection("localhost", WEBHOOK_PORT)
                conn.request("GET", "/webhook/"+apiresponse.query_id+"/")
                logger.debug(conn.getresponse().read())
                conn.close()
                logger.debug("Webhook called!")


    except StopIteration:
        logger.debug("[%s] Stopping worker", os.getpid())
        exit()





