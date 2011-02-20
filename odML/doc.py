#-*- coding: utf-8
class Document(object):
    """A represenation of an odML document in memory"""
    def __init__(self, author=None, date=None, version=1.0):
        self._author = author
        self._date = date
        self._version = version
        self._sections = []

    @property
    def author(self):
        return self._author

    @property
    def version(self):
        return self._version

    @property
    def date(self):
        return self._date
        
    @property
    def sections(self):
        return self._sections

    def add_section(self, section):
        """adds the section to the section-list and makes this document the section’s parent"""
        self._sections.append (section)
        section._parent = self

    def __repr__(self):
        return "<Doc %s by %s (%d sections)>" % (self._version, self._author, len(self._sections))
