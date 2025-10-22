# -*- coding: UTF-8 -*-
# Copyright 2008-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import os
from datetime import timedelta
from email.utils import parseaddr

from lino.utils.html import E, join_elems, forcetext, tostring, escape
from django.utils.html import mark_safe, format_html
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Right

from lino import mixins
from lino.api import dd, rt, _
from lino.core import constants
from lino.mixins.clonable import Clonable
from lino.mixins.human import name2kw, Human, parse_name
from lino.mixins.human import Born
# from lino_xl.lib.cal.mixins import BirthdayGenerator
from lino.mixins.polymorphic import Polymorphic
# from lino.mixins.periods import ObservedDateRange
from lino.mixins.periods import DateRangeObservable
from lino.modlib.publisher.mixins import Publishable
from lino.modlib.uploads.mixins import UploadController
# from lino.modlib.memo.mixins import MemoReferrable
from lino.modlib.comments.mixins import Commentable
from lino.utils import join_words
from lino.utils.addressable import Addressable
from lino.utils.media import TmpMediaFile
from lino_xl.lib.addresses.mixins import AddressOwner
from lino_xl.lib.phones.mixins import ContactDetailsOwner
from lino_xl.lib.skills.mixins import Feasible
from lino_xl.lib.trading.mixins import TradingPartner
from lino_xl.lib.peppol.mixins import PeppolPartner
from lino_xl.lib.vat.choicelists import VatSubjectable

from .mixins import ContactRelated
from .choicelists import CivilStates
from .choicelists import PartnerEvents
from .roles import SimpleContactsUser, ContactsStaff, ContactsUser
from .utils import PARTNER_NUMBERS_START_AT

if dd.plugins.contacts.use_vcard_export:
    from lino.modlib.uploads.mixins import UploadBase
    from lino_xl.lib.countries.wikidata import get_countries
    try:
        import vobject
    except ImportError:
        # silently ignore it because we don't want `inv install` to fail.
        # raise Exception(
        #     "use_vcard_export is True but vobject is not installed")
        vobject = None

    class UploadVCardFile(UploadBase):

        class Meta(object):
            app_label = 'contacts'
            verbose_name = _("vCard File")
            verbose_name_plural = _("vCard Files")

        description = dd.CharField(max_length=10,
                                   blank=True,
                                   verbose_name=_('Description'))

        def save_newly_uploaded_file(self, uf):
            if not str(uf).endswith('.vcf'):
                raise ValidationError(_("Invalid File Type"))
            countries = get_countries()
            Country = rt.models.countries.Country
            Place = rt.models.countries.Place
            Person = rt.models.contacts.Person
            for vo in vobject.readComponents(uf.read().decode()):
                if not hasattr(vo, 'n'):
                    continue
                p = Person()
                p.first_name = vo.n.value.given
                p.middle_name = vo.n.value.additional
                p.last_name = vo.n.value.family
                if hasattr(vo, 'email'):
                    p.email = vo.email.value
                    emails = []
                    for e in vo.contents['email']:
                        emails.append(e.value)
                if hasattr(vo, 'tel'):
                    p.phone = vo.tel.value
                    tels = []
                    for t in vo.contents['tel']:
                        tels.append(t.value)
                if hasattr(vo, 'adr'):
                    p.street_box = vo.adr.value.box
                    p.zip_code = vo.adr.value.code
                    country = vo.adr.value.country
                    kw = dict()
                    if country != "":
                        iso = country.lower()
                        country, created = Country.objects.get_or_create(
                            isocode=country)
                        if created:
                            country.name = countries['data'][iso]['name']
                            country.full_clean()
                            country.save()
                        kw.update(country=country)
                    p.country = country
                    city = vo.adr.value.city
                    if city != "":
                        city, created = Place.objects.get_or_create(name=city,
                                                                    **kw)
                        if created:
                            city.full_clean()
                            city.save()
                    p.city = city
                    region = vo.adr.value.region
                    if region != "":
                        region, created = Place.objects.get_or_create(
                            name=region, **kw)
                        if created:
                            region.full_clean()
                            region.save()
                    p.street = vo.adr.value.street
                    p.addr2 = vo.adr.value.extended  # Address Line 2
                if hasattr(vo, 'bday'):
                    bday = vo.bday.value
                    year = bday[:4]
                    month = bday[4:6]
                    day = bday[6:]
                    p.birth_date = '.'.join([day, month, year])
                if hasattr(vo, 'org'):
                    org = vo.org.value
                    org_name = org[0]
                    if len(org) > 1:
                        designation = org[1]
                    if hasattr(vo, 'title'):
                        title = vo.title.value
                if hasattr(vo, 'url'):
                    url = vo.url.value
                    if not url.startswith('http'):
                        url = 'https://' + url
                    p.url = url
                p.full_clean()
                p.save()

        def save(self, *args, **kwargs):
            """
            We don't want to save any object instance of this model. We mimic
            the behaviour of saving just by settings the primary key to some
            value."""
            self.pk = 0

    class UploadVCardFiles(dd.Table):
        required_roles = dd.login_required(SimpleContactsUser)
        model = 'contacts.UploadVCardFile'
        insert_layout = """
        file
        description
        """


