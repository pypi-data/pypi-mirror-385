# Copyright 2017-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Adds voting functionality.

See :doc:`/plugins/votes`.


"""

from lino.api import ad, _

from lino.core.utils import resolve_model


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Votes")

    ## settings
    votable_model = 'tickets.Ticket'
    """The things we are voting about. A string referring to the model
    that represents a votable in your application.

    Default value is ``'tickets.Ticket'`` (referring to
    :class:`lino_xl.lib.tickets.Ticket`).

    """

    with_candidatures = False
    """
    Whether to use votes for implementing a kind of polling: when somebody posts
    a ticket, other users are asked to vote on it, deciding whether they take it
    or not.
    """

    def pre_site_startup(self, site):
        # print("votes.pre_site_startup")
        self.votable_model = resolve_model(self.votable_model)
        super().pre_site_startup(site)

    def setup_main_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        # mg = site.plugins[self.votable_model._meta.app_label]
        # mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        if self.with_candidatures:
            m.add_action('votes.MyInvitations')
            m.add_action('votes.MyTasks')
            m.add_action('votes.MyOffers')
            m.add_action('votes.MyWatched')
            # m.add_action('votes.MyVotes')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        # p = site.plugins.tickets
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('votes.AllVotes')
        m.add_action('votes.VoteStates')

    def get_dashboard_items(self, user):
        if self.with_candidatures and user.is_authenticated:
            yield self.site.models.votes.MyInvitations
            yield self.site.models.votes.MyTasks
            # yield self.site.models.votes.MyOffers
            yield self.site.models.votes.MyWatched
