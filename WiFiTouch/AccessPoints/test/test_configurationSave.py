__author__ = 'bopablog'


from AccessPoints.models import *
from django.test import TestCase

class ConfigTest(TestCase):
    #This is the fixture:
    #-   fields: {config_body: 'test'}
    #model: AccessPoints.ConfigurationTest1
    #pk: 1
    fixtures = ['ConfigurationTest1']

    def testConfigurationSave(self):
        config = Configuration.objects.get(pk = 1)
        self.assertEquals(config.config_body, 'test')
        config.config_body = 'test1234'
        config.save()
        config_nowe = Configuration.objects.get(pk = 1)
        self.assertEquals(config_nowe.config_body, 'test1234')
