__author__ = 'bopablog'


from AccessPoints.views import *
from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        #print found
        self.assertEqual(found.func, main)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = main(request)
        #print response.status_code
        self.assertEquals(response.status_code, 200)

class ApiQueriesPageTest(TestCase):

    def test_url_resolves_to_apiqueries_view(self):
        found = resolve('/apiqueries/')
        #print found
        self.assertEqual(found.func, apiqueries)

    def test_apiqueries_returns_correct_html(self):
        request = HttpRequest()
        response = apiqueries(request)
        #print response.status_code
        self.assertEquals(response.status_code, 200)


class RoutersPageTest(TestCase):

    def test_url_resolves_to_routers_view(self):
       found = resolve('/routers/')
       #print found
       self.assertEqual(found.func, routers)

    def test_routers_returns_correct_html(self):
        request = HttpRequest()
        response = routers(request)
        #print response.status_code
        self.assertEquals(response.status_code, 200)


class GroupsPageTest(TestCase):
    def test_url_resolves_groups_view(self):
        found = resolve('/groups/')
        #print found
        self.assertEqual(found.func, groups)

    def test_groups_returns_correct_html(self):
        request = HttpRequest()
        response = groups(request)
        #print response.status_code
        self.assertEquals(response.status_code, 200)


class LoginPageTest(TestCase):
    def test_url_resolves_to_login_view(self):
        found = resolve('/login/')
        #print found
        self.assertEqual(found.func, login)

    def test_login_returns_correct_html(self):
        request = HttpRequest()
        response = login(request)
        #print response.status_code
        self.assertEquals(response.status_code, 200)