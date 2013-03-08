# -*- coding: utf-8 -*-

import re
import json

from zExceptions import NotFound

from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface

from zope.schema.interfaces import IVocabularyFactory

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from rt.bulkmodify import messageFactory as _
from rt.bulkmodify import utility

path_id_pattern = re.compile(r'^(.*)-(\d+)$')

class IBulkModify(Interface):
    """View for bulk modify"""
    
    def batchSearch():
        """Search for a subset of results and preview matches"""

    def batchReplace():
        """Search for a subset of result, and preview mach changes"""

    def replaceText():
        """Apply a regex replacement to documents"""


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
        portal_type = request.get('content_type', [])
        catalog = getToolByName(context, 'portal_catalog')
        
        results = []

        if not portal_type or not search_query:
            return json.dumps(results)
        
        brains = catalog(portal_type=portal_type)[b_start:b_start+b_size]
        if not brains:
            # stop client side queries
            return json.dumps(None)
        for brain in brains:
            obj = brain.getObject()
            text = obj.getField('text').get(obj)
            inner_results = utility.text_search(text, search_query, flags=flags, preview=True)
            for result in inner_results:
                result['url'] = brain.getURL()
                result['id'] = brain.getPath()
                result['uid'] = brain.UID
                result['title'] = brain.Title
            results.extend(inner_results)
        return json.dumps(results)

    def get_content_diff_info(self, obj, search_query, replace_query, flags=0):
        text = obj.getField('text').get(obj)
        inner_results = utility.text_replace(text, search_query, replace_query, flags=flags)
        for result in inner_results:
            result['url'] = obj.absolute_url()
            result['id'] = '/'.join(obj.getPhysicalPath()[2:])
            result['uid'] = obj.UID()
            result['title'] = obj.Title()
        return inner_results

    def batchReplace(self):
        context = self.context
        request = self.request
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        search_query = request.get('searchQuery')
        replace_query = request.get('replaceQuery')
        b_start = request.get('b_start', 0)
        b_size = request.get('b_size', 20)
        flags = request.get('flags', 0)
        portal_type = request.get('content_type', [])
        catalog = getToolByName(context, 'portal_catalog')
        
        results = []
        
        if not portal_type or not search_query or not replace_query:
            return json.dumps(results)
        
        brains = catalog(portal_type=portal_type)[b_start:b_start+b_size]
        if not brains:
            # stop client side queries
            return json.dumps(None)
        for brain in brains:
            obj = brain.getObject()
            inner_results = self.get_content_diff_info(obj, search_query, replace_query, flags=flags)
            results.extend(inner_results)
        return json.dumps(results)

    def changeDocumentText(self, obj, diff):
        text = obj.getField('text').get(obj)
        obj.getField('text').set(obj, text[:diff['start']] + diff['new'] + text[diff['end']:])
        obj.reindexObject(idxs=['SearchableText'])

    def replaceText(self):
        context = self.context
        request = self.request
        portal = getToolByName(context, 'portal_url').getPortalObject()
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        # ids MUST be of the same objects
        ids = request.get('id')
        search_query = request.get('searchQuery')
        replace_query = request.get('replaceQuery')
        flags = request.get('flags', 0)
        
        messages = []
        
        if search_query and replace_query:
            for counter, id in enumerate(ids):
                match = path_id_pattern.match(id)
                path, id = match.groups()
                obj = portal.restrictedTraverse(path, default=None)
                id = int(id)
                if obj:
                    diff_info = self.get_content_diff_info(obj, search_query, replace_query, flags=flags)
                    diff = diff_info[id-counter]
                    self.changeDocumentText(obj, diff)
                    messages.append({'status': 'OK'})
                else:
                    messages.append({'status': 'error', 'message': 'Document "%s" not found'})
        return json.dumps(messages)