with_roles_history = dd.plugins.contacts.with_roles_history


class ExportVCardFile(dd.Action):
    label = _("Export as vCard")
    icon_name = 'vcard'
    sort_index = -9
    default_format = 'ajax'
    show_in_toolbar = True

    def run_from_ui(self, ar, **kw):
        # ~ print 20130912
        # ~ obj = ar.selected_rows[0]
        mf = TmpMediaFile(ar, 'vcf')
        settings.SITE.makedirs_if_missing(os.path.dirname(mf.name))
        with open(mf.name, 'w') as wf:
            for obj in ar.selected_rows:
                j = vobject.vCard()
                obj.fill_vcard(j)
                wf.write(j.serialize())

        ar.set_response(success=True)
        ar.set_response(open_url=mf.get_url(ar.request))


class ImportText(dd.Action):
    """
    Example values for text:

    Albert Adam <albert@example.com>

    """
    label = _("Import from text")
    sort_index = -10
    select_rows = False
    http_method = 'POST'
    show_in_toolbar = True

    parameters = dict(text=dd.RichTextField(_("One line per contact"),
                                            format='plain'),
                      confirm_changes=models.BooleanField(
                          _("Confirm every change"), default=True))
    params_layout = dd.ActionParamsLayout("""
    text
    confirm_changes
    """,
                                          window_size=(60, 15))

    def run_from_ui(self, ar, **kw):
        pv = ar.action_param_values
        changes = []
        for ln in pv.text.splitlines():
            print(ln)
            name, addr = parseaddr(ln)
            kw = name2kw(name, last_name_first=False)
            values_to_update = dict()
            qs = rt.models.contacts.Person.objects.filter(**kw)
            count = qs.count()
            object_to_update = None
            if count == 1:
                object_to_update = qs.first()
                values_to_update.update(email=addr)
            elif count == 0:
                print(qs.query)
                qs = rt.models.contacts.Partner.objects.filter(
                    name__icontains=name)
                if qs.count() == 1:
                    object_to_update = qs.first()
                    values_to_update.update(email=addr)
            if object_to_update:
                # if pv.confirm_changes...
                for k, v in values_to_update.items():
                    setattr(object_to_update, k, v)
                object_to_update.full_clean()
                object_to_update.save()

            changes.append(("{} <{}> --> {}".format(name, addr, qs)))
        print(changes)
        ar.set_response(success='\n'.join(changes), alert=True)


