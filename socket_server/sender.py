#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import hashlib
import time
from xml.dom import minidom
import pickle

import simplejson

import mysocketio
from fabrichelper import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_XML_CONFIG = 'config.xml'

"""
Podobny do nizej zaprezentowanego modelu musi prezentowac Django.
Czyli wyslanie eventa w JSON
Serwer zajmie sie zdekodowaniem tego polecenia i wyslaniem do FabricWorkera (jakis fork?)
"""


def makeJSONfromCommandWithID(_command,_hosts_dict):
    _hasherToMD5 = hashlib.md5()
    _dataToSend = {'hosts': [], 'args': {}}
    _dataToSend['args']['command'] = _command
    _dataToSend['hosts'] = _hosts_dict
    _hasherToMD5.update(_dataToSend['args']['command']+str(time.time()))
    _dataToSend['id'] = _hasherToMD5.hexdigest()
    logger.debug("Constructed command dict: %s", _dataToSend)
    return _dataToSend

def getAddressAndPortFromXML(_filename):
    logger.info("Trying to parse XML config...")
    _xmlConfig = minidom.parse(_XML_CONFIG)
    logger.info("XML parsed")
    _serverConfig = _xmlConfig.getElementsByTagName('server')[0]
    _serverAddress = _serverConfig.getElementsByTagName('address')[0].firstChild.nodeValue
    _serverPort = int(_serverConfig.getElementsByTagName('port')[0].firstChild.nodeValue)
    return _serverAddress, _serverPort

decodersForOutput = pickle.load(open("decoders.p", "rb"))
parser = OutputParser(decodersForOutput)
serverAddress, serverPort = getAddressAndPortFromXML(_XML_CONFIG)
logger.info("server config %s : %s", serverAddress, serverPort)
#inputCommand = raw_input("Podaj komendę\n")
inputCommand = "/interface print"
#hostsRecvCommandsString = raw_input("Podaj adres hosta\n")
hostsRecvCommandsString = "192.168.10.200"
hostsRecvCommandsString = hostsRecvCommandsString.split()
socketIO = mysocketio.MySocketIO(serverAddress, serverPort)
pp = pprint.PrettyPrinter(indent=4, width=10, depth=2)
dataToSend = makeJSONfromCommandWithID(inputCommand, hostsRecvCommandsString)
dataToSendInJSON = simplejson.dumps(dataToSend, indent=4, separators=(',', ':'))
socketIO.sendDataToSpecifiedHost(dataToSendInJSON)
#tutaj wyjscie jest w JSONie wiec musimy to sparsowac
response = simplejson.loads(socketIO.getResponseDataAndFlush())
logger.info("Got response from server")

logger.debug("response from server: %s",response)
for singleHost in response:
    logger.debug("singleHost: %s",singleHost)
    outputFromDevice = response[singleHost]
    result = parser.parseOutput(inputCommand, outputFromDevice)
    logger.info("Host %s, result: %s", singleHost, result)
