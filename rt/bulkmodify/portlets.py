# coding=utf-8
from itertools import chain
from plone.portlet.static.static import Assignment as StaticAssignment
from plone.portlets.interfaces import ILocalPortletAssignable, IPortletManager, \
    IPortletAssignmentMapping
from zope.component import getUtility, getMultiAdapter


class PortletFixer(object):
    """ Magical portlet debugging view """ 
    managers = ['plone.leftcolumn', 'plone.rightcolumn']

    def __init__(self, portal):
        self.portal = portal

    def find_all_static_assignments(self):
        brains = self.portal.portal_catalog(show_inactive=True,
                                            language="ALL")

        portal = self.portal

        class FakeBrain(object):

            def getObject(self):
                return portal

        for brain in chain((FakeBrain(),), brains):
            content = brain.getObject()
            if not ILocalPortletAssignable.providedBy(content):
                continue
         
            for manager_name in self.managers: 
                manager = getUtility(IPortletManager,
                                     name=manager_name,
                                     context=content)
 
                mapping = getMultiAdapter((content, manager),
                                          IPortletAssignmentMapping)
 
                for ignored, assignment in mapping.items():
                    if isinstance(assignment, StaticAssignment):
                        yield assignment 
     
    def __call__(self):
        assignments = list(self.find_assignments())
        for assignment in assignments:
            return assignment
