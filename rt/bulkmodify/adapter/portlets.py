# -*- coding: utf-8 -*-

from zope.interface import implements

from ..interfaces import IBulkModifyContentChanger

class StaticPortletAssignmentAdapter(object):
    implements(IBulkModifyContentChanger)

    def __init__(self, context):
        self.context = context

    def _get_text(self):
        return self.context.text.encode('utf-8')

    def _set_text(self, text):
        self.context.text = text.decode('utf-8')

    text = property(_get_text, _set_text)