class Partner(Clonable, ContactDetailsOwner, Polymorphic, AddressOwner,
              UploadController, Feasible, Publishable, DateRangeObservable,
              VatSubjectable, Commentable, PeppolPartner, TradingPartner):

    preferred_foreignkey_width = 20

    # preferred width for ForeignKey fields to a Partner

    class Meta:
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'Partner')
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")

    if dd.plugins.contacts.use_vcard_export:
        export_vcf = ExportVCardFile()
        import_text = ImportText()

    prefix = models.CharField(_("Name prefix"), max_length=200, blank=True)
    name = models.CharField(_('Name'), max_length=200)
    remarks = models.TextField(_("Remarks"), blank=True)  # ,null=True)
    if dd.plugins.contacts.with_partner_ref:
        partner_ref = models.CharField(
                _("Partner ref"), max_length=200, blank=True)
    else:
        partner_ref = dd.DummyField()

    quick_search_fields = "prefix name phone gsm"

    # print_labels = dd.PrintLabelsAction()

    allow_merge_action = True

    # @classmethod
    # def get_request_queryset(cls, ar, **filter):
    #     qs = super().get_request_queryset(ar, **filter)
    #     return qs.select_related('country', 'city')

    def on_create(self, ar):
        self.language = ar.get_user().language
        if not self.country:
            if (sc := settings.SITE.plugins.contacts.site_owner):
                self.country = sc.country
        super().on_create(ar)

    # 20250411 : the next_partner_id field is no longer being used.
    # def save(self, *args, **kw):
    #     if self.id is None:
    #         sc = settings.SITE.site_config
    #         if sc.next_partner_id is not None:
    #             try:
    #                 rt.models.contacts.Partner.objects.get(
    #                     id=sc.next_partner_id)
    #                 raise ValidationError(
    #                     "Cannot create partner with id={0}. "
    #                     "Check your next_partner_id in SiteConfig!".format(
    #                         sc.next_partner_id))
    #             except rt.models.contacts.Partner.DoesNotExist:
    #                 self.id = sc.next_partner_id
    #                 sc.next_partner_id += 1
    #                 sc.save()
    #     super(Partner, self).save(*args, **kw)

    def get_last_name_prefix(self):
        # overrides lino.mixins.humans.Human
        return self.prefix

    def __str__(self):
        # ~ return self.name
        return self.get_full_name()

    def address_person_lines(self):
        # ~ yield self.name
        yield self.get_full_name()

    def get_full_name(self, *args, **kwargs):
        """Return a one-line string representing this Partner.  The default
        returns simply the `name`, optionally prefixed by the
        :attr:`prefix`, ignoring any arguments, but
        e.g. :class:`Human` overrides this.

        """
        return join_words(self.prefix, self.name)

    full_name = property(get_full_name)

    def get_partner_instance(self):
        return self  # compatibility with lino.modlib.partners

    def get_overview_elems(self, ar):
        elems = []
        buttons = self.get_mti_buttons(ar)
        if len(buttons) > 1:
            # buttons = join_elems(buttons, ', ')
            elems.append(
                E.p(str(_("See as ")),
                    *buttons,
                    style="font-size:8px;text-align:right;padding:3pt;"))
        elems += self.get_name_elems(ar, sep=E.br)
        elems.append(E.br())
        elems += join_elems(list(self.address_location_lines()), sep=E.br)
        elems = [
            E.div(*forcetext(elems),
                  style="font-size:18px;font-weigth:bold;"
                  "vertical-align:bottom;text-align:middle")
        ]
        elems += AddressOwner.get_overview_elems(self, ar)
        elems += ContactDetailsOwner.get_overview_elems(self, ar)
        return elems

    def as_paragraph(self, ar, **kwargs):
        if ar is None:
            s = str(self)
        else:
            s = ar.obj2htmls(self)
        lst = list(self.address_location_lines())
        if len(lst) > 0:
            s = format_html("{} ({})", s, ", ".join(lst))
            # s += " (" + ", ".join(lst) + ")"
        return s

    def get_name_elems(self, ar, sep=E.br):
        elems = []
        if self.prefix:
            elems += [self.prefix, ' ']
        elems.append(E.b(self.name))
        return elems

    def get_print_language(self):
        return self.language

    @classmethod
    def setup_parameters(cls, fields):
        fields.setdefault(
            'observed_event',
            PartnerEvents.field(blank=True,
                                help_text=_("Extended filter criteria")))
        super(Partner, cls).setup_parameters(fields)

    @classmethod
    def get_request_queryset(self, ar, **filter):
        qs = super(Partner, self).get_request_queryset(ar, **filter)

        if (pv := ar.param_values) is None:
            return qs
        oe = pv.observed_event
        if oe:
            qs = oe.add_filter(qs, pv)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Partner, self).get_title_tags(ar):
            yield t
        pv = ar.param_values

        if pv.observed_event:
            yield str(pv.observed_event)

    def as_page(self, ar, display_mode="detail", **kwargs):
        title = dd.babelattr(self, "title")
        yield "<p class=\"display-4\">{}</p>".format(escape(title))

        # elems = []
        elems = list(self.get_name_elems(ar, sep=E.br))
        elems.append(E.br())
        elems += join_elems(list(self.address_location_lines()), sep=E.br)
        # elems = [
        #     E.div(*forcetext(elems),
        #           style="font-size:18px;font-weigth:bold;"
        #           "vertical-align:bottom;text-align:middle")
        # ]
        elems += AddressOwner.get_overview_elems(self, ar)
        elems += ContactDetailsOwner.get_overview_elems(self, ar)
        for e in elems:
            yield tostring(e)

    def get_as_user(self):
        """Return the user object that corresponds to this partner.

        If the application's User model inherits from Partner, then


        """
        User = rt.models.users.User
        try:
            if issubclass(User, self.__class__):
                return User.objects.get(partner_ptr=self)
            else:
                return User.objects.get(partner=self)
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            pass

    def fill_vcard(self, j):
        j.add('n')
        j.n.value = vobject.vcard.Name(family=self.name)
        j.add('fn')
        j.fn.value = self.name
        if self.city:
            j.add('adr')
            j.adr.street = self.street
            j.adr.box = (self.street_no + " " + self.street_box).strip()
            j.adr.city = str(self.city)
            j.adr.region = str(self.region)
            j.adr.country = str(self.country)
            j.adr.code = self.zip_code
        if self.email:
            j.add('email')
            j.email.value = self.email
            j.email.type_param = 'INTERNET'
        if self.phone:
            j.add('tel')
            j.tel.value = self.phone
            j.tel.type_param = 'HOME'
        if self.gsm:
            j.add('tel')
            j.tel.value = self.gsm
            j.tel.type_param = 'CELL'
        if self.url:
            j.add('url')
            j.url.value = self.url


