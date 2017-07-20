# -*- coding: utf-8
import uuid

import odml.base as base
import odml.format as format
import odml.terminology as terminology
from odml.doc import BaseDocument
# this is supposedly ok, as we only use it for an isinstance check
from odml.property import Property
# it MUST however not be used to create any Property objects
from odml.tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class Section(base._baseobj):
    pass


@allow_inherit_docstring
class BaseSection(base.sectionable, Section):
    """ An odML Section """
    type = None
    # id = None
    _link = None
    _include = None
    reference = None  # the *import* property

    _merged = None

    _format = format.Section

    def __init__(self, name, type=None, parent=None,
                 definition=None, reference=None):
        self._id = str(uuid.uuid4())
        self._parent = None
        self._name = name
        self._props = base.SmartList()
        self._definition = definition
        self._reference = reference
        super(BaseSection, self).__init__()
        # this may fire a change event, so have the section setup then
        self.type = type
        self.parent = parent

    def __repr__(self):
        return "<Section %s[%s] (%d)>" % (self._name, self.type,
                                          len(self._sections))

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_value):
        self._name = new_value

    @property
    def include(self):
        """
        The same as :py:attr:`odml.section.BaseSection.link`, except that
        include specifies an arbitrary url instead of a local path within
        the same document
        """
        return self._include

    @include.setter
    def include(self, new_value):
        if self._link is not None:
            raise TypeError("%s.include: You can either set link or include, "
                            "but not both." % repr(self))

        if not new_value:
            self._include = None
            self.clean()
            return

        if '#' in new_value:
            url, path = new_value.split('#', 1)
        else:
            url, path = new_value, None

        terminology.deferred_load(url)

        if self.parent is None:
            self._include = new_value
            return

        term = terminology.load(url)
        new_section = term.get_section_by_path(
            path) if path is not None else term.sections[0]

        if self._include is not None:
            self.clean()
        self._include = new_value
        self.merge(new_section)

    @property
    def link(self):
        """
        Specifies a softlink, i.e. a path within the document
        When the merge()-method is called, the link will be resolved creating
        according copies of the section referenced by the link attribute.
        When the unmerge() method is called (happens when running clean())
        the link is unresolved, i.e. all properties and sections that are
        completely equivalent to the merged object will be removed.
        (They will be restored accordingly when calling merge()).
        When changing the *link* attribute, the previously merged section is
        unmerged, and the new reference will be immediately resolved. To avoid
        this side-effect, directly change the *_link* attribute.
        """
        return self._link

    @link.setter
    def link(self, new_value):
        if self._include is not None:
            raise TypeError("%s.link: You can either set link or include,"
                            " but not both." % repr(self))

        if self.parent is None:  # we cannot possibly know where the link goes
            self._link = new_value
            return

        if not new_value:
            self._link = None
            self.clean()
            return

        # raises exception if path cannot be found
        new_section = self.get_section_by_path(new_value)
        if self._link is not None:
            self.clean()
        self._link = new_value
        self.merge(new_section)

    @property
    def definition(self):
        """ Name Definition of the section """
        if hasattr(self, "_definition"):
            return self._definition
        else:
            return None

    @definition.setter
    def definition(self, val):
        self._definition = val

    @definition.deleter
    def definition(self):
        del self._definition

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, new_value):
        self._reference = new_value

    # API (public)
    #
    #  properties
    @property
    def properties(self):
        """ The list of all properties contained in this section """
        return self._props

    @property
    def sections(self):
        """ The list of all child-sections of this section """
        return self._sections

    @property
    def parent(self):
        """ The parent section, the parent document or None """
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if new_parent is None and self._parent is None:
            return
        elif new_parent is None and self._parent is not None:
            self._parent.remove(self)
            self._parent = None
        elif self._validate_parent(new_parent):
            if self._parent is not None:
                self._parent.remove(self)
            self._parent = new_parent
            self._parent.append(self)
        else:
            raise ValueError(
                "odml.Section.parent: passed value is not of consistent type!"
                "\nodml.Document or odml.Section expected")

    def _validate_parent(self, new_parent):
        if isinstance(new_parent, BaseDocument) or \
           isinstance(new_parent, BaseSection):
            return True
        return False

    def get_repository(self):
        """
        Returns the repository responsible for this section,
        which might not be the *repository* attribute, but may
        be inherited from a parent section / the document
        """
        if self._repository is None and self.parent is not None:
            return self.parent.get_repository()
        return super(BaseSection, self).repository

    @base.sectionable.repository.setter
    def repository(self, url):
        base.sectionable.repository.fset(self, url)

    @inherit_docstring
    def get_terminology_equivalent(self):
        repo = self.get_repository()
        if repo is None:
            return None
        term = terminology.load(repo)
        if term is None:
            return None
        return term.find_related(type=self.type)

    def get_merged_equivalent(self):
        """
        Return the merged object or None
        """
        return self._merged

    def __append(self, obj):
        """
        Append a Section or Property
        """
        if isinstance(obj, Section):
            self._sections.append(obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.append(obj)
            obj._parent = self
        else:
            raise ValueError("Can only append sections and properties")

    def append(self, *obj_tuple):
        """
        Append Sections or Properties
        """
        for obj in obj_tuple:
            self.__append(obj)

    def insert(self, position, obj):
        """
        Insert a Section or Property at the respective position
        """
        if isinstance(obj, Section):
            self._sections.insert(position, obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.insert(position, obj)
            obj._section = self
        else:
            raise ValueError("Can only insert sections and properties")

    def remove(self, obj):
        # TODO make sure this is not compare based
        if isinstance(obj, Section):
            self._sections.remove(obj)
            obj._parent = None
        elif isinstance(obj, Property):
            self._props.remove(obj)
            obj._section = None
        else:
            raise ValueError("Can only remove sections and properties")

    def __iter__(self):
        """
        Iterate over each section and property contained in this section
        """
        for section in self._sections:
            yield section
        for prop in self._props:
            yield prop

    def __len__(self):
        """
        Number of children (sections AND properties)
        """
        return len(self._sections) + len(self._props)

    def clone(self, children=True):
        """
        Clone this object recursively allowing to copy it independently
        to another document
        """
        obj = super(BaseSection, self).clone(children)

        obj._props = base.SmartList()
        if children:
            for p in self._props:
                obj.append(p.clone())

        return obj

    def contains(self, obj):
        """
        Finds a property or section with the same name&type properties or None
        """
        if isinstance(obj, Section):
            return super(BaseSection, self).contains(obj)
        for i in self._props:
            if obj.name == i.name:
                return i

    def merge(self, section=None):
        """
        Merges this section with another *section*
        See also: :py:attr:`odml.section.BaseSection.link`
        If section is none, sets the link/include attribute (if _link or
        _include are set), causing the section to be automatically merged
        to the referenced section.
        """
        if section is None:
            # for the high level interface
            if self._link is not None:
                self.link = self._link
            elif self._include is not None:
                self.include = self._include
            return

        for obj in section:
            mine = self.contains(obj)
            if mine is not None:
                mine.merge(obj)
            else:
                mine = obj.clone()
                mine._merged = obj
                self.append(mine)
        self._merged = section

    @inherit_docstring
    def clean(self):
        if self._merged is not None:
            self.unmerge(self._merged)
        super(BaseSection, self).clean()

    def unmerge(self, section):
        """
        Clean up a merged section by removing objects that are totally equal
        to the linked object
        """
        if self == section:
            raise RuntimeError("cannot unmerge myself?")
        removals = []
        for obj in section:
            mine = self.contains(obj)
            if mine is None:
                continue
            if mine == obj:
                removals.append(mine)
            else:
                mine.unmerge(obj)
        for obj in removals:
            self.remove(obj)

        # The path may not be valid anymore, so make sure to update it
        # however this does not reflect changes happening while the section
        # is unmerged
        if self._link is not None:
            # TODO get_absolute_path, # TODO don't change if the section can
            # still be reached using the old link
            self._link = self.get_relative_path(section)

        self._merged = None

    @property
    def is_merged(self):
        """
        Returns True if the section is merged with another one (e.g. through
        :py:attr:`odml.section.BaseSection.link` or
        :py:attr:`odml.section.BaseSection.include`)
        The merged object can be accessed through the *_merged* attribute.
        """
        return self._merged is not None

    @property
    def can_be_merged(self):
        """
        Returns True if either a *link* or an *include* attribute is specified
        """
        return self._link is not None or self._include is not None