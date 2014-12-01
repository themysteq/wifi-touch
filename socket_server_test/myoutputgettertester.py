__author__ = 'mysteq'
import logging

from fabrichelper import FabricWorker

logger = logging.getLogger(__name__)

command = "/ip address print"
host = "192.168.10.200"
output = FabricWorker(host, command)
linesDict = output.split('\r\n')
for line in linesDict[:]:
    #print "LINE: ",line
    #pajton = re.sub(' ','s',line)
    #print pajton
    #print line.split('  ')
    print line