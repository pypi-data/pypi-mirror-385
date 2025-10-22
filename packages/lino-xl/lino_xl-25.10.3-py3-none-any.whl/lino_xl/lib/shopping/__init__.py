# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# https://dev.lino-framework.org/plugins/shopping.html

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Shopping")
    needs_plugins = ['lino_xl.lib.contacts', 'lino_xl.lib.trading']
    menu_group = "trading"

    journal_ref = "SLS"
    """The reference of the journal where shopping invoices will be created."""

    def get_quicklinks(self):
        yield 'shopping.MyCart.start_plan'

    def setup_main_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('shopping.MyAddresses')
        m.add_action('shopping.MyCart.start_plan')

    def setup_config_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('shopping.DeliveryMethods')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('shopping.AllCarts')
        m.add_action('shopping.AllAddresses')
