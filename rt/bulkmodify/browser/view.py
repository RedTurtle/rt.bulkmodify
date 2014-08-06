# -*- coding: utf-8 -*-

import re
import json
from plone.portlet.static.static import Assignment as StaticAssignment
from plone.portlets.interfaces import ILocalPortletAssignable, IPortletManager, \
    IPortletAssignmentMapping
from rt.bulkmodify.utility import text_search

from zope.component import getUtility, getMultiAdapter
from zope.component import queryAdapter
from zope.component import getUtilitiesFor
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory

from plone.memoize.view import memoize

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.CMFEditions.utilities import isObjectChanged
from Products.CMFEditions.utilities import maybeSaveVersion
from Products.CMFEditions.utilities import isObjectVersioned

from rt.bulkmodify import messageFactory as _
from rt.bulkmodify import logger
from rt.bulkmodify import utility
from rt.bulkmodify.interfaces import IBulkModifyContentChanger
from rt.bulkmodify.interfaces import IBulkModifyReplacementHandler

path_id_pattern = re.compile(r'^(.*)-(\d+)$')

class IBulkModify(Interface):
    """View for bulk modify"""
    
    def batchSearch():
        """Search for a subset of results and preview matches"""

    def batchReplace():
        """Search for a subset of result, and preview mach changes"""

    def replaceText():
        """Apply a regex replacement to documents"""

class Result(object):
    managers = ['plone.leftcolumn', 'plone.rightcolumn']

    def __init__(self, brain_or_object, portal_types, portlets):
        if hasattr(brain_or_object, 'getObject'):
            self.brain = brain_or_object
            self.obj = brain_or_object.getObject()
        else:
            self.brain = None
            self.obj = brain_or_object
        self.portal_types = portal_types
        self.portlets = portlets
        
    def _get_text_adapters(self):
        if self.obj.portal_type in self.portal_types or self.portal_types == []:
            adapter = queryAdapter(self.obj, IBulkModifyContentChanger)
            if adapter:
                yield adapter
        if self.portlets and ILocalPortletAssignable.providedBy(self.obj):
            for manager_name in self.managers:
                manager = getUtility(IPortletManager, name=manager_name,
                                     context=self.obj)
                mapping = getMultiAdapter((self.obj, manager),
                                          IPortletAssignmentMapping)
                for ignored, assignment in mapping.items():
                    adapter = queryAdapter(assignment, IBulkModifyContentChanger)
                    if adapter:
                        yield adapter

    @property
    def text(self):
        if not hasattr(self, '_text'):
            self._text = '\n'.join([x.text for x in
                                    self._get_text_adapters() if x.text])
        return self._text

    def get_possible_replacements(self, regex, repl, flags):
        retval = []
        offset_number = 0
        for adapter in self._get_text_adapters():
            matches = text_search(adapter.text.decode('utf-8'), regex,
                                  flags=flags)
            pattern = re.compile(regex, flags)
            for match in matches:
                offset = lambda x: match[x]+offset_number
                old = match['text']
                replaced = pattern.sub(repl, old)
                if old != replaced:
                    result = dict(old=old, new=replaced)
                    result['start'] = offset('start')
                    result['end'] = offset('end')
                    result['pre_text'] = match['pre_text']
                    result['post_text'] = match['post_text']
                    retval.append(result)
            offset_number += len(adapter.text) + 1
        return retval

    def replace(self, diffs):
        changed = []
        multi_adapter_offset = 0
        for adapter in self._get_text_adapters():
            next_adapter_offset = len(adapter.text) + 1
            multi_match_offset = 0
            for diff in diffs:
                offset = lambda x: diff[x]+multi_adapter_offset+multi_match_offset
                text = adapter.text.decode('utf-8')
                if offset('start') > 0 and offset('start') < len(text):
                    adapter.text = (text[:offset('start')] + diff['new'] \
                                   + text[offset('end'):]).encode('utf-8')
                    has_changed = adapter.text != text
                    if has_changed:
                        multi_match_offset += len(adapter.text) - len(text)
                    changed.append(has_changed)

            multi_adapter_offset -= next_adapter_offset
        return changed

    def __getitem__(self, key):
        if key == 'url':
            return self.obj.absolute_url()
        if key == 'id':
            return '/'.join(self.obj.getPhysicalPath()[2:])
        if key == 'uid':
            return self.obj.UID()
        if key == 'title':
            return self.obj.Title()
        if key == 'icon':
            return self.brain.getIcon if self.brain else ""
        if key == 'normalized_portal_type':
            return self.obj.portal_type.lower().replace(' ', '-')


