# -*- coding: UTF-8 -*-
# Copyright 2013-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Adds blogging functionality. See :doc:`/plugins/blogs`.
"""

from lino.ad import Plugin, _


class Plugin(Plugin):

    verbose_name = _("Blog")

    menu_group = "publisher"
    needs_plugins = [
        'lino.modlib.publisher',
        'lino_xl.lib.topics', 'lino_xl.lib.albums', 'lino_xl.lib.sources'
    ]

    def setup_main_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        # mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.MyEntries')

    def setup_config_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.EntryTypes')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.AllEntries')
        # m.add_action('blogs.AllTaggings')

    def setup_quicklinks(self, tb):
        tb.add_action("blogs.MyEntries.insert", label=_("New blog entry"))

    def get_dashboard_items(self, user):
        yield self.site.models.blogs.LatestEntries
        # yield self.site.models.blogs.PublicEntries
        # from lino.core.dashboard import ActorItem
        # yield ActorItem(
        #     self.site.models.blogs.LatestEntries, display_mode="list")

    # def get_dashboard_items(self, user):
    #     from lino.core.dashboard import ActorItem
    #     yield ActorItem(
    #         self.site.models.blogs.LatestEntries, header_level=None)
    # yield CustomItem(
    #     'blogs.Entry.latest_entries',
    #     self.models.blogs.Entry.latest_entries, max_num=10)
