# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool

from . import user, webdav


__all__ = ['register']


def register():
    Pool.register(
        user.User,
        webdav.CardDAVCollection,
        webdav.CalDAVCollection,
        module='dav_client', type_='model')
    Pool.register(
        module='dav_client', type_='wizard')
    Pool.register(
        module='dav_client', type_='report')
