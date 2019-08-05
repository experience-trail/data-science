from py2neo.ogm import GraphObject, Property
from py2neo.ogm import RelatedTo, RelatedFrom, Related


class Person(GraphObject):
    __primarykey__ = "google_id"

    google_id = Property()
    email = Property()
    verified_email = Property()
    name = Property()
    given_name = Property()
    family_name = Property()
    picture = Property()
    locale = Property()

    # Set of friends. This is bi-directional relationship
    friends = Related("Person")

    # Set of friend requests sent
    friend_requests_sent = RelatedTo("Person")

    # Set of friend requests received
    friend_requests_recv = RelatedFrom("Person")

    # Set of Person whom the Person follows
    followings = RelatedTo("Person", "FOLLOWINGS")

    # Set of Person who follow the Person
    followers = RelatedFrom("Person", "FOLLOWERS")

    # Set of Places visted by Person
    visited = RelatedTo("Place")

    # Set of Albums posted by Person
    posted_albums = RelatedTo("Album")

    # Set of Comments posted by Person
    posted_comments = RelatedTo("Comment")

    def add_or_update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __init__(self, **kwargs):
        self.add_or_update(**kwargs)

    def as_dict(self):
        return {
            'google_id': self.google_id,
            'email': self.email,
            'verified_email': self.verified_email,
            'name': self.name,
            'given_name': self.given_name,
            'family_name': self.family_name,
            'picture': self.picture,
            'locale': self.locale
        }

    def update(self, **kwargs):
        self.add_or_update(**kwargs)

    # List interfaces
    def add_or_update_friends(self, friends):
        for friend in friends:
            self.friends.update(friend)

    def add_or_update_friend(self, friend):
        self.friends.update(friend)

    def remove_friends(self, friends):
        for friend in friends:
            self.friends.remove(friend)

    def remove_friend(self, friend):
        self.friends.remove(friend)

    def add_or_update_friend_requests_sent(self, friends):
        for friend in friends:
            self.friend_requests_sent.update(friend)

    def add_or_update_friend_request_sent(self, friend):
        self.friend_requests_sent.update(friend)

    def remove_friend_requests_sent(self, friends):
        for friend in friends:
            self.friend_requests_sent.remove(friend)

    def remove_friend_request_sent(self, friend):
        self.friend_requests_sent.remove(friend)

    def add_or_update_friend_requests_recv(self, friends):
        for friend in friends:
            self.friend_requests_recv.update(friend)

    def add_or_update_friend_request_recv(self, friend):
        self.friend_requests_recv.update(friend)

    def remove_friend_requests_recv(self, friends):
        for friend in friends:
            self.friend_requests_recv.remove(friend)

    def remove_friend_request_recv(self, friend):
        self.friend_requests_recv.remove(friend)

    def add_or_update_followings(self, followings):
        for following in followings:
            self.followings.update(following)

    def add_or_update_following(self, following):
        self.followings.update(following)

    def remove_followings(self, followings):
        for following in followings:
            self.followings.remove(following)

    def remove_following(self, following):
        self.followings.remove(following)

    def add_or_update_followers(self, followers):
        for follower in followers:
            self.followers.update(follower)

    def add_or_update_follower(self, follower):
        self.followers.update(follower)

    def remove_followers(self, followers):
        for follower in followers:
            self.followers.remove(follower)

    def remove_follower(self, follower):
        self.followers.remove(follower)

    def add_or_update_visited_places(self, places):
        for place in places:
            self.visited.update(place)

    def add_or_update_visited_place(self, place):
        self.visited.update(place)

    def remove_visited_places(self, places):
        for place in places:
            self.visited.remove(place)

    def remove_visited_place(self, place):
        self.visited.remove(place)

    def add_or_update_posted_albums(self, albums):
        for album in albums:
            self.posted_albums.update(album)

    def add_or_update_posted_album(self, album):
        self.posted_albums.update(album)

    def remove_posted_albums(self, albums):
        for album in albums:
            self.posted_albums.remove(album)

    def remove_posted_album(self, album):
        self.posted_albums.remove(album)

    def add_or_update_posted_comments(self, comments):
        for comment in comments:
            self.posted_comments.update(comment)

    def add_or_update_posted_comment(self, comment):
        self.posted_comments.update(comment)

    def remove_posted_comments(self, comments):
        for comment in comments:
            self.posted_comments.remove(comment)

    def remove_posted_comment(self, comment):
        self.posted_comments.remove(comment)

    def clean_up(self, graph):
        """
        clean_up on person shall remove link with associalted friends,
        followings, followers and visited but not delete it.
        However since person posts albums and comments, clean_up
        on person shall clean_up and delete associated albums and comments.
        """
        # Delete albums associated with person
        if len(self.posted_albums) != 0:
            for album in self.posted_albums:
                album.clean_up()
                album.delete(graph)

        # Delete comments associated with person
        if len(self.posted_comments) != 0:
            for comment in self.posted_comments:
                comment.clean_up()
                comment.delete(graph)

    # Object level interfaces
    def save(self, graph):
        graph.push(self)

    def delete(self, graph):
        graph.delete(self)


# To avoid cyclic dependency import error
from .albumgo import Album  # noqa: E402 F401
from .commentgo import Comment  # noqa: E402 F401
from .placego import Place  # noqa: E402 F401