class PartnerDetail(dd.DetailLayout):

    main = "general contact trading subscriptions storage tickets accounting sepa"

    general = dd.Panel("""
    overview info_box
    bottom_box
    """, label=_("General"))

    bottom_box = """
    bottom_left bottom_right
    """

    if dd.is_installed('assets'):
        bottom_left = """
        remarks assets.AssetsByPartner
        """
    else:
        bottom_left = """
        remarks
        """

    bottom_right = ""

    name_box = "name"
    info_box = """id:6
    vat_id
    vat_regime
    peppol_id
    send_peppol
    """

    contact = dd.Panel("""
    contact1 contact2
    """, label=_("Contact"))

    if dd.is_installed('addresses'):
        contact1 = dd.Panel("""
        addresses.AddressesByPartner
        """)
        contact2 = dd.Panel("""
        language
        email
        url
        """)
    else:
        contact1 = dd.Panel("""
        name_box
        country region city zip_code:10
        addr1
        #street_prefix street:25 street_no street_box
        addr2
        """)
        contact2 = dd.Panel("""
        language
        email
        url
        phone
        gsm fax
        """)

    if dd.is_installed('invoicing'):
        trading = dd.Panel("""
        trading.RulesByPartner
        trading.InvoicesByPartner
        """, label=dd.plugins.trading.verbose_name)
    elif dd.is_installed('trading'):
        trading = dd.Panel("""
        vat_id vat_regime send_peppol
        trading.InvoicesByPartner
        """, label=dd.plugins.trading.verbose_name)
    else:
        trading = dd.DummyPanel()

    if dd.is_installed('storage'):
        storage = dd.Panel("""
        storage.FillersByPartner storage.ProvisionsByPartner storage.MovementsByPartner
        """, label=dd.plugins.storage.verbose_name)
    else:
        storage = dd.DummyPanel()

    if dd.is_installed('subscriptions'):
        subscriptions = dd.Panel("""
        subscriptions.SubscriptionsByPartner
        """, label=dd.plugins.subscriptions.verbose_name)
    else:
        subscriptions = dd.DummyPanel()

    if dd.is_installed('tickets'):
        tickets = dd.Panel("""
        tickets.TicketsByEndUser
        """, label=dd.plugins.tickets.verbose_name)
    else:
        tickets = dd.DummyPanel()

    if dd.is_installed('vatless'):
        accounting = dd.Panel("""
        vatless.VouchersByPartner
        accounting.MovementsByPartner
        """, label=dd.plugins.accounting.verbose_name)
    elif dd.is_installed('vat'):
        accounting = dd.Panel("""
        partner_ref purchase_account
        vat.VouchersByPartner
        accounting.MovementsByPartner
        """, label=dd.plugins.accounting.verbose_name)
    else:
        accounting = dd.DummyPanel()

    if dd.is_installed('sepa'):
        sepa = dd.Panel("""
        payment_reminders
        sepa.AccountsByPartner
        """, label=_("Payments"))
    else:
        sepa = dd.DummyPanel()

    # more = dd.Panel("""
    # remarks
    # """, label=_("More"))


