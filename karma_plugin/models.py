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
        given: {
            positive: 0,
            negative: 0
        },
        received: {
            positive: this.vote > 0 ? 1 : 0,
            negative: this.vote < 0 ? 1 : 0
        }
    })
    emit(this.giver_user_id, {
        first_name: this.giver_first_name,
        given: {
            positive: this.vote > 0 ? 1 : 0,
            negative: this.vote < 0 ? 1 : 0
        },
        received: {
            positive: 0,
            negative: 0
        }
    })
}
"""

        reduce_f = """
function (key, values) {
    return {
        first_name: values[0].first_name,
        given: {
            positive: Array.sum(values.map(v => v.given.positive)),
            negative: Array.sum(values.map(v => v.given.negative))
        },
        received: {
            positive: Array.sum(values.map(v => v.received.positive)),
            negative: Array.sum(values.map(v => v.received.negative))
        }
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
    emit (this.receiver_user_id, {
        receiver_user_id: this.receiver_user_id,
        receiver_first_name: this.receiver_first_name,
        giver_user_id: this.giver_user_id,
        giver_first_name: this.giver_first_name,
        karma: this.vote
    })
}
"""
        reduce_f = """
function (key, values) {
    if (!values.length) {
        return {
            karma: 0
        }
    }
    const response = {
        receiver_first_name: values[values.length - 1].receiver_first_name,
        karma: 0,
        lovers: {
            karma: 0,
            givers: {}
        },
        haters: {
            karma: 0,
            givers: {}
        }
    }
    for (let value of values) {
        const w = ~value.karma ? 'lovers' : 'haters'
        response.karma += ~value.karma ? 1 : -1
        response[w].karma++
        if (!response[w].givers[value.giver_user_id]) {
            response[w].givers[value.giver_user_id] = {
                user_id: `${value.giver_user_id}`,
                first_name: value.giver_first_name,
                karma: 0,
            }
        }
        response[w].givers[value.giver_user_id].karma++
    }
    
    ['lovers','haters'].forEach(function(w) {
        response[w].givers = Object.keys(response[w].givers).map(function (giver_user_id) {
            return response[w].givers[giver_user_id]
        })
        
        response[w].givers.sort(function (a, b) {
            return b.karma - a.karma
        })
        response[w].givers = response[w].givers.slice(0, 3)
    })
    return response
}
"""
        try:
            return cls.objects(
                chat_id=chat_id,
                receiver_user_id=receiver_user_id,
                date_added__gte=Karma.get_last_quarter()
            ).map_reduce(map_f, reduce_f, 'inline')
        except:
            return None
