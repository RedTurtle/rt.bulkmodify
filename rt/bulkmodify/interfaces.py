# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute


class IBulkModifyContentChanger(Interface):
    """An object that is able to readn and change text data inside a content's field"""

    text = Attribute('''Text attribute getter & setter''')


class IBulkModifyReplacementHandler(Interface):
    """An utility that can manage special regex substitution"""

    name = Attribute('''Name of the handler''')
    descrition = Attribute('''An exhaustive description of the handler''')

    def repl(match):
        """A callable that can be passed to re.sub.
        Must accept the re.MatchObject and return the string to be replaced
        """ 
