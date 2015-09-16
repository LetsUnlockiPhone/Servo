# -*- coding: utf-8 -*-

import unittest
from django.test import TestCase
from django.http import HttpRequest
from django.core.urlresolvers import resolve
from django.test.simple import DjangoTestSuiteRunner

from servo.views import checkin


class NoDbTestRunner(DjangoTestSuiteRunner):
    """ A test runner to test without database creation """

    def setup_databases(self, **kwargs):
        """ Override the database creation defined in parent class """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """ Override the database teardown defined in parent class """
        pass


class ApiTest(TestCase):
    pass

    
class CheckinTest(TestCase):
    def test_checkin_url_resolves(self):
        found = resolve('/checkin/')
        self.assertEqual(found.func, checkin.home)

    def test_homepage_error_without_cookies(self):
        request = HttpRequest()
        response = checkin.home(request)
        self.assertTrue(response.content.startswith("<!DOCTYPE html>"), response.content)
        self.assertIn('<title>An error occurred', response.content)
        self.assertTrue(response.content.endswith('</html>'))


if __name__ == '__main__':
    unittest.main()
