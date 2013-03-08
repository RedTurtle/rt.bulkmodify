# -*- coding: utf-8 -*-

import logging

from zope.i18nmessageid import MessageFactory

messageFactory = MessageFactory('rt.bulkmodify')
logger = logging.getLogger('rt.bulkmodify')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
