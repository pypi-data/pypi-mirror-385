# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

import xml.etree.ElementTree as ET

import requests

from requests.auth import HTTPBasicAuth

from trytond.i18n import gettext
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta

from .exceptions import DAVConnectionTestError


class User(metaclass=PoolMeta):
    __name__ = "res.user"
    webdav_url = fields.Char("WebDAV URL",
        help="The base URL to your WebDAV server\n"
            "e.g. http://<host>:<port>/remote.php/dav/")
    webdav_username = fields.Char("WebDAV Username",
        help="The name of the user used to authenticate with "
        "the WebDAV server.")
    webdav_password = fields.Char("WebDAV Password",
        help="The password of the authenticating user.\n"
        "Preferably use an app password created in the backend.")
    carddav_collections = fields.One2Many('webdav.carddav_collection',
        'user', 'CardDAV Collections (Addressbooks)')
    caldav_collections = fields.One2Many('webdav.caldav_collection',
        'user', 'CalDAV Collections (Calendars)')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'test_webdav_connection': {},
            'update_dav_collections': {},
            })

    @property
    def base_url(self):
        return self.webdav_url.rstrip('/')

    def dav_request(self, url, mode='PROPFIND', depth='1', body=None):
        """
        Send PROPFIND and return XML
        """
        headers = {
            "Depth": depth,
            "Content-Type": "application/xml; charset=utf-8",
            }
        auth = HTTPBasicAuth(self.webdav_username, self.webdav_password)
        r = requests.request(
            mode, url, headers=headers, data=body, auth=auth, timeout=10)
        r.raise_for_status()
        return r.text

    def list_dav_collections(self, url, service="carddav"):
        """
        List CardDAV/CalDAV collections

        For the sake of simplicity provide already here nextcloud compatibility
        """

        # XML-Namespace-Map
        ns = {
            "d": "DAV:",
            "card": "urn:ietf:params:xml:ns:carddav",
            "cal": "urn:ietf:params:xml:ns:caldav",
            "cs": "http://calendarserver.org/ns/",
            "nc": "http://nextcloud.org/ns/",
            }

        if service == "carddav":
            namespace = 'xmlns:card="urn:ietf:params:xml:ns:carddav"'
            description = '<card:addressbook-description/>'
        else:
            namespace = 'xmlns:cal="urn:ietf:params:xml:ns:caldav"'
            description = '<cal:calendar-description/>'

        body = f"""<?xml version="1.0"?>
        <d:propfind xmlns:d="DAV:"
                    {namespace}
                    xmlns:cs="http://calendarserver.org/ns/"
                    xmlns:nc="http://nextcloud.org/ns/">
          <d:prop>
            <d:displayname/>
            {description}
            <cs:getctag/>
            <nc:ctag/>
          </d:prop>
        </d:propfind>"""

        xml_text = self.dav_request(url, 'PROPFIND', '1', body)
        tree = ET.fromstring(xml_text)

        collections = []
        for resp in tree.findall("d:response", ns):
            href = resp.findtext("d:href", namespaces=ns)
            print(href)
            url = href.split('/')[-2]
            displayname = resp.findtext(
                "d:propstat/d:prop/d:displayname", namespaces=ns)
            desc = (
                resp.findtext(
                    "d:propstat/d:prop/card:addressbook-description",
                    namespaces=ns)
                or resp.findtext(
                    "d:propstat/d:prop/cal:calendar-description",
                    namespaces=ns)
            )

            # Suche nach ctag oder getctag (Nextcloud compat 23-30)
            ctag = (
                resp.findtext("d:propstat/d:prop/cs:getctag", namespaces=ns)
                or resp.findtext("d:propstat/d:prop/nc:ctag", namespaces=ns)
            )
            collection = {
                'url': url,
                'displayname': displayname,
                'description': desc,
                'ctag': ctag,
                }
            collections.append(collection)
        return collections

    @classmethod
    @ModelView.button
    def test_webdav_connection(cls, records):
        for record in records:
            try:
                response = requests.request(
                    "PROPFIND",
                    record.webdav_url,
                    auth=HTTPBasicAuth(
                        record.webdav_username, record.webdav_password),
                    headers={"Depth": "0"},
                    timeout=10,
                    )
                if response.status_code in (200, 207):
                    status = gettext('dav_client.msg_dav_success')
                elif response.status_code == 401:
                    status = gettext('dav_client.msg_dav_401')
                else:
                    status = gettext('dav_client.msg_dav_unexpected',
                        status_code=response.status_code,
                        reason=response.reason)
                raise DAVConnectionTestError(gettext(
                        'dav_client.msg_dav_status',
                        status=status))
            except requests.exceptions.RequestException as e:
                raise DAVConnectionTestError(gettext(
                        'dav_client.msg_dav_status',
                        status=e))

    @classmethod
    @ModelView.button
    def update_dav_collections(cls, records):
        cls.update_carddav_collection(records)
        cls.update_caldav_collection(records)

    @classmethod
    def update_carddav_collection(cls, records):
        pool = Pool()
        CardDAVCollection = pool.get('webdav.carddav_collection')

        for record in records:
            username = record.webdav_username
            carddav_url = (
                f"{record.base_url}/addressbooks/users/{username}/")
            collections = record.list_dav_collections(
                carddav_url, 'carddav')

            card_collections = []
            for collection in collections:
                displayname = collection['displayname']
                url = collection['url']
                if (displayname
                        and url
                        and not url.startswith('z-')  # system
                        and '_shared_by_' not in url):  # shared
                    stored_collections = CardDAVCollection.search([
                        ('user', '=', record.id),
                        ('url', '=', collection['url']),
                        ], limit=1)
                    if stored_collections:
                        stored_collection = stored_collections[0]
                        if stored_collection.ctag == collection['ctag']:
                            continue
                        card_collection = stored_collection
                    else:
                        card_collection = CardDAVCollection()
                        card_collection.user = record
                        card_collection.url = collection['url']
                    card_collection.name = collection['displayname']
                    card_collection.description = collection['description']
                    card_collection.ctag = collection['ctag']
                    card_collections.append(card_collection)
            CardDAVCollection.save(card_collections)

    @classmethod
    def update_caldav_collection(cls, records):
        pool = Pool()
        CalDAVCollection = pool.get('webdav.caldav_collection')

        for record in records:
            username = record.webdav_username
            caldav_url = (
                f"{record.base_url}/calendars/{username}/")
            collections = record.list_dav_collections(
                caldav_url, 'caldav')

            cal_collections = []
            for collection in collections:
                displayname = collection['displayname']
                url = collection['url']
                if displayname and url:
                    stored_collections = CalDAVCollection.search([
                        ('user', '=', record.id),
                        ('url', '=', collection['url']),
                        ], limit=1)
                    if stored_collections:
                        stored_collection = stored_collections[0]
                        if stored_collection.ctag == collection['ctag']:
                            continue
                        cal_collection = stored_collection
                    else:
                        cal_collection = CalDAVCollection()
                        cal_collection.user = record
                        cal_collection.url = collection['url']
                    cal_collection.name = collection['displayname']
                    cal_collection.description = collection['description']
                    cal_collection.ctag = collection['ctag']
                    cal_collections.append(cal_collection)
            CalDAVCollection.save(cal_collections)
