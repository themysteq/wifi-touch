# -*- coding: utf-8 -*-
__author__ = 'mysteq'
import re
import logging

from fabric.api import *
from fabric.network import disconnect_all

logger = logging.getLogger(__name__)

class OutputParser:

    def __init__(self):
        self._decoders = {}

    def __init__(self, decoders):
        self._decoders = decoders

    def parseOutput(self, issuedCommand, outputFromDevice):

        result = []
        """
        Nie możemy zakładać, że zawsze zwijamy dwie pierwsze linijki, ale teraz tak mozemy
        """
        outPutFromDeviceAsDict = outputFromDevice.split("\r\n")[2:]
        logger.debug("output in dict: %s", outPutFromDeviceAsDict)
        slicingRegex = self._decoders[issuedCommand]
        logger.debug("Command '%s' and regex: '%s'", issuedCommand, slicingRegex)
        pattern = re.compile(slicingRegex)
        for singleLine in outPutFromDeviceAsDict:
            logger.debug("singleline: '%s'", singleLine)
            regexSearched = pattern.search(singleLine)
            if not regexSearched:
                break
            logger.debug("regex found: %s", regexSearched)
            result.append(regexSearched.groupdict())
        logger.debug(result)
        return result





def FabricWorker(_host, command):
    # arg to czysty string do wykonania
    with hide('running','status','warnings','stdout', 'stderr'):
        env.host_string = _host
        env.user = "fabric"
        env.password = "fabric1"
        env.no_keys = True
        env.no_agent = True
        #print env
        output = run(command, pty=False, shell=False,timeout=3)
        disconnect_all()
    #na razie hardcode
    return output