class Partners(dd.Table):
    required_roles = dd.login_required(SimpleContactsUser)
    model = 'contacts.Partner'
    column_names = "name id mti_navigator email * "
    default_display_modes = {
        30: constants.DISPLAY_MODE_SUMMARY,
        70: constants.DISPLAY_MODE_LIST,
        None: constants.DISPLAY_MODE_GRID}
    order_by = ['name', 'id']
    card_layout = """
    id name
    overview
    """

    # parameters = ObservedDateRange()
    # detail_layout = 'contacts.PartnerDetail'
    # removed for #2777 ()
    # insert_layout = """
    # name
    # #language email
    # """

    @classmethod
    def get_request_queryset(self, ar):
        qs = super().get_request_queryset(ar)
        return qs.select_related('country', 'city')
        # return self.model.objects.select_related('country', 'city')


# ~ class AllPartners(Partners):

# ~ @classmethod
# ~ def get_actor_label(self):
# ~ return _("All %s") % self.model._meta.verbose_name_plural


class PartnersByCity(Partners):
    master_key = 'city'
    order_by = 'street street_no street_box addr2'.split()
    column_names = "address_column #street #street_no #street_box #addr2 name *"


class PartnersByCountry(Partners):
    master_key = 'country'
    column_names = "city street street_no name language *"
    order_by = "city street street_no".split()


