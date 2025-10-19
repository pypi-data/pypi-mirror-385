# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import Index, ModelSQL, ModelView, Unique, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    carddav_collection = fields.Function(
        fields.Many2One('webdav.carddav_collection',
        'CardDAV Addressbook',
        domain=[
            ('user', '=', Eval('context_user', -1)),
            ]),
        'get_carddav_collection', setter='set_carddav_collection',
        searcher='search_carddav_cllection')
    context_user = fields.Function(
        fields.Many2One('res.user', 'Context User'),
        'on_change_with_context_user')

    def on_change_with_context_user(self, name=None):
        return Transaction().user

    @staticmethod
    def default_carddav_collection():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        if user.default_carddav_collection:
            return user.default_carddav_collection.id

    def get_carddav_collection(self, name):
        pool = Pool()
        CardDAVCollectionRel = pool.get('party.carddav_collection_rel')

        rel = CardDAVCollectionRel.search([
                ('user', '=', Transaction().user),
                ('party', '=', self.id),
                ], limit=1)
        if rel:
            return rel[0].carddav_collection.id

    @classmethod
    def set_carddav_collection(cls, parties, name, value):
        pool = Pool()
        CardDAVCollectionRel = pool.get('party.carddav_collection_rel')

        user = Transaction().user
        for party in parties:
            existing = CardDAVCollectionRel.search([
                ('party', '=', party.id),
                ('user', '=', user),
            ], limit=1)

            if value:
                if existing:
                    existing[0].carddav_collection = value
                    existing[0].save()
                else:
                    CardDAVCollectionRel.create([{
                        'party': party.id,
                        'user': user,
                        'carddav_collection': value,
                    }])
            else:
                if existing:
                    existing[0].delete()

    @classmethod
    def search_nextcloud_addressbook(cls, name, clause):
        pool = Pool()
        CardDAVCollectionRel = pool.get('party.carddav_collection_rel')

        rels = CardDAVCollectionRel.search([
            ('user', '=', Transaction().user),
            ('carddav_collection',) + tuple(clause[1:])
        ])
        return [('id', 'in', [r.party.id for r in rels])]

    @fields.depends('carddav_collection')
    def on_change_carddav_collection(self):
        pool = Pool()
        User = pool.get('res.user')

        user = User(Transaction().user)
        if self.carddav_collection:
            coll = user.ensure_dav_collection(self.carddav_collection)
            print(coll)


    #@classmethod
    #def create(cls, vlist):
    #    vlist = [x.copy() for x in vlist]
    #    for values in vlist:
    #        if not values.get('uuid'):
    #            values['uuid'] = str(uuid.uuid4())
    #    return super().create(vlist)

    #@classmethod
    #def write(cls, *args):
    #    actions = iter(args)
    #    for party, values in zip(actions, actions):
    #        if not values.get('ctag'):
    #            values['ctag'] = cls.increase_ctag(party[0].ctag)
    #    super().write(*args)


class PartyCardDAVCollection(ModelSQL, ModelView):
    "CardDAV Collection per Party and User"
    __name__ = "party.carddav_collection_rel"
    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    user = fields.Many2One('res.user', 'User', required=True,
        ondelete='CASCADE')
    carddav_collection = fields.Many2One('webdav.carddav_collection',
        'CardDAV Addressbook', required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('party_user_unique', Unique(t, t.party, t.user),
                    'party_carddav_client.msg_party_user_unique'),
                ])
        cls._sql_indexes.update({
            Index(t, (t.party, Index.Equality())),
            Index(t, (t.user, Index.Equality())),
        })

