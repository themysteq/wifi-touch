__author__ = 'bopablog'

import socket
from AccessPoints.apihelper import *

apireq = APIQuery(API_COMMAND_GET_QUERY, 1234567890, "test", ["body", "test"], {"network" : "192.168.10.100", "host" : "bopablo"}, "GET")

print "Wywolanie apiQueryDevice"
wynik = apiQueryDevice(apireq)
print wynik