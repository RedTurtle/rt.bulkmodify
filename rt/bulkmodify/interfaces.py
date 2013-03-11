# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute


class IBulkModifyContentChanger(Interface):
    """An object that is able to readn and change text data inside a content's field"""

    text = Attribute('''Text attribute getter & setter''')



