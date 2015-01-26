# -*- coding: utf-8 -*-

from ..interfaces import IBulkModifyContentChanger
from zope.interface import implements


class StaticPortletAssignmentAdapter(object):
    implements(IBulkModifyContentChanger)

    def __init__(self, context):
        self.context = context

    def _get_text(self):
        raise NotImplementedError('Portlets do not handle non-unicode')

    def _set_text(self, text):
        raise NotImplementedError('Portlets do not handle non-unicode')

    def _get_utext(self):
        return self.context.text

    def _set_utext(self, text):
        self.context.text = text

    text = property(_get_text, _set_text)
    utext = property(_get_utext, _set_utext)
