# -*- coding: utf-8 -*-

import unittest
import json

from zope import interface
from zope.component import queryUtility

from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import logout

HTML1 = """<p>
    <ul>   
        <li>Lorem ipsum dolor <a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>, sed do eiusmod tempor incididunt</li>
        <li>Duis aute irure dolor in <a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a> esse cillum dolore eu fugiat nulla pariatur</li>
    </ul>
</p>
"""

HTML2 = """<p>
    Excepteur sint occaecat cupidatat <a target="_blank" href="http://loripsum.net/">non proident, sunt in culpa qui</a> officia deserunt mollit anim id est laborum.
</p>
"""

HTML3 = """<p>
    <ul>   
        <li>Sed tristique accumsan arcu et congue. <a target="_blank" href="http://loripsum.net/">Duis ac augue diam</a>, dignissim imperdiet lectus</li>
        <li>Integer<a target="_blank" href="http://loripsum.net/">facilisis cursus</a> iaculis</li>
    </ul>
</p>
"""

re_pattern = r'(?P<link><a target="_blank" href="(?P<url>.*?)">(?P<text>[^<]*.)</a>)'
re_subn_pattern = r'<a href="\g<url>" class="external-link">\g<text></a>'

class BaseTestCase(unittest.TestCase):
    
    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        self.generateContents()
    
    def generateContents(self):
        portal = self.layer['portal']
        portal.invokeFactory('Document', 'page1', title="Page 1",
                             text=HTML1)
        portal.invokeFactory('News Item', 'news1', title="News 1",
                             text=HTML2)
        portal.invokeFactory('Document', 'page2', title="Page 2",
                             text=HTML3)
        portal.invokeFactory('Link', 'link1', title="Link 1",
                             remoteUrl='http://plone.org/')
