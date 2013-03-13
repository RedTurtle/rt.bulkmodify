# -*- coding: utf-8 -*-

from rt.bulkmodify import logger

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-rt.bulkmodify:uninstall')
        logger.info("Uninstall done")
