import graphene
import os
from py2neo import Graph

# Internal imports
from .commentgo import Comment
from .albumgo import Album
from .placego import Place
from .persongo import Person
from .schemasdef import PlaceSchema, PlaceInput, PlaceDetailsSchema,\
    PersonSchema, PersonInput, VisitorInput,\
    AlbumSchema, AlbumInput, PlaceAlbumInput,\
    FriendsInput, FollowingInput, PersonAlbumInput, CommentSchema,\
    CommentQuerySchema, CommentInput, CommentDeleteInput,\
    PersonCommentInput, AlbumCommentInput
from .mongo import insert_to_mongodb, find_in_mongodb, delete_from_mongodb
from .mongo import insert_to_basers_mongodb, find_in_basers_mongodb,\
    delete_from_basers_mongodb

# Environment variables
url = os.environ['NEO4J_URL']
username = os.environ['NEO4J_USERNAME']
password = os.environ['NEO4J_PASSWORD']

# Global variables
graph = Graph(url, auth=(username, password))


class CreatePlace(graphene.Mutation):

    class Arguments:
        place_data = PlaceInput(required=True)

    place = graphene.Field(PlaceSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_data=None):
        # Insert into MongoDB
        if not insert_to_mongodb(_id=place_data.place_id,
                                 data=place_data.google_place_details):
            ok = False
            message = "Insertion to MongoDB failed"
            return CreatePlace(place=None, ok=ok, message=message)

        # Insert into GraphDB
        place = Place(place_id=place_data.place_id,
                      timestamp=place_data.timestamp)

        place.save(graph)
        ok = True
        message = "Success"

        return CreatePlace(place=place, ok=ok, message=message)


class CreateBaseRSPlace(graphene.Mutation):

    class Arguments:
        place_data = PlaceInput(required=True)

    place_id = graphene.String()
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_data=None):
        # Insert into MongoDB
        if not insert_to_basers_mongodb(_id=place_data.place_id,
                                        timestamp=place_data.timestamp,
                                        data=place_data.google_place_details):
            ok = False
            message = "Insertion to MongoDB failed"
            return CreatePlace(place_id=place_data.place_id,
                               ok=ok, message=message)

        ok = True
        message = "Success"

        return CreateBaseRSPlace(place_id=place_data.place_id,
                                 ok=ok, message=message)


class CreatePerson(graphene.Mutation):

    class Arguments:
        person_data = PersonInput(required=True)

    person = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_data=None):
        person = Person(google_id=person_data.google_id,
                        email=person_data.email,
                        verified_email=person_data.verified_email,
                        name=person_data.name,
                        given_name=person_data.given_name,
                        family_name=person_data.family_name,
                        picture=person_data.picture,
                        locale=person_data.locale)

        person.save(graph)
        ok = True
        message = "Success"

        return CreatePerson(person=person, ok=ok, message=message)


class CreateAlbum(graphene.Mutation):

    class Arguments:
        album_data = AlbumInput(required=True)

    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, album_data=None):
        album = Album(album_id=album_data.album_id,
                      private=album_data.private)
        album.save(graph)
        ok = True
        message = "Success"

        return CreateAlbum(album=album, ok=ok, message=message)


class CreateComment(graphene.Mutation):

    class Arguments:
        comment_data = CommentInput(required=True)

    comment = graphene.Field(CommentSchema)
    key = graphene.Int()
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, comment_data=None):
        comment = Comment(text=comment_data.text,
                          timestamp=comment_data.timestamp)

        # To get the unique key, first need to store in DB
        comment.save(graph)
        key = comment.__primaryvalue__
        ok = True
        message = "Success"

        return CreateComment(comment=comment, key=key, ok=ok, message=message)


