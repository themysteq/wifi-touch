__author__ = 'mysteq'
import apihelper
import logging
import socket
import json
from models import ApiQuery
from django.http import HttpResponse
def webhook(request, query_id):

    query_to_backend_for_more = apihelper.APIQuery(query_type=apihelper.API_COMMAND_GET_QUERY, query_id=query_id)
    backend_api_response = None
    sock = None
    logger = logging.getLogger(__name__)
    webhook_response = {"ERROR": ""}
    raw_response = ""
    try:
        #logger.debug("Creating socket")
        sock = socket.socket()
        sock.connect(("localhost", apihelper.API_SERVER_PORT))
        #logger.debug("Socket connected")
        #logger.debug("Trying to serialize...")
        data_to_send = apihelper.serialize(query_to_backend_for_more)
        #logger.debug("Sending data... %s", data_to_send)
        sock.sendall(data_to_send)
        #logger.debug("Data sent!")
        raw_response = sock.recv(4096).strip()
        #logger.debug("Response received")
        #logger.debug("Raw response: %s", raw_response )
        backend_api_response = apihelper.deserialize(raw_response)

        if backend_api_response.status =="OK":
            webhook_response = {"OK": query_id}
        else:
            logger.debug("[webhook] ERROR status in response")
            webhook_response = {"ERROR": str(backend_api_response.__dict__)}

        """ Here is the moment where save request to database """
        element = ApiQuery.objects.all().filter(action_id=backend_api_response.query_action)

        element, created = ApiQuery.objects.get_or_create(action_id=backend_api_response.query_action)
        if created:
            webhook_response["created"] = True
        else:
            webhook_response["created"] = False

        element.action_id = backend_api_response.query_action
        element.request_id = backend_api_response.query_id
        element.status = backend_api_response.status
        element.response_body = json.dumps(backend_api_response.query_body)

        element.save()



    except IOError, e:
        logger.error("Exception: "+ e.strerror)
        raise

    finally:
        sock.close()
        json_response = json.dumps(webhook_response)
        #logger.debug("[webhook] JSON response: %s", json_response)
        #logger.debug(apihelper.serialize(backend_api_response))
        return HttpResponse(json_response)
