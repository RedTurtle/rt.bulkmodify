# -*- coding: utf-8 -*-

import re
import unittest

from rt.bulkmodify.handler.to_uid import InternalLinkToUIDUtility

from rt.bulkmodify.testing import BULK_MODIFY_INTEGRATION_TESTING
from .base import BaseTestCase

re_pattern = r'<a href="(?P<url>[^"]*)">(?P<text>[^<]*)</a>'
is_internal_link = re.compile(re_pattern)
utility = InternalLinkToUIDUtility()

class TestUtility(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING

    def setUp(self):
        BaseTestCase.setUp(self)
    
    def test_basic_replace(self):
        portal = self.layer['portal']
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://external.org/foo">Bar Baz</a> Ipsum'),
                         'Lorem <a href="http://external.org/foo">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/foo">Bar Baz</a> Ipsum'),
                         'Lorem <a href="http://nohost/plone/foo">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/page1">Bar Baz</a> Ipsum'),
                         'Lorem <a href="http://nohost/plone/resolveuid/' + portal.page1.UID() + '">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/page1/base_view">Bar Baz</a> Ipsum'),
                         'Lorem <a href="http://nohost/plone/resolveuid/' + portal.page1.UID() + '/base_view">Bar Baz</a> Ipsum')