# Relationship between place and its visitor
class LinkPlaceVisitor(graphene.Mutation):

    class Arguments:
        visitor_data = VisitorInput(required=True)

    place = graphene.Field(PlaceSchema)
    visitor = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, visitor_data=None):
        place = Place.match(graph, visitor_data.place_id).first()
        visitor = Person.match(graph, visitor_data.visitor_google_id).first()

        if not place or not visitor:
            ok = False
            message = "Either place or visitor not available"
            return LinkPlaceVisitor(place=None, visitor=None,
                                    ok=ok, message=message)

        place.add_or_update_visitor(visitor)
        place.save(graph)

        visitor.add_or_update_visited_place(place)
        visitor.save(graph)
        ok = True
        message = "Success"

        return LinkPlaceVisitor(place=place, visitor=visitor,
                                ok=ok, message=message)


class DelinkPlaceVisitor(graphene.Mutation):

    class Arguments:
        visitor_data = VisitorInput(required=True)

    place = graphene.Field(PlaceSchema)
    visitor = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, visitor_data=None):
        place = Place.match(graph, visitor_data.place_id).first()
        visitor = Person.match(graph, visitor_data.visitor_google_id).first()

        if not place or not visitor:
            ok = False
            message = "Either place or visitor not available"
            return DelinkPlaceVisitor(place=None, visitor=None,
                                      ok=ok, message=message)

        place.remove_visitor(visitor)
        place.save(graph)

        visitor.remove_visited_place(place)
        visitor.save(graph)
        ok = True
        message = "Success"

        return DelinkPlaceVisitor(place=place, visitor=visitor,
                                  ok=ok, message=message)


# Relationship between place and its album
class LinkPlaceAlbum(graphene.Mutation):

    class Arguments:
        place_album_data = PlaceAlbumInput(required=True)

    place = graphene.Field(PlaceSchema)
    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_album_data=None):
        place = Place.match(graph, place_album_data.place_id).first()
        album = Album.match(graph, place_album_data.album_id).first()

        if not place or not album:
            ok = False
            message = "Either place or album not available"
            return LinkPlaceAlbum(place=None, album=None,
                                  ok=ok, message=message)

        place.add_or_update_album(album)
        place.save(graph)

        album.add_or_update_place(place)
        album.save(graph)
        ok = True
        message = "Success"

        return LinkPlaceAlbum(place=place, album=album,
                              ok=ok, message=message)


class DelinkPlaceAlbum(graphene.Mutation):

    class Arguments:
        place_album_data = PlaceAlbumInput(required=True)

    place = graphene.Field(PlaceSchema)
    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_album_data=None):
        place = Place.match(graph, place_album_data.place_id).first()
        album = Album.match(graph, place_album_data.album_id).first()

        if not place or not album:
            ok = False
            message = "Either place or album not available"
            return DelinkPlaceAlbum(place=None, album=None,
                                    ok=ok, message=message)

        place.remove_album(album)
        place.save(graph)

        album.remove_place(place)
        album.save(graph)
        ok = True
        message = "Success"

        return DelinkPlaceAlbum(place=place, album=album,
                                ok=ok, message=message)


# Establish friendship
class LinkFriends(graphene.Mutation):

    class Arguments:
        friends_data = FriendsInput(required=True)

    friend1 = graphene.Field(PersonSchema)
    friend2 = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, friends_data=None):
        friend1 = Person.match(graph, friends_data.friend1_google_id).first()
        friend2 = Person.match(graph, friends_data.friend2_google_id).first()

        if not friend1 or not friend2:
            ok = False
            message = "Either friend1 or friend2 not available"
            return LinkFriends(friend1=None, friend2=None,
                               ok=ok, message=message)

        friend1.add_or_update_friend(friend2)
        friend1.save(graph)

        friend2.add_or_update_friend(friend1)
        friend2.save(graph)
        ok = True
        message = "Success"

        return LinkFriends(friend1=friend1, friend2=friend2,
                           ok=ok, message=message)


