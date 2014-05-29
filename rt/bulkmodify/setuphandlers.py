# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from rt.bulkmodify import logger

def migrateTo41(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-rt.bulkmodify:default', 'jsregistry')
    setup_tool.runImportStepFromProfile('profile-rt.bulkmodify:default', 'cssregistry')
    logger.info("Migrated to 0.4.1")
