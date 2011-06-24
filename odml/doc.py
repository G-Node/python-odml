#-*- coding: utf-8
import types
import base
import format

class Document(base.sectionable):
    """A represenation of an odML document in memory"""

    repository = None

    _format = format.Document

    def __init__(self, author=None, date=None, version=None, repository=None):
        self._author = author
        self._date = date # date must be a datetime
        self._version = version
        self._repository = repository
        super(BaseDocument, self).__init__()

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, new_value):
        self._author = new_value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, new_value):
        self._version = new_value

    @property
    def date(self):
        return types.set(self._date, "date")

    @property
    def parent(self):
        return None

    @date.setter
    def date(self, new_value):
        self._date = types.get(new_value, "date")

    def __repr__(self):
        return "<Doc %s by %s (%d sections)>" % (self._version, self._author, len(self._sections))

BaseDocument = Document