class DelinkFriends(graphene.Mutation):

    class Arguments:
        friends_data = FriendsInput(required=True)

    friend1 = graphene.Field(PersonSchema)
    friend2 = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, friends_data=None):
        friend1 = Person.match(graph, friends_data.friend1_google_id).first()
        friend2 = Person.match(graph, friends_data.friend2_google_id).first()

        if not friend1 or not friend2:
            ok = False
            message = "Either friend1 or friend2 not available"
            return DelinkFriends(friend1=None, friend2=None,
                                 ok=ok, message=message)

        friend1.remove_friend(friend2)
        friend1.save(graph)

        friend2.remove_friend(friend1)
        friend2.save(graph)
        ok = True
        message = "Success"

        return DelinkFriends(friend1=friend1, friend2=friend2,
                             ok=ok, message=message)


# Establish following
class LinkFollowing(graphene.Mutation):

    class Arguments:
        following_data = FollowingInput(required=True)

    person = graphene.Field(PersonSchema)
    follower = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, following_data=None):
        person = Person.match(graph, following_data.person_google_id).first()
        follower = Person.match(graph,
                                following_data.follower_google_id).first()

        if not person or not follower:
            ok = False
            message = "Either person or follower not available"
            return LinkFollowing(person=None, follower=None,
                                 ok=ok, message=message)

        person.add_or_update_follower(follower)
        person.save(graph)

        follower.add_or_update_following(person)
        follower.save(graph)
        ok = True
        message = "Success"

        return LinkFollowing(person=person, follower=follower,
                             ok=ok, message=message)


class DelinkFollowing(graphene.Mutation):

    class Arguments:
        following_data = FollowingInput(required=True)

    person = graphene.Field(PersonSchema)
    follower = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, following_data=None):
        person = Person.match(graph, following_data.person_google_id).first()
        follower = Person.match(graph,
                                following_data.follower_google_id).first()

        if not person or not follower:
            ok = False
            message = "Either person or follower not available"
            return DelinkFollowing(person=None, follower=None,
                                   ok=ok, message=message)

        person.remove_follower(follower)
        person.save(graph)

        follower.remove_following(person)
        follower.save(graph)
        ok = True
        message = "Success"

        return DelinkFollowing(person=person, follower=follower,
                               ok=ok, message=message)


# Relationship between person and album posted
class LinkPersonAlbum(graphene.Mutation):

    class Arguments:
        person_album_data = PersonAlbumInput(required=True)

    person = graphene.Field(PersonSchema)
    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_album_data=None):
        person = Person.match(graph,
                              person_album_data.person_google_id).first()
        album = Album.match(graph, person_album_data.album_id).first()

        if not person or not album:
            ok = False
            message = "Either person or album not available"
            return LinkPersonAlbum(person=None, album=None,
                                   ok=ok, message=message)

        person.add_or_update_posted_album(album)
        person.save(graph)

        album.add_or_update_poster(person)
        album.save(graph)
        ok = True
        message = "Success"

        return LinkPersonAlbum(person=person, album=album,
                               ok=ok, message=message)


class DelinkPersonAlbum(graphene.Mutation):

    class Arguments:
        person_album_data = PersonAlbumInput(required=True)

    person = graphene.Field(PersonSchema)
    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_album_data=None):
        person = Person.match(graph,
                              person_album_data.person_google_id).first()
        album = Album.match(graph, person_album_data.album_id).first()

        if not person or not album:
            ok = False
            message = "Either person or album not available"
            return DelinkPersonAlbum(person=None, album=None,
                                     ok=ok, message=message)

        person.remove_posted_album(album)
        person.save(graph)

        album.remove_poster(person)
        album.save(graph)
        ok = True
        message = "Success"

        return DelinkPersonAlbum(person=person, album=album,
                                 ok=ok, message=message)


