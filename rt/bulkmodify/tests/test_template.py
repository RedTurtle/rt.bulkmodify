# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter

from rt.bulkmodify.testing import BULK_MODIFY_INTEGRATION_TESTING
from .base import BaseTestCase
from .base import re_pattern
from .base import re_subn_pattern


class TestViewBatchSearch(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"bulk-modify")

    def test_additional_utilities(self):
        """Testing that is possible to see new handlers in the UI"""
        view = self.view
        self.assertTrue('<label class="possibleReplaceType" for="repltype-2">Fake utility</label>' in view())
