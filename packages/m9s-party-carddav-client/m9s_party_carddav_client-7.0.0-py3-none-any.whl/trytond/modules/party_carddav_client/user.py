# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.i18n import gettext
from trytond.model import ModelView, fields
#from trytond.modules.dav_client.user import dav_request
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


class User(metaclass=PoolMeta):
    __name__ = "res.user"
    default_carddav_collection = fields.Many2One('webdav.carddav_collection',
        'Default Addressbook',
        domain=[('user', '=', Eval('id'))],
        help='Select the addressbook used for new parties.\n'
        'When empty the default addressbook "Contacts" '
        'will be used for uploads.')

    @classmethod
    def ensure_addressbook(cls, records):
        pool = Pool()
        CardDAVCollection = pool.get('webdav.carddav_collection')

        for record in records:
            username = record.webdav_username
            carddav_url = (
                f"{record.webdav_url}/addressbooks/users/{username}/")
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
