import mongoengine
from marvinbot.utils import localized_date


class Karma(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)

    chat_id = mongoengine.LongField(required=True)
    message_id = mongoengine.LongField(required=True)
    response_message_id = mongoengine.LongField(null=True)

    message = mongoengine.StringField(required=True)

    giver_user_id = mongoengine.LongField(required=True)
    giver_username = mongoengine.StringField(required=True)

    receiver_user_id = mongoengine.LongField(required=True)
    receiver_username = mongoengine.StringField(required=True)

    vote = mongoengine.IntField(required=True)

    date_added = mongoengine.DateTimeField(default=localized_date)
    date_modified = mongoengine.DateTimeField(default=localized_date)
    date_deleted = mongoengine.DateTimeField(required=False, null=True)

    @classmethod
    def by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def by_chat_id_and_receiver_user_id(cls, chat_id, receiver_user_id):
        try:
            return cls.objects.get(chat_id=chat_id, receiver_user_id=receiver_user_id)
        except cls.DoesNotExist:
            return None


