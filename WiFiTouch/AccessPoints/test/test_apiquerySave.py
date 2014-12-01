__author__ = 'bopablog'


from AccessPoints.models import *
from django.test import TestCase

class ApiQueryTest(TestCase):
    #This is the fixture:
    #-   fields: {Request id: dd1df6629cee19104b3ed3b69bd1cc0d, Status: 'ERROR',
    #             Response body: 'No route to host', Action id: 'dupaosiem'}
    #model: AccessPoints.ApiqueryTest1
    #pk: 42
    fixtures = ['ApiqueryTest1']

    def testRouterObjectSave(self):
        aquery = ApiQuery.objects.get(pk = 42)
        self.assertEquals(aquery.action_id, 'dupaosiem')
        aquery.action_id = 'dupadziewiec'
        aquery.save()
        aquery_nowe = ApiQuery.objects.get(pk = 42)
        self.assertEquals(aquery_nowe.action_id, 'dupadziewiec')