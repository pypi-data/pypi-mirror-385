# -*- coding: UTF-8 -*-
# Copyright 2008-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.conf import settings

from lino.api import dd, rt, _
from lino.mixins import Sequenced
from lino.mixins import Hierarchical
from lino.mixins.clonable import Clonable
from lino.utils.mldbc.mixins import BabelNamed
from lino.modlib.memo.mixins import BabelPreviewable
from lino.modlib.memo.mixins import MemoReferrable
from lino.modlib.printing.models import Printable
from lino.modlib.printing.actions import DirectPrintAction

from lino_xl.lib.vat.choicelists import VatClasses
from lino_xl.lib.storage.mixins import Storable

from .choicelists import DeliveryUnits, ProductTypes, PriceFactors
from .roles import ProductsUser, ProductsStaff


class Category(BabelNamed, BabelPreviewable, Hierarchical):

    class Meta:
        app_label = 'products'
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        abstract = dd.is_abstract_model(__name__, 'Category')

    product_type = ProductTypes.field(default='default')


dd.update_field(Category, 'body', verbose_name=_("Long description"))


class PrintBarcode(DirectPrintAction):
    action_name = 'barcode_print'
    label = _("Print barcode")
    tplname = 'product_barcode'
    build_method = 'weasy2pdf'
    select_rows = True


class ProductsTable(dd.Table):
    # common things for Products and Categories
    required_roles = dd.login_required(ProductsUser)
    abstract = True
    _product_type = None

    @classmethod
    def hide_editing(cls, user_type):
        if not user_type.has_required_roles([ProductsStaff]):
            return True
        return super().hide_editing(user_type)


class Categories(ProductsTable):
    model = 'products.Category'
    order_by = ["id"]
    column_names = "id parent name product_type *"
    detail_layout = """
    id name
    body
    ProductsByCategory
    """


class Barcodable(dd.Model):
    class Meta:
        abstract = True

    barcode_identity = dd.DummyField()
    vendor = dd.DummyField()

    if dd.plugins.products.barcode_driver is not None:
        barcode_identity = dd.PositiveIntegerField()
        vendor = dd.ForeignKey('contacts.Company', null=False,
                               blank=False, on_delete=models.PROTECT)
        print_barcode = PrintBarcode()

        def get_printable_context(self, ar):
            ctx = super().get_printable_context(ar)
            ctx.update(barcode_image=dd.plugins.products.barcode_driver.get_image_tag_as_string(
                self, module_height=3, module_width=0.1, quiet_zone=2, font_size=3.3, text_distance=2))
            return ctx

        def full_clean(self, *args, **kwargs):
            drv = dd.plugins.products.barcode_driver
            drv.write_svg_file(drv.get_barcode(self))
            super().full_clean(*args, **kwargs)

        @dd.htmlbox()
        def barcode_svg(self, ar=None):
            bcode = dd.plugins.products.barcode_driver.get_barcode(self)
            return '<img src="{}" alt="{}"/>'.format(
                settings.SITE.build_media_url('barcodes', bcode + ".svg"), bcode)


