# -*- coding: utf-8 -*-
from marvinbot.plugins import Plugin
from marvinbot.utils import localized_date, get_message, trim_accents
from marvinbot.handlers import CommonFilters, CommandHandler, MessageHandler
from marvinbot_simple_replies_plugin.models import KarmaReaction, KarmaPhrase, Reaction
import logging

log = logging.getLogger(__name__)


class MarvinbotKarmaPlugin(Plugin):
    def __init__(self):
        super(MarvinbotKarmaPlugin, self).__init__('karma')

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
        }

    def configure(self, config):
        log.info("Initializing Karma plugin")
        pass

    def setup_handlers(self, adapter):
        self.add_handler(MessageHandler([CommonFilters.text], self.on_text), priority=90)
        pass

    def setup_schedules(self, adapter):
        pass
