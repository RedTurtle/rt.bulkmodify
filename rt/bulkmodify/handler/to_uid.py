# -*- coding: utf-8 -*-

from zope.interface import implements

from zope.site.hooks import getSite

#from Products.CMFCore.PortalContent import PortalContent

from plone.uuid.interfaces import IUUID

from rt.bulkmodify import messageFactory as _
from rt.bulkmodify.interfaces import IBulkModifyReplacementHandler

class InternalLinkToUIDUtility(object):
    implements(IBulkModifyReplacementHandler)
    
    name = _('utility_internal_link_to_uid_name',
             default=u"Convert internal links to resolveuid usage")

    descrition = _('utility_internal_link_to_uid_description',
                   default=u"If the match contains a group called <url>, and a group called <text>, "
                           u"and the group called URL is an internal link to a site content, let's transform "
                           u"it to a link using resolveuid:\n"
                           u"<a href=\"http://site/.../resolveuid/uid/...\" class=\"internal-link\">text</a>")
    
    def repl(self, match):
        groups = match.groupdict()
        if groups.get('url'):
            old_url = groups.get('url')
            site = getSite()
            portal_url = site.portal_url
            site_url = site.absolute_url()
            if portal_url.isURLInPortal(old_url):
                path = old_url.replace('%s/' % site_url, '', 1)
                content = None
                while not content:
                    content = site.unrestrictedTraverse(path, default=None)
                    if 
                content = site.unrestrictedTraverse(path, default=None)
                if content:
                    uuid = IUUID(content)
                    return match.string[match.start():match.end()].replace(old_url,
                                                                           site_url+'/resolveuid/%s' % uuid)
        return match.string[match.start():match.end()]
        
