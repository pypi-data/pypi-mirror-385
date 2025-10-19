# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import uuid

import vobject

from trytond import __version__
from trytond.model import Unique, fields
from trytond.pool import Pool, PoolMeta
from trytond.report import Report


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    uuid = fields.Char('UUID', required=True, strip=False,
            help='Universally Unique Identifier')
    vcard = fields.Function(fields.Text('VCard'),
        'get_vcard')
    ctag = fields.Char('CTag', readonly=True,
            help='Change tag for sync tracking')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('uuid_uniq',
                    Unique(t, t.uuid),
                    'party_vcard.msg_uuid_unique'),
                ])

    @classmethod
    def __register__(cls, module_name):
        super().__register__(module_name)
        to_update = cls.search([
                ('uuid', '=', None)
                ])
        if to_update:
            for record in to_update:
                cls.write([record], {
                    'uuid': str(uuid.uuid4()),
                    })

    @staticmethod
    def default_ctag():
        return '0'

    def get_vcard(self, name):
        return self.create_vcard().serialize()

    def create_vcard(self):
        '''
        Return a vcard instance of vobject for the party
        '''
        vcard = vobject.vCard()
        if not hasattr(vcard, 'n'):
            vcard.add('n')
        vcard.n.value = vobject.vcard.Name(self.full_name)
        if not hasattr(vcard, 'fn'):
            vcard.add('fn')
        vcard.fn.value = self.full_name
        if self.uuid:
            if not hasattr(vcard, 'uid'):
                vcard.add('uid')
            vcard.uid.value = self.uuid
        if not hasattr(vcard, 'prodid'):
            vcard.add('prodid')
            vcard.prodid.value = ('-//m9s.biz//trytond-webdav %s//EN'
                % __version__)

        i = 0
        for address in self.addresses:
            try:
                adr = vcard.contents.get('adr', [])[i]
            except IndexError:
                adr = None
            if not adr:
                adr = vcard.add('adr')
            if not hasattr(adr, 'value'):
                adr.value = vobject.vcard.Address()
            if address.vcard_type:
                adr.type_param = address.vcard_type
            if hasattr(self, 'invoice'):
                if self.invoice:
                    adr.type_param += ',POSTAL'
            if hasattr(self, 'delivery'):
                if self.delivery:
                    adr.type_param += ',PARCEL'
            adr.value.street = address.street and address.street + (
                address.name and (" / " + address.name) or '') or ''
            adr.value.city = address.city or ''
            if address.subdivision:
                adr.value.region = address.subdivision.name or ''
            adr.value.code = address.postal_code or ''
            if address.country:
                adr.value.country = address.country.name or ''
            label = vcard.add('label')
            label.value = address.full_address.replace('\n', '\\n ')
            i += 1
        try:
            older_addresses = vcard.contents.get('adr', [])[i:]
        except IndexError:
            older_addresses = []
        for adr in older_addresses:
            vcard.contents['adr'].remove(adr)

        email_count = 0
        tel_count = 0
        url_count = 0
        for cm in self.contact_mechanisms:
            if cm.type == 'email':
                try:
                    email = vcard.contents.get('email', [])[email_count]
                except IndexError:
                    email = None
                if not email:
                    email = vcard.add('email')
                email.value = cm.value
                if not hasattr(email, 'type_param'):
                    email.type_param = 'internet'
                elif 'internet' not in email.type_param.lower():
                    email.type_param += ',internet'
                if cm.vcard_type:
                    email.type_param += ',' + cm.vcard_type
                email_count += 1
            elif cm.type in ('phone', 'mobile', 'fax'):
                try:
                    tel = vcard.contents.get('tel', [])[tel_count]
                except IndexError:
                    tel = None
                if not tel:
                    tel = vcard.add('tel')
                tel.value = cm.value
                if cm.type == 'mobile':
                    if not hasattr(tel, 'type_param'):
                        tel.type_param = 'cell'
                    elif 'cell' not in tel.type_param.lower():
                        tel.type_param += ',cell'
                elif cm.type == 'fax':
                    if not hasattr(tel, 'type_param'):
                        tel.type_param = 'fax'
                else:
                    if not hasattr(tel, 'type_param'):
                        tel.type_param = 'voice'
                if cm.vcard_type:
                    tel.type_param += ',' + cm.vcard_type
                tel_count += 1
            elif cm.type == 'website':
                try:
                    url = vcard.contents.get('url', [])[url_count]
                except IndexError:
                    url = None
                if not url:
                    url = vcard.add('url')
                url.value = cm.value
                url_count += 1

        try:
            older_emails = vcard.contents.get('email', [])[email_count:]
        except IndexError:
            older_emails = []
        for email in older_emails:
            vcard.contents['email'].remove(email)

        try:
            older_tels = vcard.contents.get('tel', [])[tel_count:]
        except IndexError:
            older_tels = []
        for tel in older_tels:
            vcard.contents['tel'].remove(tel)

        try:
            older_urls = vcard.contents.get('url', [])[url_count:]
        except IndexError:
            older_urls = []
        for url in older_urls:
            vcard.contents['url'].remove(url)
        # print(vcard.prettyPrint())
        return vcard

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('uuid'):
                values['uuid'] = str(uuid.uuid4())
        return super().create(vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        for party, values in zip(actions, actions):
            if not values.get('ctag'):
                values['ctag'] = cls.increase_ctag(party[0].ctag)
        super().write(*args)

    @classmethod
    def copy(cls, parties, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('uuid', None)
        return super().copy(parties, default=default)

    @classmethod
    def increase_ctag(cls, ctag):
        return str(int(ctag) + 1)

    def vcard2values(self, vcard):
        '''
        Convert vcard to values for create or write
        '''
        Address = Pool().get('party.address')

        res = {}
        res['name'] = vcard.fn.value
        if not hasattr(vcard, 'n'):
            vcard.add('n')
            vcard.n.value = vobject.vcard.Name(vcard.fn.value)
        res['vcard'] = vcard.serialize()
        if not self.id:
            if hasattr(vcard, 'uid'):
                res['uuid'] = vcard.uid.value
            res['addresses'] = []
            to_create = []
            for adr in vcard.contents.get('adr', []):
                vals = Address.vcard2values(adr)
                to_create.append(vals)
            if to_create:
                res['addresses'].append(('create', to_create))
            res['contact_mechanisms'] = []
            to_create = []
            for email in vcard.contents.get('email', []):
                vals = {}
                vals['type'] = 'email'
                vals['value'] = email.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))
            to_create = []
            for tel in vcard.contents.get('tel', []):
                vals = {}
                vals['type'] = 'phone'
                if hasattr(tel, 'type_param') \
                        and 'cell' in tel.type_param.lower():
                    vals['type'] = 'mobile'
                vals['value'] = tel.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))
        else:
            i = 0
            res['addresses'] = []
            addresses_todelete = []
            for address in self.addresses:
                try:
                    adr = vcard.contents.get('adr', [])[i]
                except IndexError:
                    addresses_todelete.append(address.id)
                    i += 1
                    continue
                if not hasattr(adr, 'value'):
                    addresses_todelete.append(address.id)
                    i += 1
                    continue
                vals = Address.vcard2values(adr)
                res['addresses'].append(('write', [address.id], vals))
                i += 1
            if addresses_todelete:
                res['addresses'].append(('delete', addresses_todelete))
            try:
                new_addresses = vcard.contents.get('adr', [])[i:]
            except IndexError:
                new_addresses = []
            to_create = []
            for adr in new_addresses:
                if not hasattr(adr, 'value'):
                    continue
                vals = Address.vcard2values(adr)
                to_create.append(vals)
            if to_create:
                res['addresses'].append(('create', to_create))

            i = 0
            res['contact_mechanisms'] = []
            contact_mechanisms_todelete = []
            for cm in self.contact_mechanisms:
                if cm.type != 'email':
                    continue
                try:
                    email = vcard.contents.get('email', [])[i]
                except IndexError:
                    contact_mechanisms_todelete.append(cm.id)
                    i += 1
                    continue
                vals = {}
                vals['value'] = email.value
                res['contact_mechanisms'].append(('write', [cm.id], vals))
                i += 1
            try:
                new_emails = vcard.contents.get('email', [])[i:]
            except IndexError:
                new_emails = []
            to_create = []
            for email in new_emails:
                if not hasattr(email, 'value'):
                    continue
                vals = {}
                vals['type'] = 'email'
                vals['value'] = email.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))

            i = 0
            for cm in self.contact_mechanisms:
                if cm.type not in ('phone', 'mobile'):
                    continue
                try:
                    tel = vcard.contents.get('tel', [])[i]
                except IndexError:
                    contact_mechanisms_todelete.append(cm.id)
                    i += 1
                    continue
                vals = {}
                vals['value'] = tel.value
                res['contact_mechanisms'].append(('write', [cm.id], vals))
                i += 1
            try:
                new_tels = vcard.contents.get('tel', [])[i:]
            except IndexError:
                new_tels = []
            to_create = []
            for tel in new_tels:
                if not hasattr(tel, 'value'):
                    continue
                vals = {}
                vals['type'] = 'phone'
                if hasattr(tel, 'type_param') \
                        and 'cell' in tel.type_param.lower():
                    vals['type'] = 'mobile'
                vals['value'] = tel.value
                to_create.append(vals)
            if to_create:
                res['contact_mechanisms'].append(('create', to_create))

            if contact_mechanisms_todelete:
                res['contact_mechanisms'].append(('delete',
                    contact_mechanisms_todelete))
        return res


class ActionReport(metaclass=PoolMeta):
    __name__ = 'ir.action.report'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        new_ext = ('vcf', 'VCard file')
        if new_ext not in cls.extension.selection:
            cls.extension.selection.append(new_ext)


class VCard(Report):
    __name__ = 'party_vcard.party.vcard'

    @classmethod
    def render(cls, report, report_context):
        return ''.join(party.create_vcard().serialize()
            for party in report_context['records'])

    @classmethod
    def convert(cls, report, data):
        return 'vcf', data