# Relationship between person and comment posted
class LinkPersonComment(graphene.Mutation):

    class Arguments:
        person_comment_data = PersonCommentInput(required=True)

    person = graphene.Field(PersonSchema)
    comment = graphene.Field(CommentSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_comment_data=None):
        person = Person.match(graph,
                              person_comment_data.person_google_id).first()
        comment = Comment.match(graph, person_comment_data.comment_key).first()

        if not person or not comment:
            ok = False
            message = "Either person or comment not available"
            return LinkPersonComment(person=None, comment=None,
                                     ok=ok, message=message)

        person.add_or_update_posted_comment(comment)
        person.save(graph)

        comment.add_or_update_poster(person)
        comment.save(graph)
        ok = True
        message = "Success"

        return LinkPersonComment(person=person, comment=comment,
                                 ok=ok, message=message)


class DelinkPersonComment(graphene.Mutation):

    class Arguments:
        person_comment_data = PersonCommentInput(required=True)

    person = graphene.Field(PersonSchema)
    comment = graphene.Field(CommentSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_comment_data=None):
        person = Person.match(graph,
                              person_comment_data.person_google_id).first()
        comment = Comment.match(graph, person_comment_data.comment_key).first()

        if not person or not comment:
            ok = False
            message = "Either person or comment not available"
            return DelinkPersonComment(person=None, comment=None,
                                       ok=ok, message=message)

        person.remove_posted_comment(comment)
        person.save(graph)

        comment.remove_poster(person)
        comment.save(graph)
        ok = True
        message = "Success"

        return DelinkPersonComment(person=person, comment=comment,
                                   ok=ok, message=message)


# Relationship between album and comment
class LinkAlbumComment(graphene.Mutation):

    class Arguments:
        album_comment_data = AlbumCommentInput(required=True)

    album = graphene.Field(AlbumSchema)
    comment = graphene.Field(CommentSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, album_comment_data=None):
        album = Album.match(graph, album_comment_data.album_id).first()
        comment = Comment.match(graph, album_comment_data.comment_key).first()

        if not album or not comment:
            ok = False
            message = "Either album or comment not available"
            return LinkAlbumComment(album=None, comment=None,
                                    ok=ok, message=message)

        album.add_or_update_comment(comment)
        album.save(graph)

        comment.add_or_update_album(album)
        comment.save(graph)
        ok = True
        message = "Success"

        return LinkAlbumComment(album=album, comment=comment,
                                ok=ok, message=message)


class DelinkAlbumComment(graphene.Mutation):

    class Arguments:
        album_comment_data = AlbumCommentInput(required=True)

    album = graphene.Field(AlbumSchema)
    comment = graphene.Field(CommentSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, album_comment_data=None):
        album = Album.match(graph, album_comment_data.album_id).first()
        comment = Comment.match(graph, album_comment_data.comment_key).first()

        if not album or not comment:
            ok = False
            message = "Either album or comment not available"
            return DelinkAlbumComment(album=None, comment=None,
                                      ok=ok, message=message)

        album.remove_comment(comment)
        album.save(graph)

        comment.remove_album(album)
        comment.save(graph)
        ok = True
        message = "Success"

        return DelinkAlbumComment(album=album, comment=comment,
                                  ok=ok, message=message)


class DeletePlace(graphene.Mutation):

    class Arguments:
        place_data = PlaceInput(required=True)

    place = graphene.Field(PlaceSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_data=None):
        place = Place.match(graph, place_data.place_id).first()

        if not place:
            ok = False
            message = "place not available"
            return DeletePlace(place=None,
                               ok=ok, message=message)

        if len(place.albums) != 0:
            ok = False
            message = "place has other associated information"
            return DeletePlace(place=None,
                               ok=ok, message=message)

        # Delete it from MongoDB
        if not delete_from_mongodb(_id=place_data.place_id):
            ok = False
            message = "Delete from MongoDB failed"
            return DeletePlace(place=None,
                               ok=ok, message=message)

        place.delete(graph)
        ok = True
        message = "Success"

        return DeletePlace(place=place,
                           ok=ok, message=message)


