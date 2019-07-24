from py2neo.ogm import GraphObject, Property
from py2neo.ogm import RelatedFrom


class Place(GraphObject):
    __primarykey__ = "place_id"

    # https://developers.google.com/places/web-service/details#PlaceDetailsResults
    place_id = Property()
    timestamp = Property()

    # Set of people who visited the Place
    visitors = RelatedFrom("Person", "VISITED")

    # Set of albums of Place
    albums = RelatedFrom("Album", "ALBUMS_OF")

    def add_or_update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __init__(self, **kwargs):
        self.add_or_update(**kwargs)

    def as_dict(self):
        return {
            'place_id': self.place_id,
            'timestamp': self.timestamp
        }

    def update(self, **kwargs):
        self.add_or_update(**kwargs)

    # List interfaces
    def add_or_update_visitors(self, visitors):
        for visitor in visitors:
            self.visitors.update(visitor)

    def add_or_update_visitor(self, visitor):
        self.visitors.update(visitor)

    def remove_visitors(self, visitors):
        for visitor in visitors:
            self.visitors.remove(visitor)

    def remove_visitor(self, visitor):
        self.visitors.remove(visitor)

    def add_or_update_albums(self, albums):
        for album in albums:
            self.albums.update(album)

    def add_or_update_album(self, album):
        self.albums.update(album)

    def remove_albums(self, albums):
        for album in albums:
            self.albums.remove(album)

    def remove_album(self, album):
        self.albums.remove(album)

    def clean_up(self, graph):
        """
        clean_up on place shall remove link with associated visitors
        but not delete it.
        However since each album needs to be associated with a place,
        clean_up on place shall clean_up and delete associated albums.
        """
        # Delete albums associated with place
        if len(self.albums) != 0:
            for album in self.albums:
                album.clean_up()
                album.delete(graph)

    # Object level interfaces
    def save(self, graph):
        graph.push(self)

    def delete(self, graph):
        graph.delete(self)


# To avoid cyclic dependency import error
from .albumgo import Album  # noqa: E402 F401
from .persongo import Person  # noqa: E402 F401
