# -*- coding: utf-8 -*-

from ..interfaces import IBulkModifyContentChanger
from zope.interface import implements


class TextContentAdapters(object):
    """This is ok for news, pages and events"""
    implements(IBulkModifyContentChanger)

    def __init__(self, context):
        self.context = context

    def _get_text(self):
        return str(self.context.getField('text').get(self.context, raw=True))
    
    def _set_text(self, text):
        self.context.getField('text').set(self.context, text)
        self.context.reindexObject(idxs=['SearchableText'])

    def _get_utext(self):
        return self.text.decode('utf-8')

    def _set_utext(self, text):
        self.text = text.encode('utf-8')

    text = property(_get_text, _set_text)
    utext = property(_get_utext, _set_utext)
