# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class DavClientTestCase(ModuleTestCase):
    "Test Dav Client module"
    module = 'dav_client'


del ModuleTestCase