class Person(Human, Born, Partner):

    class Meta(object):
        app_label = 'contacts'
        abstract = dd.is_abstract_model(__name__, 'Person')
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        ordering = ['last_name', 'first_name']

    memo_command = 'person'

    def get_after_salutation_words(self):
        if self.prefix:
            yield self.prefix

    def full_clean(self, *args, **kw):
        """Set the `name` field of this person.  This field is visible in the
        Partner's detail but not in the Person's detail and serves for
        sorting when selecting a Partner.  It also serves for quick
        search on Persons.

        """
        name = join_words(self.last_name, self.first_name)
        if name:
            self.name = name
        else:
            for k, v in list(name2kw(self.name).items()):
                setattr(self, k, v)
            # self.last_name = self.name
        super(Person, self).full_clean(*args, **kw)

    def address_person_lines(self, *args, **kw):
        "Deserves more documentation."
        # if self.title:
        #     yield join_words(self.get_salutation(), self.title)
        #     kw.update(salutation=False)
        yield self.get_full_name(*args, **kw)

    def get_name_elems(self, ar, sep=E.br):
        elems = [self.get_salutation(nominative=True), ' ', self.prefix, sep()]
        elems += [self.first_name, ' ', E.b(self.last_name)]
        return elems

    def fill_vcard(self, j):
        super(Person, self).fill_vcard(j)
        j.n.value = vobject.vcard.Name(family=self.last_name,
                                       given=self.first_name)

    @classmethod
    def choice_text_to_dict(cls, text, ar):
        return parse_name(text)
        # try:
        #     kw = parse_name(text)
        # except Exception as e:
        #     return None
        #     # raise ValidationError(
        #     #     _("Could not create {person} from '{text}'").format(
        #     #     person=cls._meta.verbose_name, text=text))
        # if len(kw) != 2:
        #     raise ValidationError(
        #         "Cannot find first and last names in %r", text)
        # return kw


class PersonDetail(PartnerDetail):

    name_box = "last_name first_name:15 gender #prefix:10"
    info_box = "id"
    bottom_right = "contacts.RolesByPerson"


class Persons(Partners):
    required_roles = dd.login_required(SimpleContactsUser)
    model = "contacts.Person"
    order_by = ["last_name", "first_name", "id"]
    column_names = ("name_column:20 address_column email "
                    "phone:10 gsm:10 id language:10 *")
    detail_layout = 'contacts.PersonDetail'

    insert_layout = """
    first_name last_name
    gender email #language
    """
    card_layout = """
    id first_name last_name
    overview
    """

    @classmethod
    def collect_extra_actions(cls):
        if dd.plugins.contacts.use_vcard_export:
            yield dd.WrappedAction(
                UploadVCardFiles.insert_action,
                help_text=_("Import contacts from vCard File."),
                label=_("Import from VCard"),
                icon_name=None,
                select_rows=False,
                callable_from='dt',
                sort_index=-8)
        else:
            return []


class CompanyType(mixins.BabelNamed):

    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'CompanyType')
        # verbose_name = _("Organization type")
        # verbose_name_plural = _("Organization types")
        verbose_name = _("Legal form")
        verbose_name_plural = _("Legal forms")

    abbr = dd.BabelCharField(_("Abbreviation"), max_length=30, blank=True)


class CompanyTypes(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'contacts.CompanyType'
    column_names = 'name *'
    # ~ label = _("Company types")


class Company(Partner):

    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'Company')
        app_label = 'contacts'
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    memo_command = 'company'

    type = dd.ForeignKey('contacts.CompanyType', blank=True, null=True)

    barcode_identity = dd.DummyField()
    if dd.is_installed('products') and dd.plugins.products.barcode_driver is not None:
        barcode_identity = dd.PositiveIntegerField(
            null=True, blank=True, unique=True)

    @classmethod
    def choice_text_to_dict(cls, text, ar):
        return dict(name=text)

    def get_full_name(self, salutation=True, **salutation_options):
        # ~ print '20120729 Company.get_full_name`'
        if self.type:
            return join_words(self.prefix, self.type.abbr, self.name)
        return join_words(self.prefix, self.name)

    full_name = property(get_full_name)

    def get_signers(self, today=None):
        if today is None:
            today = dd.today()
        qs = rt.models.contacts.Role.objects.filter(
            company=self).order_by('type')
        qs = qs.filter(type__can_sign=True)
        if with_roles_history:
            qs = qs.filter(Q(start_date__isnull) | Q(start_date__lte=today))
            qs = qs.filter(Q(end_date__isnull) | Q(end_date__gte=today))
        return qs


