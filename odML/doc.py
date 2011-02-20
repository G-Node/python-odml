
class Document(object):
    """A represenation of an odML document in memory"""
    def __init__(self, author=None, date=None, version=1.0):
        self._author = author
        self._date = date
        self._version = version

    @property
    def author(self):
        return self._author

    @property
    def version(self):
        return self._version

    @property
    def date(self):
        return self._date



