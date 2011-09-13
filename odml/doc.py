#-*- coding: utf-8
import types
import base
import format
import terminology

class Document(base.sectionable):
    """A represenation of an odML document in memory"""

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

    def finalize(self):
        """
        This needs to be called after the document is set up from parsing
        it will perform additional operations, that need the complete document
        """
        # we could not fill out links while parsing (referenced sections where not known),
        # so try to set them now, where the document is complete
        for sec in self.itersections(recursive=True):
            if sec._link is not None:
                sec.link = sec._link

    def get_terminology_equivalent(self):
        if self.repository is None: return None
        term = terminology.load(self.repository)
        return term

BaseDocument = Document
