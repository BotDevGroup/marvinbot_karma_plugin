import mongoengine
from marvinbot.utils import localized_date

KARMA_TYPES = (('upvote', '+1'),
               ('downvote', '-1'),
               ('reaction', 'Reaction')
               )


class Reaction(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    reaction = mongoengine.StringField(required=True)
    alias = mongoengine.StringField(required=True)

    user_id = mongoengine.LongField(required=True)
    username = mongoengine.StringField(required=True)

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
    def by_reaction(cls, reaction):
        try:
            return cls.objects.get(reaction=reaction)
        except cls.DoesNotExist:
            return None

    @classmethod
    def all(cls):
        try:
            return cls.objects(date_deleted=None)
        except:
            return None


class KarmaReaction(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    karma_type = mongoengine.StringField(choices=KARMA_TYPES, required=True)

    chat_id = mongoengine.LongField(required=True)
    message_id = mongoengine.LongField(required=True)

    response_message_id = mongoengine.LongField(null=True)

    reaction_id = mongoengine.LongField(null=True)

    giver_user_id = mongoengine.LongField(required=True)
    giver_username = mongoengine.StringField(required=True)

    receiver_user_id = mongoengine.LongField(required=True)
    receiver_username = mongoengine.StringField(required=True)

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
    def by_reaction_id(cls, reaction_id):
        try:
            return cls.objects.get(reaction_id=reaction_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def all(cls):
        try:
            return cls.objects(date_deleted=None)
        except:
            return None


class KarmaPhrase(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)

    chat_id = mongoengine.LongField(required=True)
    message_id = mongoengine.LongField(required=True)

    response_message_id = mongoengine.LongField(null=True)

    phrase = mongoengine.StringField(required=True)

    vote = mongoengine.IntField(required=True)

    user_id = mongoengine.LongField(required=True)
    username = mongoengine.StringField(required=True)

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
    def all(cls):
        try:
            return cls.objects(date_deleted=None)
        except:
            return None
