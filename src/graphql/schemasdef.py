import datetime
import graphene
from neotime import DateTime


class CustomGrapheneDateTime(graphene.DateTime):
    @staticmethod
    def serialize(date):
        if isinstance(date, DateTime):
            date = datetime.datetime(date.year, date.month, date.day,
                                     date.hour, date.minute, int(date.second),
                                     int(date.second * 1000000 % 1000000),
                                     tzinfo=date.tzinfo)
        return graphene.DateTime.serialize(date)


class PlaceSchema(graphene.ObjectType):
    place_id = graphene.String()
    timestamp = CustomGrapheneDateTime()


class PlaceIDSchema(graphene.ObjectType):
    place_id = graphene.String()


class PlaceDetailsSchema(graphene.ObjectType):
    place_id = graphene.String()
    google_place_details = graphene.types.json.JSONString()


class PlaceInput(graphene.InputObjectType):
    place_id = graphene.String(required=True)
    google_place_details = graphene.types.json.JSONString()
    timestamp = CustomGrapheneDateTime()


class PersonSchema(graphene.ObjectType):
    google_id = graphene.String()
    email = graphene.String()
    verified_email = graphene.Boolean()
    name = graphene.String()
    given_name = graphene.String()
    family_name = graphene.String()
    picture = graphene.String()
    locale = graphene.String()


class PersonInput(graphene.InputObjectType):
    google_id = graphene.String(required=True)
    email = graphene.String()
    verified_email = graphene.Boolean()
    name = graphene.String()
    given_name = graphene.String()
    family_name = graphene.String()
    picture = graphene.String()
    locale = graphene.String()


class AlbumSchema(graphene.ObjectType):
    album_id = graphene.String()
    private = graphene.Boolean()


class AlbumInput(graphene.InputObjectType):
    album_id = graphene.String(required=True)
    private = graphene.Boolean()


class CommentSchema(graphene.ObjectType):
    text = graphene.String()
    timestamp = CustomGrapheneDateTime()


class CommentQuerySchema(graphene.ObjectType):
    key = graphene.Int()
    text = graphene.String()
    timestamp = CustomGrapheneDateTime()


class CommentInput(graphene.InputObjectType):
    text = graphene.String()
    timestamp = CustomGrapheneDateTime()


class CommentDeleteInput(graphene.InputObjectType):
    key = graphene.Int(required=True)


# Place Person relationship
class VisitorInput(graphene.InputObjectType):
    place_id = graphene.String(required=True)
    visitor_google_id = graphene.String(required=True)


# Place Album relationship
class PlaceAlbumInput(graphene.InputObjectType):
    place_id = graphene.String(required=True)
    album_id = graphene.String(required=True)


# Friend relationship
class FriendsInput(graphene.InputObjectType):
    friend1_google_id = graphene.String(required=True)
    friend2_google_id = graphene.String(required=True)


# Friend Request
class FriendRequestInput(graphene.InputObjectType):
    person_google_id = graphene.String(required=True)
    friend_google_id = graphene.String(required=True)


# Following relationship
class FollowingInput(graphene.InputObjectType):
    person_google_id = graphene.String(required=True)
    follower_google_id = graphene.String(required=True)


# Person Album relationship
class PersonAlbumInput(graphene.InputObjectType):
    person_google_id = graphene.String(required=True)
    album_id = graphene.String(required=True)


# Person Comment relationship
class PersonCommentInput(graphene.InputObjectType):
    person_google_id = graphene.String(required=True)
    comment_key = graphene.Int(required=True)


# Album Comment relationship
class AlbumCommentInput(graphene.InputObjectType):
    album_id = graphene.String(required=True)
    comment_key = graphene.Int(required=True)
