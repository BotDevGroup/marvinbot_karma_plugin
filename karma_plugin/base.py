# -*- coding: utf-8 -*-
from marvinbot.plugins import Plugin
from marvinbot.utils import get_message, trim_accents
from marvinbot.handlers import CommonFilters, MessageHandler
from marvinbot.filters import RegexpFilter
from karma_plugin.models import Karma
import logging

log = logging.getLogger(__name__)

UPVOTE_PATTERNS = [
    r'^\+(?!0+)(\d+)'
]

DOWNVOTE_PATTERNS = [
    r'^-(?!0+)(\d+)'
]

class KarmaPlugin(Plugin):
    def __init__(self):
        super(KarmaPlugin, self).__init__('karma')

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
        }

    def configure(self, config):
        log.info("Initializing Karma plugin")
        pass

    def setup_handlers(self, adapter):
        log.info("Setting up handlers for Karma plugin")
        self.add_handler(MessageHandler([CommonFilters.text, CommonFilters.reply, RegexpFilter(UPVOTE_PATTERNS[0])], self.on_upvote), priority=90)
        self.add_handler(MessageHandler([CommonFilters.text, CommonFilters.reply, RegexpFilter(DOWNVOTE_PATTERNS[0])], self.on_downvote), priority=90)

    @classmethod
    def add_karma(cls, **kwargs):
        try:
            karma = Karma(**kwargs)
            karma.save()
            return True
        except:
            return False

    @classmethod
    def username_as_link(cls, username):
        return "[{username}](http://telegram.me/{username})".format(username=username)

    def on_upvote(self, update):
        message = get_message(update)

        if message.from_user.id == message.reply_to_message.from_user.id:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="❌ Not possible.")
            return

        if not message.from_user.username:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="❌ You must set your username first to use this feature.")
            return

        if not message.reply_to_message.from_user.username:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="❌ That user must set their username first to use this feature.")
            return

        data = {
            'chat_id': message.chat_id,
            'message_id': message.message_id,
            'response_message_id': message.reply_to_message.message_id,
            'message': message.text,
            'giver_user_id': message.from_user.id,
            'giver_username': message.from_user.username,
            'receiver_user_id': message.reply_to_message.from_user.id,
            'receiver_username': message.reply_to_message.from_user.username,
            'vote': 1
        }
        if KarmaPlugin.add_karma(**data):
            receiver_username = KarmaPlugin.username_as_link(message.reply_to_message.from_user.username)
            giver_username = KarmaPlugin.username_as_link(message.from_user.username)
            text = "⬆ Positive karma for {} given by {}.".format(receiver_username, giver_username)
            self.adapter.bot.sendMessage(chat_id=message.chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            self.adapter.bot.sendMessage(chat_id=message.chat_id, text="❌ Unable to save karma.")

    def on_downvote(self, update):
        message = get_message(update)

        if message.from_user.id == message.reply_to_message.from_user.id:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="❌ Not possible.")
            return

        if not message.from_user.username:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="❌ You must set your username first to use this feature.")
            return

        if not message.reply_to_message.from_user.username:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                 text="❌ That user must set their username first to use this feature.")
            return

        data = {
            'chat_id': message.chat_id,
            'message_id': message.message_id,
            'response_message_id': message.reply_to_message.message_id,
            'message': message.text,
            'giver_user_id': message.from_user.id,
            'giver_username': message.from_user.username,
            'receiver_user_id': message.reply_to_message.from_user.id,
            'receiver_username': message.reply_to_message.from_user.username,
            'vote': -1
        }

        if KarmaPlugin.add_karma(**data):
            receiver_username = KarmaPlugin.username_as_link(message.reply_to_message.from_user.username)
            giver_username = KarmaPlugin.username_as_link(message.from_user.username)
            text = "⬇ Negative karma for {} given by {}.".format(receiver_username, giver_username)
            self.adapter.bot.sendMessage(chat_id=message.chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            self.adapter.bot.sendMessage(chat_id=message.chat_id, text="❌ Unable to save karma.")

