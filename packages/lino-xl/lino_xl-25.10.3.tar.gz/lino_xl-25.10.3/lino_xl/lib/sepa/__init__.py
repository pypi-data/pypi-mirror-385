# Copyright 2014-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""See :doc:`/plugins/sepa`.

.. autosummary::
   :toctree:

    utils
    fields
    roles
    fixtures.sample_ibans

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("SEPA")
    site_js_snippets = ['iban/uppercasetextfield.js']
    # needs_plugins = ['lino_xl.lib.accounting']

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sepa.Accounts')
