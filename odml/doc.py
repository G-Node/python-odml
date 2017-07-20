# -*- coding: utf-8
import uuid

import odml.base as base
import odml.dtypes as dtypes
import odml.format as format
import odml.terminology as terminology
from odml.tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class Document(base._baseobj):
    pass


@allow_inherit_docstring
class BaseDocument(base.sectionable, Document):
    """
    A represenation of an odML document in memory.
    Its odml attributes are: *author*, *date*, *version* and *repository*.
    A Document behaves very much like a section, except that it cannot hold
    properties.
    """

    _format = format.Document

    def __init__(self, author=None, date=None, version=None, repository=None):
        super(BaseDocument, self).__init__()
        self._id = str(uuid.uuid4())
        self._author = author
        self._date = date  # date must be a datetime
        self._version = version
        self._repository = repository

    @property
    def id(self):
        """
        The uuid for the document.
        """
        return self._id

    @property
    def author(self):
        """
        The author of the document.
        """
        return self._author

    @author.setter
    def author(self, new_value):
        self._author = new_value

    @property
    def version(self):
        """
        A personal version-specifier that can be used to track different
        versions of the same document.
        """
        return self._version

    @version.setter
    def version(self, new_value):
        self._version = new_value

    @property
    def date(self):
        """
        The date the document was created.
        """
        return dtypes.set(self._date, "date")

    @date.setter
    def date(self, new_value):
        self._date = dtypes.get(new_value, "date")

    @property
    def parent(self):
        """ The parent of a document is always None. """
        return None

    def __repr__(self):
        return "<Doc %s by %s (%d sections)>" % (self._version,
                                                 self._author,
                                                 len(self._sections))

    def finalize(self):
        """
        This needs to be called after the document is set up from parsing
        it will perform additional operations, that need the complete document.
        In particular, this method will resolve all *link* and *include*
        attributes accordingly.
        """
        # We could not fill out links while parsing (referenced sections where
        # not known), so try to set them now, where the document is complete

        for sec in self.itersections(recursive=True):
            if sec._link is not None:
                sec.link = sec._link
            if sec._include is not None:
                sec.include = sec._include

    @inherit_docstring
    def get_terminology_equivalent(self):
        if self.repository is None:
            return None
        term = terminology.load(self.repository)
        return term