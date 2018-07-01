import mongoengine
from marvinbot.utils import localized_date


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

    # @classmethod
    # def by_id(cls, id):
    #     try:
    #         return cls.objects.get(id=id)
    #     except cls.DoesNotExist:
    #         return None

    @classmethod
    def by_chat_id_and_receiver_user_id(cls, chat_id, receiver_user_id):
        try:
            return cls.objects(chat_id=chat_id, receiver_user_id=receiver_user_id)
        except cls.DoesNotExist:
            return None


    @classmethod
    def get_lovers(cls, chat_id):
        map_f = """
function () {
    emit (this.giver_user_id, {
        first_name: this.giver_first_name
    })
}
"""
        reduce_f = """
function (key, values) {
    return { karma: values.length, first_name: values[values.length - 1].first_name }
}
"""
        try:
            return cls.objects(chat_id=chat_id, vote__gt=0).map_reduce(map_f, reduce_f, 'inline')
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
        vote: this.vote
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
        const w = ~value.vote ? 'lovers' : 'haters'
        response.karma += ~value.vote ? 1 : -1
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
            return cls.objects(chat_id=chat_id, receiver_user_id=receiver_user_id).map_reduce(map_f, reduce_f, 'inline')
        except:
            return None