class DeleteBaseRSPlace(graphene.Mutation):

    class Arguments:
        place_data = PlaceInput(required=True)

    place_id = graphene.String()
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_data=None):
        # Delete it from MongoDB
        if not delete_from_basers_mongodb(_id=place_data.place_id):
            ok = False
            message = "Delete from MongoDB failed"
            return DeletePlace(place_id=place_data.place_id,
                               ok=ok, message=message)

        ok = True
        message = "Success"

        return DeletePlace(place_id=place_data.place_id,
                           ok=ok, message=message)


class DeletePlaceByForce(graphene.Mutation):

    class Arguments:
        place_data = PlaceInput(required=True)

    place = graphene.Field(PlaceSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, place_data=None):
        place = Place.match(graph, place_data.place_id).first()

        if not place:
            ok = False
            message = "place not available"
            return DeletePlace(place=None,
                               ok=ok, message=message)

        # Delete it from MongoDB
        if not delete_from_mongodb(_id=place_data.place_id):
            ok = False
            message = "Delete from MongoDB failed"
            return DeletePlace(place=None,
                               ok=ok, message=message)

        if len(place.albums) != 0:
            place.clean_up(graph)

        place.delete(graph)
        ok = True
        message = "Success"

        return DeletePlace(place=place,
                           ok=ok, message=message)


class DeletePerson(graphene.Mutation):

    class Arguments:
        person_data = PersonInput(required=True)

    person = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_data=None):
        person = Person.match(graph, person_data.google_id).first()

        if not person:
            ok = False
            message = "person not available"
            return DeletePerson(person=None,
                                ok=ok, message=message)

        if (len(person.posted_albums) != 0
                or len(person.posted_comments) != 0):
            ok = False
            message = "person has other associated information"
            return DeletePerson(person=None,
                                ok=ok, message=message)

        person.delete(graph)
        ok = True
        message = "Success"

        return DeletePerson(person=person,
                            ok=ok, message=message)


class DeletePersonByForce(graphene.Mutation):

    class Arguments:
        person_data = PersonInput(required=True)

    person = graphene.Field(PersonSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, person_data=None):
        person = Person.match(graph, person_data.google_id).first()

        if not person:
            ok = False
            message = "person not available"
            return DeletePerson(person=None,
                                ok=ok, message=message)

        if (len(person.posted_albums) != 0
                or len(person.posted_comments) != 0):
            person.clean_up(graph)

        person.delete(graph)
        ok = True
        message = "Success"

        return DeletePerson(person=person,
                            ok=ok, message=message)


class DeleteAlbum(graphene.Mutation):

    class Arguments:
        album_data = AlbumInput(required=True)

    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, album_data=None):
        album = Album.match(graph, album_data.album_id).first()

        if not album:
            ok = False
            message = "album not available"
            return DeleteAlbum(album=None,
                               ok=ok, message=message)

        if len(album.comments) != 0:
            ok = False
            message = "album has other associated information"
            return DeleteAlbum(album=None,
                               ok=ok, message=message)

        album.delete(graph)
        ok = True
        message = "Success"

        return DeleteAlbum(album=album,
                           ok=ok, message=message)


class DeleteAlbumByForce(graphene.Mutation):

    class Arguments:
        album_data = AlbumInput(required=True)

    album = graphene.Field(AlbumSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, album_data=None):
        album = Album.match(graph, album_data.key).first()

        if not album:
            ok = False
            message = "album not available"
            return DeleteAlbum(album=None,
                               ok=ok, message=message)

        if len(album.comments) != 0:
            album.clean_up(graph)

        album.delete(graph)
        ok = True
        message = "Success"

        return DeleteAlbum(album=album,
                           ok=ok, message=message)


class DeleteComment(graphene.Mutation):

    class Arguments:
        comment_data = CommentDeleteInput(required=True)

    comment = graphene.Field(CommentSchema)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, comment_data=None):
        comment = Comment.match(graph, comment_data.key).first()

        if not comment:
            ok = False
            message = "comment not available"
            return DeleteComment(comment=None,
                                 ok=ok, message=message)

        # No check for associated information needed here

        comment.delete(graph)
        ok = True
        message = "Success"

        return DeleteComment(comment=comment,
                             ok=ok, message=message)


