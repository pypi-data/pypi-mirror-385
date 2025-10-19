# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from .configuration import sel_adr_type


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    vcard_type = fields.Selection(sel_adr_type,
        'VCard Type',
        help='Type of address for use in VCards.')

    @classmethod
    def default_vcard_type(cls):
        Configuration = Pool().get('party.configuration')
        cfg = Configuration(1)
        return cfg.adr_type

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Party = pool.get('party.party')

        actions = iter(args)
        parties = set()
        for addr, values in zip(actions, actions):
            parties.add(addr[0].party)
        super().write(*args)
        for party in parties:
            party.ctag = party.increase_ctag(party.ctag)
        Party.save(parties)

    #def get_vcard_lines(self):
    #    """ get content as VCard-Lines
    #    """
    #    # ADR;TYPE=work:<po-box>;<extend address>;<street+number>;
    #    # <city>;<region>;<zip>;<country>
    #    # LABEL;TYPE=<type>:<readable line of address>
    #    typ_lst = []
    #    if hasattr(self, 'invoice'):
    #        if self.invoice is True:
    #            typ_lst.append('POSTAL')
    #    if hasattr(self, 'delivery'):
    #        if self.delivery is True:
    #            typ_lst.append('PARCEL')
    #    typ_lst.append(self.vcard_type)

    #    # cleanup content of 'street'
    #    lst_adr = []
    #    for x in (self.street or '').split('\n'):
    #        if len(x.strip()) > 0:
    #            lst_adr.append(x)
    #    txt_adr = '\\n'.join(lst_adr)

    #    adr_line = ';'.join([
    #        'ADR;TYPE="%(type)s":' % {'type': ','.join(typ_lst)},
    #        self.name or '',
    #        txt_adr,
    #        self.city or '',
    #        self.subdivision.name if self.subdivision else '',
    #        self.postal_code or '',
    #        self.country.name if self.country else ''
    #        ])

    #    label_line = 'LABEL;TYPE="%(type)s":%(adr)s' % {
    #        'type': ','.join(typ_lst),
    #        'adr': self.full_address.replace('\n', '\\n ')}
    #    return [adr_line, label_line]

    def vcard2values(self, adr):
        '''
        Convert adr from vcard to values for create or write
        '''
        pool = Pool()
        Country = pool.get('country.country')
        Subdivision = pool.get('country.subdivision')

        vals = {}
        vals['street'] = adr.value.street or ''
        vals['city'] = adr.value.city or ''
        vals['postal_code'] = adr.value.code or ''
        if adr.value.country:
            countries = Country.search([
                    ('rec_name', '=', adr.value.country),
                    ], limit=1)
            if countries:
                country, = countries
                vals['country'] = country.id
                if adr.value.region:
                    subdivisions = Subdivision.search([
                            ('rec_name', '=', adr.value.region),
                            ('country', '=', country.id),
                            ], limit=1)
                    if subdivisions:
                        subdivision, = subdivisions
                        vals['subdivision'] = subdivision.id
        return vals
