# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from .configuration import sel_adr_type


class ContactMechanism(metaclass=PoolMeta):
    __name__ = 'party.contact_mechanism'

    vcard_type = fields.Selection(sel_adr_type,
        'VCard Type',
        help='Type of contact for use in VCards.')

    @classmethod
    def default_vcard_type(cls):
        Configuration = Pool().get('party.configuration')
        cfg = Configuration(1)
        return cfg.contact_type

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Party = pool.get('party.party')

        actions = iter(args)
        parties = set()
        for cm, values in zip(actions, actions):
            parties.add(cm[0].party)
        super().write(*args)
        for party in parties:
            party.ctag = party.increase_ctag(party.ctag)
        Party.save(parties)

    #def get_vcard_lines(self):
    #    """ get content as VCard-Lines
    #    """
    #    if self.type in ['phone', 'mobile', 'fax', 'sip']:
    #        type_lst = []
    #        type_lst.append(self.vcard_type or 'WORK')
    #        type_lst.append({
    #                    'phone': 'VOICE',
    #                    'mobile': 'CELL',
    #                    'fax': 'FAX',
    #                    'sip': 'SIP',
    #                }[self.type])
    #        return 'TEL;TYPE="%s";VALUE=text:%s' % (
    #                ','.join(type_lst),
    #                self.value,
    #            )
    #    elif self.type == 'email':
    #        return 'EMAIL;TYPE=%s:%s' % (self.vcard_type or 'WORK', self.value)
    #    elif self.type in ['skype', 'irc', 'jabber']:
    #        type_lst = []
    #        type_lst.append(self.vcard_type or 'WORK')
    #        type_lst.append(self.type)
    #        return 'IMPP;X-SERVICE-TYPE="%(type)s":%(val)s' % {
    #            'type': ','.join(type_lst),
    #            'val': self.value}
    #    elif self.type == 'website':
    #        return 'URL:%s' % (self.value)
    #    return ''
