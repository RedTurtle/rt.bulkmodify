# -*- coding: utf-8 -*-

from zope.interface import implements

from zope.site.hooks import getSite

from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware

from rt.bulkmodify import messageFactory as _
from rt.bulkmodify.interfaces import IBulkModifyReplacementHandler

class InternalLinkToUIDUtility(object):
    implements(IBulkModifyReplacementHandler)
    
    context = None
    name = _('utility_internal_link_to_uid_name',
             default=u"Convert internal links to resolveuid usage")
    description = _('utility_internal_link_to_uid_description',
                    default=u"If the match contains a group called <url> and this group is an internal link to "
                            u"a site content, let's transform it to a link using resolveuid.")

    @classmethod
    def repl(cls, match):
        groups = match.groupdict()
        if groups.get('url'):
            old_url = groups.get('url')
            if not old_url.startswith('resolveuid/'):
                site = getSite()
                portal_url = site.portal_url
                site_url = site.absolute_url()
                if portal_url.isURLInPortal(old_url, cls.context or None):
                    path = old_url.replace('%s/' % site_url, '', 1)
                    suffix = []
                    content = None
                    while path:
                        content = site.unrestrictedTraverse(path, default=None)
                        if IUUIDAware.providedBy(content):
                            break
                        suffix.insert(0, path.split('/')[-1])
                        path = '/'.join(path.split('/')[:-1])
                    if content and IUUIDAware.providedBy(content):
                        uuid = IUUID(content)
                        suffix.insert(0, '')
                        new_url = 'resolveuid/%s' % uuid + '/'.join(suffix)
                        return match.string[match.start():match.end()].replace(old_url,
                                                                               new_url)
        return match.string[match.start():match.end()]
        
