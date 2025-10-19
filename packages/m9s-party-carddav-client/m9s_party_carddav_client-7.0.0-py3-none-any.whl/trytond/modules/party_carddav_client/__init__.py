# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool

from . import party, user

__all__ = ['register']


def register():
    Pool.register(
        party.Party,
        party.PartyCardDAVCollection,
        user.User,
        module='party_carddav_client', type_='model')
    Pool.register(
        module='party_carddav_client', type_='wizard')
    Pool.register(
        module='party_carddav_client', type_='report')