class CompanyDetail(PartnerDetail):

    bottom_right = "contacts.RolesByCompany"

    name_box = "prefix:10 name:40"

    info_box = """
    id type
    vat_id
    vat_regime
    peppol_id
    send_peppol
    """


class Companies(Partners):
    required_roles = dd.login_required(SimpleContactsUser)
    model = "contacts.Company"
    order_by = ["name"]
    column_names = ("name_column:20 address_column email "
                    "phone:10 gsm:10 id language:10 *")
    detail_layout = 'contacts.CompanyDetail'
    insert_layout = """
    name
    #language:20 email:40
    type #id
    """


class RoleType(mixins.BabelNamed):

    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'RoleType')
        verbose_name = _("Function")
        verbose_name_plural = _("Functions")

    can_sign = models.BooleanField(_("Authorized to sign"), default=False)


class RoleTypes(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'contacts.RoleType'


class Role(dd.Model, Addressable):

    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'Role')
        verbose_name = _("Contact person")
        verbose_name_plural = _("Contact persons")

    type = dd.ForeignKey('contacts.RoleType', blank=True, null=True)
    person = dd.ForeignKey("contacts.Person",
                           related_name='rolesbyperson',
                           blank=True,
                           null=True)
    company = dd.ForeignKey("contacts.Company",
                            related_name='rolesbycompany',
                            blank=True,
                            null=True)
    # blank and null are set to True because otherwise learning doesn't work...

    if with_roles_history:
        start_date = models.DateField(verbose_name=_("Start date"),
                                      blank=True,
                                      null=True)
        end_date = models.DateField(verbose_name=_("End date"),
                                    blank=True,
                                    null=True)
    else:
        start_date = dd.DummyField()
        end_date = dd.DummyField()

    def __str__(self):
        # if self.person_id is None:
        #     return super().__str__()
        # if self.type is None:
        #     return str(self.person)
        return _("{person} is {role} at {company}").format(
            person=self.person, role=self.type, company=self.company)

    def as_summary_item(self, ar, text=None, **kwargs):
        # raise Exception("20240613")
        if ar is None:
            obj = super()
        elif ar.is_obvious_field('person'):
            obj = self.company
        elif ar.is_obvious_field('company'):
            obj = self.person
        else:
            obj = super()
        if self.type is None:
            text = str(obj)
        else:
            text = "{} ({})".format(obj, self.type)
        return obj.as_summary_item(ar, text, **kwargs)

    # def as_paragraph(self, ar):
    #     if ar.is_obvious_field('person'):
    #         txt = ar.obj2htmls(self.company)
    #     elif ar.is_obvious_field('company'):
    #         txt = ar.obj2htmls(self.person)
    #     else:
    #         txt = format_html("{}, {}", ar.obj2htmls(self.person),
    #                               ar.obj2htmls(self.company))
    #     if self.type is not None:
    #         # txt = "{} ({})".format(txt, ar.obj2htmls(self, str(self.type)))
    #         txt = format_html("{} ({})", txt, self.type)
    #     return txt

    def address_person_lines(self):
        if self.company:
            for ln in self.company.address_person_lines():
                yield ln
        for ln in self.person.address_person_lines():
            yield ln

    def address_location_lines(self):
        if self.company_id:
            return self.company.address_location_lines()
        if self.person_id:
            return self.person.address_location_lines()
        return super(Role, self).__str__()

    def get_print_language(self):
        if self.company_id:
            return self.company.language
        if self.person_id:
            return self.person.language
        return super(Role, self).get_print_language()

    @dd.chooser()
    def person_choices(cls):
        # needed to activate create_person_choice
        return rt.models.contacts.Person.objects.all()

    def create_person_choice(self, *args, **kwargs):
        return rt.models.contacts.Person.create_from_choice(*args, **kwargs)

    def create_company_choice(self, *args, **kwargs):
        # print("20231227")
        return rt.models.contacts.Company.create_from_choice(*args, **kwargs)


