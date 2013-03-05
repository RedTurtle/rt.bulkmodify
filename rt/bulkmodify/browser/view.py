# -*- coding: utf-8 -*-

import re
import json

from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface

from zope.schema.interfaces import IVocabularyFactory

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from rt.bulkmodify import messageFactory as _
from rt.bulkmodify import utility


class IBulkModify(Interface):
    """View for bulk modify"""
    
    def batchSearch():
        """Search for a subset of results"""


class BulkModifyView(BrowserView):
    implements(IBulkModify)
    
    def type_vocabulary(self):
        factory = getUtility(IVocabularyFactory, 'plone.app.vocabularies.ReallyUserFriendlyTypes')
        return factory(self.context)

    def batchSearch(self):
        context = self.context
        request = self.request
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        search_query = request.get('searchQuery')
        b_start = request.get('b_start', 0)
        b_size = request.get('b_size', 20)
        flags = request.get('flags', 0)
        portal_type = request.get('types', [])
        catalog = getToolByName(context, 'portal_catalog')
        
        results = []
        brains = catalog(portal_type=portal_type)[b_start:b_start+b_size]
        if not brains:
            # stop client side queries
            return json.dumps(None)
        for brain in brains:
            obj = brain.getObject()
            text = obj.getField('text').get(obj)
            result = utility.text_search(text, search_query, flags=flags)
            for r in result:
                r['url'] = brain.getURL()
                r['id'] = brain.UID
                r['title'] = brain.Title
            results.extend(result)
        return json.dumps(results)

        