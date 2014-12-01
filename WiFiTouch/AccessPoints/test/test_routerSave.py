__author__ = 'bopablog'

from AccessPoints.models import *
from django.test import TestCase

class RouterTest(TestCase):
    #This is the fixture:
    #-   fields: {management_ip:192.168.10.100, name:'Test', login:'test', password:'test'}
    #model: AccessPoints.RouterTest1
    #pk: 5
    fixtures = ['RouterTest1']

    def testRouterObjectSave(self):
        router = Router.objects.get(pk = 5)
        self.assertEquals(router.name, 'Test')
        router.name = 'Nowa nazwa'
        router.save()
        router_nowy = Router.objects.get(pk = 5)
        self.assertEquals(router_nowy.name, 'Nowa nazwa')