class Roles(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'contacts.Role'


class RolesByCompany(Roles):
    required_roles = dd.login_required(SimpleContactsUser)
    auto_fit_column_widths = True
    label = _("Contact persons")
    master_key = 'company'
    column_names = 'person type start_date end_date *'
    # hidden_columns = 'id'
    insert_layout = """
    person type
    start_date end_date
    """
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}


class RolesByPerson(Roles):
    """Shows all roles of a person."""
    required_roles = dd.login_required(SimpleContactsUser)
    # ~ required_user_level = None
    label = _("Contact for")
    master_key = 'person'
    column_names = 'company type start_date end_date *'
    insert_layout = """
    type company
    start_date end_date
    """
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}
    auto_fit_column_widths = True
    hidden_columns = 'id'
    details_of_master_template = _("%(master)s is contact person for")


# dd.inject_field(
#     'system.SiteConfig', 'next_partner_id',
#     models.IntegerField(
#         default=PARTNER_NUMBERS_START_AT,
#         blank=True,
#         null=True,
#         verbose_name=_("Next partner id"),
#         help_text=_("The next automatic id for any new partner.")))


@dd.receiver(dd.pre_analyze)
def company_model_alias(sender, **kw):
    """
    prepare ticket #72 which will rename Company to Organisation
    """
    sender.modules.contacts.Organisation = sender.modules.contacts.Company


@dd.receiver(dd.post_analyze)
def company_tables_alias(sender, **kw):
    """
    prepare ticket #72 which will rename Company to Organisation
    """
    sender.modules.contacts.Organisations = sender.modules.contacts.Companies


def PartnerField(**kw):
    return dd.ForeignKey(Partner, **kw)


def show_birthdays(ar, today=None):
    if not ar.get_user().user_type.has_required_roles([ContactsUser]):
        return
    if today is None:
        today = dd.today()
    qs = rt.models.contacts.Person.objects.exclude(birth_date='')
    qs = qs.annotate(bday=Right("birth_date", 5)).exclude(
        bday="00-00").order_by('bday')
    recent_bdays = [str(today - timedelta(days=x + 1))[-5:] for x in range(3)]
    coming_bdays = [str(today + timedelta(days=x + 1))[-5:] for x in range(3)]

    recent = qs.filter(bday__in=recent_bdays)
    coming = qs.filter(bday__in=coming_bdays)
    todayqs = qs.filter(bday=str(today)[-5:])

    def fmt(obj, day=True):
        if day:
            s1 = str(obj.birth_date)[-5:] + " "
        else:
            s1 = ""
        if obj.birth_date.year:
            s2 = " ({})".format(today.year - obj.birth_date.year)
        else:
            s2 = ""
        return format_html("{}{}{}",
                           s1, ar.obj2htmls(obj, obj.get_full_name(salutation=False)), s2)

    if todayqs.count():
        yield format_html(
            "<p><b>{}</b>: {}</p>", _("Birthdays today"),
            mark_safe(", ".join([fmt(obj, day=False) for obj in todayqs])))
    if recent.count():
        yield format_html(
            "<p>{}: {}</p>", _("Recent birthdays"),
            mark_safe(", ".join([fmt(obj) for obj in recent])))
    if coming.count():
        yield format_html(
            "<p>{}: {}</p>", _("Upcoming birthdays"),
            mark_safe(", ".join([fmt(obj) for obj in coming])))


if dd.get_plugin_setting('contacts', 'show_birthdays', False):
    dd.add_welcome_handler(show_birthdays)
