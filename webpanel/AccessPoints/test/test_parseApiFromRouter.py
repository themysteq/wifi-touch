__author__ = 'bopablog'

from django.test import TestCase
from AccessPoints.apihelper import *

tested_query_re = [ {'!re': 'alamakota', 'body': {'network': '192.168.100.200'} } ]
tested_query_done = [ {'!done': '', 'body': ''} ]
tested_query_trap = [ {'!trap': 'alamakota', 'body1': 'ok'} ]

class parseApiFromRouterTest(TestCase):

    def testParseFromRouter(self):
        print 'To jeszcze nie jest test'

        print '! done czyli ok bez body'
        wynik = parseApiFromRouter(tested_query_done)
        print wynik

        print '! re czyli ok z body'
        wynik = parseApiFromRouter(tested_query_re)
        print wynik

        print '! trap czyli blad'
        wynik = parseApiFromRouter(tested_query_trap)
        print wynik