from py2neo.ogm import GraphObject, Property
from py2neo.ogm import RelatedTo, RelatedFrom


class Album(GraphObject):
    __primarykey__ = "album_id"

    # https://developers.google.com/photos/library/guides/manage-albums
    album_id = Property()
    private = Property()

    # Album posted by a Person
    poster = RelatedFrom("Person", "ALBUMS_POSTED")

    # Set of Comments posted on the Album
    comments = RelatedFrom("Comment", "COMMENT_ON")

    # Album of particular Place
    place = RelatedTo("Place")

    def add_or_update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __init__(self, **kwargs):
        self.add_or_update(**kwargs)

    def as_dict(self):
        return {
            'album_id': self.album_id,
            'private': self.private,
        }

    def update(self, **kwargs):
        self.add_or_update(**kwargs)

    # List interfaces
    def add_or_update_poster(self, poster):
        self.poster.update(poster)

    def remove_poster(self, poster):
        self.poster.remove(poster)

    def add_or_update_comments(self, comments):
        for comment in comments:
            self.comments.update(comment)

    def add_or_update_comment(self, comment):
        self.comments.update(comment)

    def remove_comments(self, comments):
        for comment in comments:
            self.comments.remove(comment)

    def remove_comment(self, comment):
        self.comments.remove(comment)

    def add_or_update_place(self, place):
        self.place.update(place)

    def remove_place(self, place):
        self.place.remove(place)

    def clean_up(self, graph):
        """
        clean_up on album shall remove link with associalted poster
        and place but not delete it.
        However since comments are associated with album, clean_up
        on album shall clean_up and delete associated comments.
        """
        # Delete comments associated with album
        if len(self.comments) != 0:
            for comment in self.comments:
                comment.clean_up()
                comment.delete(graph)

    # Object level interfaces
    def save(self, graph):
        graph.push(self)

    def delete(self, graph):
        graph.delete(self)


# To avoid cyclic dependency import error
from .commentgo import Comment  # noqa: E402 F401
from .placego import Place  # noqa: E402 F401
from .persongo import Person  # noqa: E402 F401
