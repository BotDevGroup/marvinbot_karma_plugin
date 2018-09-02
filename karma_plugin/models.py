# pylint: disable=E1101
import mongoengine
from marvinbot.utils import localized_date
from datetime import timedelta

aggregate_map_f = """
function () {{
    emit (this.{who}_user_id, {{
        karma: 1,
        first_name: this.{who}_first_name
    }})
}}
"""

aggregate_reduce_f = """
function (key, values) {
    return {
        karma: Array.sum(values.map(v => v.karma)),
        first_name: values[values.length - 1].first_name
    }
}
"""


class Karma(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)

    chat_id = mongoengine.LongField(required=True)
    message_text = mongoengine.StringField(null=True)

    giver_first_name = mongoengine.StringField(required=True)
    giver_user_id = mongoengine.LongField(required=True)

    receiver_first_name = mongoengine.StringField(required=True)
    receiver_user_id = mongoengine.LongField(required=True)

    vote = mongoengine.IntField(required=True)

    date_added = mongoengine.DateTimeField(default=localized_date)

    @staticmethod
    def get_last_quarter():
        return localized_date() - timedelta(days=90)

    @classmethod
    def get_report(cls, chat_id):
        map_f = """
function () {
    emit(this.receiver_user_id, {
        first_name: this.receiver_first_name,
        hate_received: this.vote < 0 ? 1 : 0,
        love_received: this.vote > 0 ? 1 : 0,
        hate_given: 0,
        love_given: 0
    })
    emit(this.giver_user_id, {
        first_name: this.giver_first_name,
        hate_given: this.vote < 0 ? 1 : 0,
        love_given: this.vote > 0 ? 1 : 0,
        hate_received: 0,
        love_received: 0
    })
}
"""

        reduce_f = """
function (key, values) {
    const { love_given, hate_given, love_received, hate_received } = values.reduce((prev, next) => {
        return {
            love_given: prev.love_given + next.love_given,
            hate_given: prev.hate_given + next.hate_given,
            love_received: prev.love_received + next.love_received,
            hate_received: prev.hate_received + next.hate_received
        }
    }, {
        love_given: 0,
        hate_given: 0,
        love_received: 0,
        hate_received: 0
    })

    return {
        first_name: values[0].first_name,
        love_given,
        hate_given,
        love_received,
        hate_received
    }
}
"""
        try:
            return cls.objects(
                chat_id=chat_id,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(map_f, reduce_f, 'inline')
        except:
            return None

    @classmethod
    def get_lovers(cls, chat_id):
        try:
            return cls.objects(
                chat_id=chat_id,
                vote__gt=0,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(aggregate_map_f.format(who='giver'), aggregate_reduce_f, 'inline')
        except:
            return None

    @classmethod
    def get_loved(cls, chat_id):
        try:
            return cls.objects(
                chat_id=chat_id,
                vote__gt=0,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(aggregate_map_f.format(who='receiver'), aggregate_reduce_f, 'inline')
        except:
            return None

    @classmethod
    def get_haters(cls, chat_id):
        try:
            return cls.objects(
                chat_id=chat_id,
                vote__lt=0,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(aggregate_map_f.format(who='giver'), aggregate_reduce_f, 'inline')
        except:
            return None

    @classmethod
    def get_hated(cls, chat_id):
        try:
            return cls.objects(
                chat_id=chat_id,
                vote__lt=0,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(aggregate_map_f.format(who='receiver'), aggregate_reduce_f, 'inline')
        except:
            return None

    @classmethod
    def get_user_karma(cls, chat_id, receiver_user_id):
        map_f = """
function () {
    const {
        receiver_user_id,
        receiver_first_name,
        giver_user_id,
        giver_first_name,
        vote
    } = this
    const love = +(vote === 1)
    const hate = 1 - love
    const givers = {}
    givers[giver_user_id] = {
        giver_user_id,
        first_name: giver_first_name,
        love,
        hate
    }
    emit (receiver_user_id, {
        first_name: receiver_first_name,
        love,
        hate,
        givers
    })
}
"""

        reduce_f = """
function (key, values) {
    return values.reduce((prev, next) => {
        const givers = Object.keys(next.givers).reduce((givers, giver_user_id) => {
            if (!givers[giver_user_id]) {
                givers[giver_user_id] = Object.assign({}, next.givers[giver_user_id])
                return givers
            }

            givers[giver_user_id] = Object.assign({}, givers[giver_user_id], {
                love: givers[giver_user_id].love + next.givers[giver_user_id].love,
                hate: givers[giver_user_id].hate + next.givers[giver_user_id].hate
            })

            return givers
        }, prev.givers)

        return {
            first_name: prev.first_name || next.first_name,
            love: prev.love + next.love,
            hate: prev.hate + next.hate,
            givers
        }
    }, {
        first_name: "",
        love: 0,
        hate: 0,
        givers: {}
    })
}
"""

        finalize_f = """
function (key, report) {
    function descending (key) {
        return function (a, b) {
            return b[key] - a[key]
        }
    }

    const lovers = Object.keys(report.givers)
        .map(giver_user_id => report.givers[giver_user_id])
        .filter(g => g.love)
        .sort(descending('love'))
        .slice(0, 3)

    const haters = Object.keys(report.givers)
        .map(giver_user_id => report.givers[giver_user_id])
        .filter(g => g.hate)
        .sort(descending('hate'))
        .slice(0, 3)

    return {
        first_name: report.first_name,
        love: report.love,
        hate: report.hate,
        lovers,
        haters
    }
}
"""
        try:
            return cls.objects(
                chat_id=chat_id,
                receiver_user_id=receiver_user_id,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(map_f, reduce_f, 'inline', finalize_f=finalize_f)
        except:
            return None
