# -*- coding: utf-8 -*-

from zope.interface import implements

from ..interfaces import IBulkModifyContentChanger


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

    text = property(_get_text, _set_text)
