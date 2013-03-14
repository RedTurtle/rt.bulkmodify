# -*- coding: utf-8 -*-

import re

from rt.bulkmodify.handler.to_uid import InternalLinkToUIDUtility

from rt.bulkmodify.testing import BULK_MODIFY_INTEGRATION_TESTING
from .base import BaseTestCase

re_pattern = r'<a href="(?P<url>[^"]*)">(?P<text>[^<]*)</a>'
is_internal_link = re.compile(re_pattern)
utility = InternalLinkToUIDUtility()


class TestUtility(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING

    def test_not_existings(self):
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://external.org/foo">Bar Baz</a> Ipsum'),
                         'Lorem <a href="http://external.org/foo">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/foo">Bar Baz</a> Ipsum'),
                         'Lorem <a href="http://nohost/plone/foo">Bar Baz</a> Ipsum')

    def test_replace(self):
        portal = self.layer['portal']
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/page1">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.page1.UID() + '">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/page1/base_view">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.page1.UID() + '/base_view">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/page1/base_view?aaa=b">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.page1.UID() + '/base_view?aaa=b">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/page1/base_view/qux">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.page1.UID() + '/base_view/qux">Bar Baz</a> Ipsum')

    def test_file_download(self):
        portal = self.layer['portal']
        with open(__file__, 'r') as f:
            portal.invokeFactory('File', 'file1', title="File 1",
                                 file=f)
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="http://nohost/plone/file1/at_download/file">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.file1.UID() + '/at_download/file">Bar Baz</a> Ipsum')

    def test_relative_urls(self):
        portal = self.layer['portal']
        utility.__class__.context = portal.page1
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="page2">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.page2.UID() + '">Bar Baz</a> Ipsum')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              r'Lorem <a href="folder1/event1">Bar Baz</a> Ipsum'),
                         'Lorem <a href="resolveuid/' + portal.folder1.event1.UID() + '">Bar Baz</a> Ipsum')
        utility.__class__.context = portal.folder1.event1
        portal.folder1.event1.setText('<p> <a href="../page2">Lorem Ipsum</a> </p>')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              portal.folder1.event1.getText()),
                         '<p> <a href="resolveuid/' + portal.page2.UID() + '">Lorem Ipsum</a> </p>')
        portal.folder1.event1.setText('<p> <a href="../page2/base_view">Lorem Ipsum</a> </p>')
        self.assertEqual(is_internal_link.sub(utility.repl,
                                              portal.folder1.event1.getText()),
                         '<p> <a href="resolveuid/' + portal.page2.UID() + '/base_view">Lorem Ipsum</a> </p>')