class Product(BabelNamed, BabelPreviewable, Clonable, MemoReferrable,
              Storable, Printable, Barcodable):

    class Meta:
        app_label = 'products'
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        abstract = dd.is_abstract_model(__name__, 'Product')
        # if dd.plugins.products.barcode_driver is not None and not dd.is_abstract_model(__name__, 'Product'):
        if dd.plugins.products.barcode_driver is not None:
            unique_together = [('vendor', 'barcode_identity')]

    memo_command = 'product'

    category = dd.ForeignKey('products.Category',
                             verbose_name=_("Category"),
                             blank=True,
                             null=True)
    delivery_unit = DeliveryUnits.field(default='piece')
    pieces_per_unit = dd.PositiveIntegerField(_("Pieces per unit"),
                                              blank=True,
                                              null=True)
    product_type = ProductTypes.field()
    vat_class = VatClasses.field(blank=True)
    subtotal = models.BooleanField(_("Subtotal"), default=False)

    @classmethod
    def get_simple_parameters(cls):
        for p in super().get_simple_parameters():
            yield p
        yield "category"

    @dd.chooser()
    def category_choices(self, product_type, ar=None):
        qs = rt.models.products.Categories.create_request().data_iterator
        if product_type is None and ar is not None:
            product_type = ar.actor._product_type
        if product_type is not None:
            qs = qs.filter(product_type=product_type)
        return qs

    # @classmethod
    # def get_product_choices(cls, partner):
    #     """Return a list of products that are allowed for the specified partner.
    #     """
    #     Product = cls
    #     qs = Product.objects.filter(product_type=ProductTypes.default)
    #     qs = qs.order_by('name')
    #     rules = PriceRule.objects.all()
    #     for pf in PriceFactors.get_list_items():
    #         rules = rules.filter(
    #             Q(**{pf.field_name: getattr(partner, pf.field_name)}) |
    #             Q(**{pf.field_name + '__isnull': True}))
    #     return [p for p in qs if rules.filter(product=p).count() > 0]
    #     # TODO: add rules condition as subquery to qs and return the query, not
    #     # the list

    # subtotal_marker_template = "∑ {}"
    subtotal_marker_template = "== {} =="

    def __str__(self):
        s = super().__str__()
        if self.subtotal:
            return self.subtotal_marker_template.format(s)
        return s

    @classmethod
    def get_ruled_price(cls, partner, selector):
        if partner is None:
            return
        for rule in rt.models.products.PriceRule.objects.order_by('seqno'):
            ok = True
            for pf in PriceFactors.get_list_items():
                rv = getattr(rule, pf.field_name)
                if rv:
                    pv = getattr(partner, pf.field_name)
                    if pv != rv:
                        # print("20181128a {} != {}".format(rv, pv))
                        ok = False
            if rule.selector and rule.selector != selector:
                # print("20181128c {} != {}".format(rule.event_type, event_type))
                ok = False

            if ok and rule.product is not None:
                return rule.product

    def full_clean(self):
        # print("20191210", self.name, self.vat_class)
        if self.product_type is None:
            if self.category_id:
                self.product_type = self.category.product_type or ProductTypes.default
            else:
                self.product_type = ProductTypes.default
        super().full_clean()


dd.update_field(Product, 'body', verbose_name=_("Long description"))


class ProductDetail(dd.DetailLayout):

    main = """
    id category #sales_price vat_class delivery_unit
    name
    body
    """


class BaseProducts(ProductsTable):
    abstract = True
    model = 'products.Product'
    order_by = ["name"]
    column_names = "id name category vat_class *"

    detail_layout = "products.ProductDetail"

    insert_layout = """
    category
    name
    """

    card_layout = """name category
    body_short_preview
    workflow_buttons
    """

    # list_layout = """name category workflow_buttons"""


class Products(BaseProducts):

    @classmethod
    def get_actor_label(cls):
        pt = cls._product_type or ProductTypes.default
        return pt.text

    @classmethod
    def create_instance(cls, ar, **kwargs):
        kwargs.update(product_type=cls._product_type or ProductTypes.default)
        return super().create_instance(ar, **kwargs)

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        qs = super().get_request_queryset(ar)
        qs = qs.filter(product_type=cls._product_type or ProductTypes.default)
        return qs


class ProductsByCategory(BaseProducts):
    master_key = 'category'


class PriceRule(Sequenced):

    class Meta(object):
        app_label = 'products'
        abstract = dd.is_abstract_model(__name__, 'PriceRule')
        verbose_name = _("Price rule")
        verbose_name_plural = _("Price rules")

    # allow_cascaded_delete = ["selector"]
    selector = dd.ForeignKey(dd.plugins.products.price_selector,
                             blank=True,
                             null=True)
    product = dd.ForeignKey('products.Product', blank=True, null=True)


class PriceRules(dd.Table):
    model = "products.PriceRule"
    column_names_tpl = "seqno {factors} selector product *"
    order_by = ['seqno']

    @classmethod
    def get_column_names(cls, ar):
        factors = ' '.join(
            [pf.field_name for pf in PriceFactors.get_list_items()])
        return cls.column_names_tpl.format(factors=factors)


@dd.receiver(dd.pre_analyze)
def inject_pricefactor_fields(sender, **kw):
    for pf in PriceFactors.get_list_items():
        dd.inject_field('products.PriceRule', pf.field_name,
                        PriceFactors.get_field(pf))
        dd.inject_field('contacts.Partner', pf.field_name,
                        PriceFactors.get_field(pf))


# @dd.receiver(dd.post_startup)
# def setup_memo_commands(sender=None, **kwargs):
#     # See :doc:`/specs/memo`
#
#     if not sender.is_installed('memo'):
#         return
#
#     Product = sender.models.products.Product
#     mp = sender.plugins.memo.parser
#
#     mp.register_django_model(
#         'product', Product, title=lambda obj: str(obj.name))
