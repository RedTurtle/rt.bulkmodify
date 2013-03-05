# -*- coding: utf-8 -*-

import re
import unittest

from rt.bulkmodify.utility import text_replace
from rt.bulkmodify.utility import text_search

HTML = """
<p>
Nam erat nisi, tempus eget cursus vitae; pretium et velit. Nullam laoreet consequat augue, quis congue libero sodales vitae. Nulla venenatis eros et sem mollis posuere. Cras eu orci eu sem viverra pharetra ac sed ipsum. Donec tincidunt, nisi mattis porta convallis, enim mauris porttitor justo, sed molestie lectus ante eget odio. Vivamus tempus malesuada feugiat. Morbi venenatis, leo a sagittis tempor; nulla tortor malesuada lorem, eu mattis tortor orci quis elit. Morbi posuere nunc vitae purus blandit sit amet vehicula felis varius. Etiam vel adipiscing ante. Suspendisse gravida, felis sed scelerisque ultricies, mauris massa lacinia eros, ut imperdiet lacus mi et nunc. Duis euismod auctor dolor vitae vehicula. Curabitur congue libero at mauris dignissim fringilla non eu lorem.
<a class="internal-link"
   href="http://foo.org/aaa/bar.exe/at_download/file">BAR file</a>
</p>
<p>
Nullam eget nibh ante. Etiam suscipit magna id dui dictum eget ultricies diam hendrerit. Nulla tincidunt odio sed lacus mollis fringilla. Praesent auctor neque leo, id tincidunt odio. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed at mauris mi, sodales euismod lacus. Aliquam ac nisi lacus.
</p>
<p>
    <a href="http://foo.org/aaa/foo.pdf/at_download/file/@@someview" class="internal-link">FOO
file</a><br />

Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse potenti. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Nullam sodales ante eget enim sodales viverra! Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus ac sapien at lorem semper adipiscing quis sit amet ligula. Maecenas orci lacus; ultricies eget blandit nec; molestie sit amet purus. Praesent risus est, pretium eu rhoncus vitae, bibendum in elit.
</p>
"""

class TestUtility(unittest.TestCase):

    def setUp(self):
        pass

    def test_search(self):
        self.assertEqual(len(text_search(HTML,
                                     r'(?P<link><a.*?href="(?P<url>http://.*?/(?P<filename>.*?)/at_download/file/?.*?)".*?>)',
                                     flags=re.DOTALL)),
                         2)

    
    def test_replace(self):
        self.assertTrue(text_replace('... http://foo.org/aaa/foo.pdf/at_download/file/@@someview ...',
                                      r'(?P<url>http://.*/(?P<filename>.*)/at_download/file)',
                                      r'\g<url>/\g<filename>'),
                         '... http://foo.org/aaa/foo.pdf/at_download/file/foo.pdf/@@someview ...')

