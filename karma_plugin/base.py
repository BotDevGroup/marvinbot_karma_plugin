# -*- coding: utf-8 -*-
from marvinbot.plugins import Plugin
from marvinbot.utils import trim_markdown
from marvinbot.handlers import CommonFilters, MessageHandler, CommandHandler
from marvinbot.filters import RegexpFilter
from karma_plugin.models import Karma
from karma_plugin.templates import *
import logging
import json
import tabulate
import re
import hyperloglog

tabulate.MIN_PADDING = 0

log = logging.getLogger(__name__)

UPVOTE_PATTERN = r'(\+(?!0+)(\d+)|rt)'

DOWNVOTE_PATTERN = r'(-(?!0+)(\d+)|old|menos uno)'


class KarmaPlugin(Plugin):
    def __init__(self):
        super(KarmaPlugin, self).__init__('karma')
        self.config = {}

        self.telegram_cardinality = 0
        self.hll = hyperloglog.HyperLogLog(0.01)  #1% counting error

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
        }

    def configure(self, config):
        log.info("Initializing Karma plugin")
        self.config = config

    def setup_handlers(self, adapter):
        log.info("Setting up handlers for Karma plugin")
        self.add_handler(CommandHandler(
            'karma', self.on_karma_command,
            command_description='Displays karma.')
        )
        self.add_handler(CommandHandler(
            'lovers', self.on_lovers_command,
            command_description='Displays the top 10 lovers.')
        )
        self.add_handler(CommandHandler(
            'haters', self.on_haters_command,
            command_description='Displays the top 10 haters.')
        )
        self.add_handler(CommandHandler(
            'loved', self.on_loved_command,
            command_description='Displays the top 10 loved users.')
        )
        self.add_handler(CommandHandler(
            'hated', self.on_hated_command,
            command_description='Displays the top 10 hated users.')
        )
        self.add_handler(CommandHandler(
            'karmareport', self.on_karmareport_command,
            command_description='Displays the karma report.')
            .add_argument('--inline', help='Displays the karma report inline.', action='store_true')
            .add_argument('--global', help='Displays the global karma report.', action='store_true')
        )
        self.add_handler(MessageHandler([
            CommonFilters.text,
            CommonFilters.reply,
            RegexpFilter(UPVOTE_PATTERN, flags=re.IGNORECASE)
        ], self.on_upvote), priority=90)
        self.add_handler(MessageHandler([
            CommonFilters.text,
            CommonFilters.reply,
            RegexpFilter(DOWNVOTE_PATTERN, flags=re.IGNORECASE)
        ], self.on_downvote), priority=90)

    def provide_blueprint(self, config):
        from .views import karma_app
        return karma_app

    @staticmethod
    def get_karma_report(chat_id=None):
        results = [result.value for result in list(Karma.get_report(chat_id))]
        results.sort(key=lambda result: result.get('love_received'), reverse=True)
        return results

    def on_karmareport_command(self, update, **kwargs):
        message = update.effective_message
        inline = kwargs.get('inline')
        show_global = kwargs.get('global', False)
        chat_id = message.chat.id if show_global is False else None

        if not inline:
            if show_global:
                text = "[View global report]({}/plugins/{})".format(self.config.get('base_url'), self.name)
            else:
                text = "[View report]({}/plugins/{}/{})".format(self.config.get('base_url'), self.name, chat_id)
            message.reply_text(text=text, disable_web_page_preview=True, parse_mode='Markdown')
            return

        results = KarmaPlugin.get_karma_report(chat_id)
        if len(results) == 0:
            message.reply_text(text=NO_KARMA)
            return

        table = tabulate.tabulate([
            [
                trim_markdown(result.get('first_name')[:16]),
                result.get('love_received', 0),
                result.get('hate_received', 0),
                result.get('love_given', 0),
                result.get('hate_given', 0)
            ]
            for result in results[:30]
        ],
            headers=['Name', "Recvd\n+1", "Recvd\n-1",
                     "Given\n+1", "Given\n-1"],
            tablefmt="fancy_grid")
        text = """```
{}
```
""".format(table)

        message.reply_text(text=text, parse_mode='Markdown')

    def on_lovers_command(self, update):
        message = update.effective_message
        chat_id = message.chat.id

        results = [result.value for result in list(Karma.get_lovers(chat_id))]
        if len(results) == 0:
            message.reply_text(text=NO_LOVERS)
            return

        results.sort(key=lambda result: result.get('karma'), reverse=True)

        users = '\n'.join([
            '{first_name} (+{karma})'.format(
                first_name=result.get('first_name'),
                karma=int(result.get('karma'))
            )
            for result in results[:10]
        ])
        message.reply_text(text=KARMA_LOVERS.format(users=users),
                           parse_mode='Markdown')

    def on_loved_command(self, update):
        message = update.effective_message
        chat_id = message.chat.id

        results = [result.value for result in list(Karma.get_loved(chat_id))]
        if len(results) == 0:
            message.reply_text(text=NO_LOVED_ONES)
            return

        results.sort(key=lambda result: result.get('karma'), reverse=True)

        users = '\n'.join([
            '{first_name} (+{karma})'.format(
                first_name=result.get('first_name'),
                karma=int(result.get('karma'))
            )
            for result in results[:10]
        ])
        message.reply_text(text=KARMA_LOVED_ONES.format(users=users),
                           parse_mode='Markdown')

    def on_haters_command(self, update):
        message = update.effective_message
        chat_id = message.chat.id

        results = [result.value for result in list(Karma.get_haters(chat_id))]
        if len(results) == 0:
            message.reply_text(text=NO_HATERS)
            return

        results.sort(key=lambda result: result.get('karma'), reverse=True)
        users = '\n'.join([
            '{first_name} (-{karma})'.format(
                first_name=result.get('first_name'),
                karma=int(result.get('karma'))
            )
            for result in results[:10]
        ])
        message.reply_text(text=KARMA_HATERS.format(users=users),
                           parse_mode='Markdown')

    def on_hated_command(self, update):
        message = update.effective_message
        chat_id = message.chat.id

        results = [result.value for result in list(Karma.get_hated(chat_id))]
        if len(results) == 0:
            message.reply_text(text=NO_HATED_ONES)
            return

        results.sort(key=lambda result: result.get('karma'), reverse=True)
        users = '\n'.join([
            '{first_name} (-{karma})'.format(
                first_name=result.get('first_name'),
                karma=int(result.get('karma'))
            )
            for result in results[:10]
        ])
        message.reply_text(text=KARMA_HATED_ONES.format(users=users),
                           parse_mode='Markdown')

    def on_upvote(self, update):
        self.do_vote(update, 1)

    def on_downvote(self, update):
        self.do_vote(update, -1)

    def on_karma_command(self, update):
        message = update.effective_message
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id

        results = list(Karma.get_user_karma(chat_id, user_id))
        if len(results) == 0:
            message.reply_text(text=KARMA_NOT_FOUND)
            return

        for result in results:
            value = result.value

            lovers = value.get('lovers', [])
            haters = value.get('haters', [])

            lovers_str = '\n'.join([
                    '{first_name} (+{karma})'.format(
                        first_name=giver.get('first_name'),
                        karma=int(giver.get('love'))
                    ) for giver in lovers
                ]) if len(lovers) else '_None_'

            haters_str = '\n'.join([
                    '{first_name} (-{karma})'.format(
                        first_name=giver.get('first_name'),
                        karma=int(giver.get('hate'))
                    ) for giver in haters
                ]) if len(haters) else '_None_'

            love = int(value.get('love', 0))
            hate = int(value.get('hate', 0))

            text_vars = {
                'receiver_first_name': value.get('first_name'),
                'karma': love - hate,
                'positive': love,
                'negative': hate,
                'lovers': lovers_str,
                'haters': haters_str
            }
            message.reply_text(
                text=SINGLE_USER_KARMA_SUMMARY.format(**text_vars),
                parse_mode='Markdown'
            )

    @staticmethod
    def add_karma(**kwargs):
        try:
            karma = Karma(**kwargs)
            karma.save()
            return True
        except Exception as ex:
            log.error(ex)
            return False

    @staticmethod
    def user_link(name, id):
        return "[{name}](tg://user?id={id})".format(name=name, id=id)

    def do_vote(self, update, vote):
        message = update.effective_message
        reply_message = message.reply_to_message

        #if message.from_user.id == reply_message.from_user.id:
        #    self.adapter.bot.sendMessage(chat_id=message.chat_id,
        #                                 text=NOT_POSSIBLE)
        #    return

        if reply_message.text is not None:
            if (re.match(UPVOTE_PATTERN, reply_message.text) or
                    re.match(DOWNVOTE_PATTERN, reply_message.text)):
                self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                             text=NOT_POSSIBLE)
                return

        # Also, we don't want a user to upvote a message more than once.
        # For that we'll use a randomized algorithm called Hyperloglog.
        user_message_fingerprint = "{}-{}-{}".format(message.chat_id, reply_message.message_id, message.from_user.id)

        # compute the user-message-fingerprint into the cardinality set
        self.hll.add(user_message_fingerprint)

        # if the count doesn't change, someone is trying to upvote a single
        # comment more that once.
        if len(self.hll) == self.telegram_cardinality:
            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                         text=DUPLICATE_KARMA)
            return

        # If we hit this line, we should increase the cardinality to mark
        # this message as computed.
        self.telegram_cardinality += 1

        fields = {
            'chat_id': message.chat_id,
            'message_text': reply_message.text,
            'giver_first_name': message.from_user.first_name,
            'giver_last_name': message.from_user.last_name,
            'giver_username': message.from_user.username,
            'giver_user_id': message.from_user.id,
            'receiver_first_name': reply_message.from_user.first_name,
            'receiver_last_name': reply_message.from_user.last_name,
            'receiver_username': reply_message.from_user.username,
            'receiver_user_id': reply_message.from_user.id,
            'vote': vote
        }

        if KarmaPlugin.add_karma(**fields):
            text_vars = {
                'giver': KarmaPlugin.user_link(
                    name=trim_markdown(
                        fields.get('giver_first_name')
                    ),
                    id=fields.get('giver_user_id')
                ),
                'receiver': '*{}*'.format(
                    trim_markdown(fields.get('receiver_first_name'))
                )
            }
            text = (POSITIVE_KARMA if vote > 0 else NEGATIVE_KARMA)

            self.adapter.bot.sendMessage(
                chat_id=message.chat_id,
                text=text.format(**text_vars),
                parse_mode='Markdown',
                disable_notification=True
            )
        else:
            self.adapter.bot.sendMessage(
                chat_id=message.chat_id, text=KARMA_NOT_SAVED)
