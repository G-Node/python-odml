# -*- coding: utf-8
"""
This module provides the Base Document class.
"""
import uuid

from . import base
from . import dtypes
from . import format as fmt
from . import terminology
from . import validation
from .tools.doc_inherit import inherit_docstring, allow_inherit_docstring


@allow_inherit_docstring
class BaseDocument(base.Sectionable):
    """
    A representation of an odML document in memory.
    Its odml attributes are: *author*, *date*, *version* and *repository*.
    A Document behaves very much like a section, except that it cannot hold
    properties.
    """

    _format = fmt.Document

    def __init__(self, author=None, date=None, version=None, repository=None, oid=None):
        super(BaseDocument, self).__init__()
        try:
            if oid is not None:
                self._id = str(uuid.UUID(oid))
            else:
                self._id = str(uuid.uuid4())
        except ValueError as exc:
            print(exc)
            self._id = str(uuid.uuid4())
        self._author = author
        self._version = version
        self._repository = repository

        # Make sure date is properly parsed into a datetime object
        self._date = None
        self.date = date

        # Enable setting of the file name from whence this document came.
        # It is for knowing while processing and will not be serialized to a file.
        self._origin_file_name = None

    def __repr__(self):
        return "Document %s {author = %s, %d sections}" % \
               (self._version, self._author, len(self._sections))

    @property
    def oid(self):
        """
        The uuid for the document. Required for entity creation and comparison,
        saving and loading.
        """
        return self.id

    @property
    def id(self):
        """
        The uuid for the document.
        """
        return self._id

    def new_id(self, oid=None):
        """
        new_id sets the id of the current object to a RFC 4122 compliant UUID.
        If an id was provided, it is assigned if it is RFC 4122 UUID format compliant.
        If no id was provided, a new UUID is generated and assigned.
        :param oid: UUID string as specified in RFC 4122.
        """
        if oid is not None:
            self._id = str(uuid.UUID(oid))
        else:
            self._id = str(uuid.uuid4())

    @property
    def author(self):
        """
        The author of the document.
        """
        return self._author

    @author.setter
    def author(self, new_value):
        if new_value == "":
            new_value = None
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
        if new_value == "":
            new_value = None
        self._version = new_value

    @property
    def date(self):
        """
        The date the document was created.
        """
        return self._date

    @date.setter
    def date(self, new_value):
        if not new_value:
            new_value = None
        else:
            new_value = dtypes.date_set(new_value)
        self._date = new_value

    @property
    def parent(self):
        """ The parent of a document is always None. """
        return None

    @property
    def origin_file_name(self):
        """
        If available, the file name from where the document has been loaded.
        Will not be serialized to file when saving the document.
        """
        return self._origin_file_name

    @origin_file_name.setter
    def origin_file_name(self, new_value):
        if not new_value:
            new_value = None
        self._origin_file_name = new_value

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

    def validate(self):
        """
        Runs a validation on itself and returns the Validation object.

        :return: odml.Validation
        """
        return validation.Validation(self)

    @inherit_docstring
    def get_terminology_equivalent(self):
        if self.repository is None:
            return None
        term = terminology.load(self.repository)
        return term

    def pprint(self, indent=2, max_depth=1, max_length=80, current_depth=0):
        """
        Pretty print method to visualize Document-Section trees.

        :param indent: number of leading spaces for every child Section or Property.
        :param max_depth: maximum number of hierarchical levels printed from the
                              starting Section.
        :param max_length: maximum number of characters printed in one line.
        :param current_depth: number of hierarchical levels printed from the
                              starting Section.
        """
        annotation = "{} [{}] {}".format(self.author, self.version, self.date)
        sec_num = "sections: {}".format(len(self._sections))
        repo = "repository: {}".format(self.repository)
        doc_str = "[{}, {}, {}]".format(annotation, sec_num, repo)
        print(doc_str)

        for sec in self._sections:
            sec.pprint(current_depth=current_depth+1, max_depth=max_depth,
                       indent=indent, max_length=max_length)
