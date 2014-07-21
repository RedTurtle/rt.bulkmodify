# coding=utf-8
from rt.bulkmodify.portlets import PortletFixer
from rt.bulkmodify.testing import BULK_MODIFY_INTEGRATION_TESTING
from rt.bulkmodify.tests.base import BaseTestCase


class TestPortlets(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING

    def test_search(self):
        fixer = PortletFixer(self.layer['portal'])
        assignments = list(fixer.find_all_static_assignments())
        self.assertEquals(1, len(assignments))
        self.assertEquals('I am a portlet', assignments[0].text)