class BulkModifyView(BrowserView):
    implements(IBulkModify)

    @property
    @memoize
    def utilities(self):
        return getUtilitiesFor(IBulkModifyReplacementHandler)
    
    def type_vocabulary(self):
        factory = getUtility(IVocabularyFactory, 'plone.app.vocabularies.ReallyUserFriendlyTypes')
        return factory(self.context)

    def repl_type_vocabulary(self):
        results = [{'title': _('default_replacement_type_label',
                               default=u'Default replacement'),
                    'description': _('default_replacement_type_help',
                                     default=u'Default replacement method. Use the replacement string '
                                             u'from the field below'),
                    'value': ''}]
        utilities = self.utilities
        for hname, hobj in utilities:
            results.append(dict(title=hobj.name,
                                description=hobj.description,
                                value=hname))
        return results

    def _catalog_search(self, portal_type, portlets, start, size):
        catalog = getToolByName(self.context, 'portal_catalog')
        all_brains = catalog(portal_type=portal_type,
                             language="ALL")
        return all_brains.actual_result_count, \
               [Result(x, portal_type, portlets) for x in
                all_brains[start:start+size]]

    def batchSearch(self):
        context = self.context
        request = self.request
        request.response.setHeader('Content-Type',
                                   'application/json;charset=utf-8')
        search_query = request.get('searchQuery')
        b_start = request.get('b_start', 0)
        b_size = request.get('b_size', 20)
        really_checked_docs = request.get('really_checked_docs', 0)
        flags = request.get('flags', 0)
        portlets = request.get('portlets', False)
        portal_type = request.get('content_type', [])

        result_json = {}
        results = []

        if not portal_type or not search_query:
            result_json['results'] = results
            return json.dumps(result_json)
        
        total_documents_count, search_results = \
            self._catalog_search(portal_type, portlets, b_start, b_size)

        if not search_results:
            # stop client side queries
            result_json['results'] = None
            return json.dumps(result_json)

        for search_result in search_results:
            if search_result.text:
                really_checked_docs += 1
                inner_results = utility.text_search(search_result.text,
                                                    search_query,
                                                    flags=flags,
                                                    preview=True)
                for result in inner_results:
                    result['url'] = search_result['url']
                    result['id'] = search_result['id']
                    result['uid'] = search_result['uid']
                    result['title'] = search_result['title']
                    result['icon'] = search_result['icon']
                    result['normalized_portal_type'] = \
                        search_result['normalized_portal_type']
                results.extend(inner_results)

        result_json['total_documents_count'] = total_documents_count
        result_json['really_checked_docs'] = really_checked_docs
        result_json['results'] = results
        return json.dumps(result_json)

    def get_content_diff_info(self, search_result, search_query, replace_query,
                              flags=0):
        if search_result.text:
            inner_results = \
                search_result.get_possible_replacements(search_query,
                                                        replace_query,
                                                        flags)
            for result in inner_results:
                result['url'] = search_result['url']
                result['id'] = search_result['id']
                result['uid'] = search_result['uid']
                result['title'] = search_result['title']
                result['normalized_portal_type'] = \
                    search_result['normalized_portal_type']
            return inner_results
        return []

    def batchReplace(self):
        context = self.context
        request = self.request
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        search_query = request.get('searchQuery')
        replace_query = request.get('replaceQuery')
        replace_type = request.get('replace_type')
        b_start = request.get('b_start', 0)
        b_size = request.get('b_size', 20)
        really_checked_docs = request.get('really_checked_docs', 0)
        flags = request.get('flags', 0)
        portlets = request.get('portlets', False)
        portal_type = request.get('content_type', [])

        result_json = {}
        results = []

        if not portal_type or not search_query \
                or (not replace_query and not replace_type):
            result_json['results'] = results
            return json.dumps(result_json)

        total_documents_count, search_results = \
            self._catalog_search(portal_type, portlets, b_start, b_size)

        if not search_results:
            # stop client side queries
            result_json['results'] = None
            return json.dumps(result_json)

        if replace_type:
            # let's load the proper replace type
            utilities = [u for u in self.utilities if u[0] == replace_type]
            replace_query = utilities[0][1].repl
            # fix multiple replacement
            utilities[0][1].context = None

        for search_result in search_results:
            inner_results = self.get_content_diff_info(search_result,
                                                       search_query,
                                                       replace_query,
                                                       flags=flags)
            if inner_results:
                really_checked_docs += 1
            for ir in inner_results:
                ir['icon'] = search_result['icon']
            results.extend(inner_results)

        result_json['total_documents_count'] = total_documents_count
        result_json['really_checked_docs'] = really_checked_docs
        result_json['results'] = results
        return json.dumps(result_json)

    def _createNewVersion(self, obj):
        _ = getToolByName(self.context, 'translation_service').utranslate
        if isObjectChanged(obj) and isObjectVersioned(obj):
            maybeSaveVersion(obj, comment=_(msgid="Bulk text replacement",
                                            domain="rt.bulkmodify",
                                            context=obj))

    def replaceText(self):
        context = self.context
        request = self.request
        portal = getToolByName(context, 'portal_url').getPortalObject()
        request.response.setHeader('Content-Type',
                                   'application/json;charset=utf-8')
        # ids MUST be of the same objects
        paths_with_match_number = request.get('id')
        search_query = request.get('searchQuery')
        replace_query = request.get('replaceQuery')
        replace_type = request.get('replace_type')
        update_time = request.get('update_time', False)
        new_version = request.get('new_version', False)
        portlets = request.get('portlets', False)
        flags = request.get('flags', 0)
        tobe_updated = False
        obj = None
        replace_query_klass = None

        messages = []

        if paths_with_match_number and search_query \
                and (replace_query or replace_type):
            
            if replace_type:
                # let's load the proper replace type
                utilities = [u for u in self.utilities if u[0] == replace_type]
                replace_query_klass = utilities[0][1]
                # fix multiple replacement
                replace_query_klass.context = None
                replace_query = replace_query_klass.repl

            doc_path = None  # Trick to make assertion work

            diff_indexes = []
            for document_path_with_match_number in paths_with_match_number:
                match = path_id_pattern.match(document_path_with_match_number)
                if doc_path:
                    assert document_path_with_match_number.startswith(doc_path)
                    doc_path, match_number = match.groups()
                else:
                    doc_path, match_number = match.groups()
                    obj = portal.restrictedTraverse(doc_path, default=None)
                diff_indexes.append(int(match_number))

            if obj:
                result_obj = Result(obj, [], portlets)
                if replace_type:
                    replace_query_klass.context = obj
                diff_info = self.get_content_diff_info(
                    result_obj, search_query, replace_query,
                    flags=flags)
                if diff_info:
                    diffs = [x[1] for x in enumerate(diff_info)
                             if x[0] in diff_indexes]
                    for result in result_obj.replace(diffs):
                        if result:
                            tobe_updated = True
                            messages.append({'status': 'OK'})
                        else:
                            messages.append({'status': 'warn',
                                             'message': 'No change is needed'})
                else:
                    messages.append({'status': 'error',
                                     'message': "Don't know how to handle %s" %
                                                obj.absolute_url()})
            else:
                messages.append({'status': 'error',
                                 'message': 'Document "%s" not found' %
                                            obj.absolute_url()})

            # check if we need to update some other data
            if tobe_updated:
                if update_time or new_version:
                    # a little dirty, but this way I'm sure all is updated
                    obj.reindexObject()
                    if new_version:
                        self._createNewVersion(obj)

        return json.dumps(messages)

