#-*- coding: utf-8
import types

class Document(object):
    """A represenation of an odML document in memory"""
    
    repository = None
    
    def __init__(self, author=None, date=None, version=None, repository=None):
        self._author = author
        self._date = date # date must be a datetime
        self._version = version
        self._repository = repository
        self._sections = []

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
        
    @date.setter
    def date(self, new_value):
        self._date = types.get(new_value, "date")

    @property
    def sections(self):
        return self._sections

    def append(self, section):
        """adds the section to the section-list and makes this document the section’s parent"""
        self._sections.append (section)
        section._parent = self
        
    def __iter__(self):
        return self._sections.__iter__()

    def __repr__(self):
        return "<Doc %s by %s (%d sections)>" % (self._version, self._author, len(self._sections))