class Query(graphene.ObjectType):
    place = graphene.Field(PlaceSchema, place_id=graphene.String())
    place_details = graphene.Field(PlaceDetailsSchema,
                                   place_id=graphene.String())
    person = graphene.Field(PersonSchema, google_id=graphene.String())
    album = graphene.Field(AlbumSchema, album_id=graphene.String())
    comment = graphene.Field(CommentQuerySchema, key=graphene.Int())

    # Base Recommendation System Places queries
    basers_place_details = graphene.Field(PlaceDetailsSchema,
                                          place_id=graphene.String())

    # Query to fetch all visitors to a particular place
    place_visitors = graphene.List(PersonSchema, place_id=graphene.String())

    # Query to fetch all place visits of a person
    person_visits = graphene.List(PlaceSchema, google_id=graphene.String())

    # Query to fetch all albums of a particular place
    place_albums = graphene.List(AlbumSchema, place_id=graphene.String())
    # Query to fetch only public albums of a particular place
    place_public_albums = graphene.List(AlbumSchema,
                                        place_id=graphene.String())

    # Query to fetch place in a particular album
    album_place = graphene.List(PlaceSchema, album_id=graphene.String())

    # Query to fetch all friends of a person
    friends = graphene.List(PersonSchema, google_id=graphene.String())

    # Query to fetch all followers of a person
    followers = graphene.List(PersonSchema, google_id=graphene.String())

    # Query to fetch all followings of a person
    followings = graphene.List(PersonSchema, google_id=graphene.String())

    # Query to fetch all albums posted by a person
    person_posted_albums = graphene.List(AlbumSchema,
                                         google_id=graphene.String())
    # Query to fetch only public albums posted by a person
    person_posted_public_albums = graphene.List(AlbumSchema,
                                                google_id=graphene.String())

    # Query to fetch poster of a particular album
    album_poster = graphene.List(PersonSchema, album_id=graphene.String())

    # Query to fetch all comments posted by a person
    person_posted_comments = graphene.List(CommentQuerySchema,
                                           google_id=graphene.String())

    # Query to fetch poster of a particular comment
    comment_poster = graphene.List(PersonSchema, key=graphene.Int())

    # Query to fetch comments posted on a particular album
    album_comments = graphene.List(CommentQuerySchema,
                                   album_id=graphene.String())

    # Query to fetch album associated with a particular comment
    # No need for specific public album information. Here assumption is that
    # if we have access to comments on album, album scope is already available.
    comment_album = graphene.List(AlbumSchema, key=graphene.Int())

    def resolve_place(self, info, place_id):
        place = Place.match(graph, place_id).first()

        if not place:
            return None

        return PlaceSchema(**place.as_dict())

    def resolve_place_details(self, info, place_id):
        doc = find_in_mongodb(_id=place_id)
        if doc is None:
            return None

        place_details = doc["google_place_details"]

        return PlaceDetailsSchema(place_id=place_id,
                                  google_place_details=place_details)

    def resolve_person(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return PersonSchema(**person.as_dict())

    def resolve_album(self, info, album_id):
        album = Album.match(graph, album_id).first()

        if not album:
            return None

        return AlbumSchema(**album.as_dict())

    def resolve_comment(self, info, key):
        comment = Comment.match(graph, key).first()

        if not comment:
            return None

        return CommentQuerySchema(**comment.as_dict())

    def resolve_basers_place_details(self, info, place_id):
        doc = find_in_basers_mongodb(_id=place_id)
        if doc is None:
            return None

        place_details = doc["google_place_details"]

        return PlaceDetailsSchema(place_id=place_id,
                                  google_place_details=place_details)

    def resolve_place_visitors(self, info, place_id):
        place = Place.match(graph, place_id).first()

        if not place:
            return None

        return [PersonSchema(**person.as_dict())
                for person in place.visitors]

    def resolve_person_visits(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return [PlaceSchema(**place.as_dict())
                for place in person.visited]

    def resolve_place_albums(self, info, place_id):
        place = Place.match(graph, place_id).first()

        if not place:
            return None

        return [AlbumSchema(**album.as_dict())
                for album in place.albums]

    def resolve_place_public_albums(self, info, place_id):
        place = Place.match(graph, place_id).first()

        if not place:
            return None

        return [AlbumSchema(**album.as_dict())
                for album in place.albums if not album.private]

    def resolve_album_place(self, info, album_id):
        album = Album.match(graph, album_id).first()

        if not album:
            return None

        return [PlaceSchema(**place.as_dict())
                for place in album.place]

    def resolve_friends(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return person

        return [PersonSchema(**friend.as_dict())
                for friend in person.friends]

    def resolve_followers(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return [PersonSchema(**follower.as_dict())
                for follower in person.followers]

    def resolve_followings(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return [PersonSchema(**following.as_dict())
                for following in person.followings]

    def resolve_person_posted_albums(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return [AlbumSchema(**album.as_dict())
                for album in person.posted_albums]

    def resolve_person_posted_public_albums(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return [AlbumSchema(**album.as_dict())
                for album in person.posted_albums if not album.private]

    def resolve_album_poster(self, info, album_id):
        album = Album.match(graph, album_id).first()

        if not album:
            return None

        return [PersonSchema(**person.as_dict())
                for person in album.poster]

    def resolve_person_posted_comments(self, info, google_id):
        person = Person.match(graph, google_id).first()

        if not person:
            return None

        return [CommentQuerySchema(**comment.as_dict())
                for comment in person.posted_comments]

    def resolve_comment_poster(self, info, key):
        comment = Comment.match(graph, key).first()

        if not comment:
            return None

        return [PersonSchema(**person.as_dict())
                for person in comment.poster]

    def resolve_album_comments(self, info, album_id):
        album = Album.match(graph, album_id).first()

        if not album:
            return None

        return [CommentQuerySchema(**comment.as_dict())
                for comment in album.comments]

    def resolve_comment_album(self, info, key):
        comment = Comment.match(graph, key).first()

        if not comment:
            return None

        return [AlbumSchema(**album.as_dict())
                for album in comment.album]


class Mutations(graphene.ObjectType):
    create_place = CreatePlace.Field()
    delete_place = DeletePlace.Field()
    delete_place_by_force = DeletePlaceByForce.Field()

    create_person = CreatePerson.Field()
    delete_person = DeletePerson.Field()
    delete_person_by_force = DeletePersonByForce.Field()

    create_album = CreateAlbum.Field()
    delete_album = DeleteAlbum.Field()
    delete_album_by_force = DeleteAlbum.Field()

    create_comment = CreateComment.Field()
    delete_comment = DeleteComment.Field()
    # delete_comment_by_force not needed currently since comment
    # has no associated information at present.

    link_place_visitor = LinkPlaceVisitor.Field()
    delink_place_visitor = DelinkPlaceVisitor.Field()

    link_place_album = LinkPlaceAlbum.Field()
    delink_place_album = DelinkPlaceAlbum.Field()

    link_friends = LinkFriends.Field()
    delink_friends = DelinkFriends.Field()

    link_following = LinkFollowing.Field()
    delink_following = DelinkFollowing.Field()

    link_person_album = LinkPersonAlbum.Field()
    delink_person_album = DelinkPersonAlbum.Field()

    link_person_comment = LinkPersonComment.Field()
    delink_person_comment = DelinkPersonComment.Field()

    link_album_comment = LinkAlbumComment.Field()
    delink_album_comment = DelinkAlbumComment.Field()


schema = graphene.Schema(query=Query,
                         mutation=Mutations,
                         auto_camelcase=False)
