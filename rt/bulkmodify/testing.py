
from zope.configuration import xmlconfig

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile


class BulkModify(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import rt.bulkmodify
        xmlconfig.file('configure.zcml',
                       rt.bulkmodify,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'rt.bulkmodify:default')


BULK_MODIFY_FIXTURE = BulkModify()
BULK_MODIFY_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(BULK_MODIFY_FIXTURE, ),
                       name="BulkModify:Integration")
BULK_MODIFY_SEMANTIC_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(BULK_MODIFY_FIXTURE, ),
                       name="BulkModify:Functional")

