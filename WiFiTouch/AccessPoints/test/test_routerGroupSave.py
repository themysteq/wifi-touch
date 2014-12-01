__author__ = 'bopablog'


from AccessPoints.models import *
from django.test import TestCase

class RouterGroupTest(TestCase):
    #This is the fixture:
    #-   fields: {Name: 'KTI_lab'}
    #model: AccessPoints.RouterGroupTest1
    #pk: 5
    fixtures = ['RouterGroupTest1']

    def testRouterGroupObjectSave(self):
        rgroup = RouterGroup.objects.get(pk = 5)
        self.assertEquals(rgroup.name, 'KTI_lab')
        rgroup.name = 'ETI'
        rgroup.save()
        rgroup_nowe = RouterGroup.objects.get(pk = 5)
        self.assertEquals(rgroup_nowe.name, 'ETI')