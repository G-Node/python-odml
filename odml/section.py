# -*- coding: utf-8
import collections
import uuid

from . import base
from . import format
from . import terminology
from .doc import BaseDocument
# this is supposedly ok, as we only use it for an isinstance check
from .property import BaseProperty
# it MUST however not be used to create any Property objects
from .tools.doc_inherit import inherit_docstring, allow_inherit_docstring


@allow_inherit_docstring
class BaseSection(base.Sectionable):
    """ An odML Section """
    type = None
    reference = None  # the *import* property
    _link = None
    _include = None
    _merged = None

    _format = format.Section

    def __init__(self, name=None, type=None, parent=None,
                 definition=None, reference=None,
                 repository=None, link=None, include=None, oid=None):

        # Sets _sections Smartlist and _repository to None, so run first.
        super(BaseSection, self).__init__()
        self._props = base.SmartList(BaseProperty)

        try:
            if oid is not None:
                self._id = str(uuid.UUID(oid))
            else:
                self._id = str(uuid.uuid4())
        except ValueError as e:
            print(e)
            self._id = str(uuid.uuid4())

        # Use id if no name was provided.
        if not name:
            name = self._id

        self._parent = None
        self._name = name
        self._definition = definition
        self._reference = reference
        self._repository = repository
        self._link = link
        self._include = include

        # this may fire a change event, so have the section setup then
        self.type = type
        self.parent = parent

    def __repr__(self):
        return "<Section %s[%s] (%d)>" % (self._name, self.type, len(self._sections))

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

    @property
    def oid(self):
        """
        The uuid for the section. Required for entity creation and comparison,
        saving and loading.
        """
        return self.id

    @property
    def id(self):
        """
        The uuid for the section.
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
    def name(self):
        return self._name

    @name.setter
    def name(self, new_value):
        if self.name == new_value:
            return

        curr_parent = self.parent
        if hasattr(curr_parent, "sections") and new_value in curr_parent.sections:
            raise KeyError("Object with the same name already exists!")

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

        # strict needs to be False, otherwise finalizing a document will
        # basically always fail.
        self.merge(new_section, strict=False)

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

        # strict needs to be False, otherwise finalizing a document will
        # basically always fail.
        self.merge(new_section, strict=False)

    @property
    def definition(self):
        """ Name Definition of the section """
        if hasattr(self, "_definition"):
            return self._definition
        else:
            return None

    @definition.setter
    def definition(self, new_value):
        if new_value == "":
            new_value = None
        self._definition = new_value

    @definition.deleter
    def definition(self):
        del self._definition

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, new_value):
        if new_value == "":
            new_value = None
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

    @base.Sectionable.repository.setter
    def repository(self, url):
        base.Sectionable.repository.fset(self, url)

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

    def append(self, obj):
        """
        Method adds single Sections and Properties to the respective child-lists
        of the current Section.

        :param obj: Section or Property object.
        """
        if isinstance(obj, BaseSection):
            self._sections.append(obj)
            obj._parent = self
        elif isinstance(obj, BaseProperty):
            self._props.append(obj)
            obj._parent = self
        elif isinstance(obj, collections.Iterable) and not isinstance(obj, str):
            raise ValueError("odml.Section.append: "
                             "Use extend to add a list of Sections or Properties.")
        else:
            raise ValueError("odml.Section.append: "
                             "Can only append Sections or Properties.")

    def extend(self, obj_list):
        """
        Method adds Sections and Properties to the respective child-lists
        of the current Section.

        :param obj_list: Iterable containing Section and Property entries.
        """
        if not isinstance(obj_list, collections.Iterable):
            raise TypeError("'%s' object is not iterable" % type(obj_list).__name__)

        # Make sure only Sections and Properties with unique names will be added.
        for obj in obj_list:
            if not isinstance(obj, BaseSection) and not isinstance(obj, BaseProperty):
                raise ValueError("odml.Section.extend: "
                                 "Can only extend sections and properties.")

            elif isinstance(obj, BaseSection) and obj.name in self.sections:
                raise KeyError("odml.Section.extend: "
                               "Section with name '%s' already exists." % obj.name)

            elif isinstance(obj, BaseProperty) and obj.name in self.properties:
                raise KeyError("odml.Section.extend: "
                               "Property with name '%s' already exists." % obj.name)

        for obj in obj_list:
            self.append(obj)

    def insert(self, position, obj):
        """
        Insert a Section or a Property at the respective child-list position.
        A ValueError will be raised, if a Section or a Property with the same
        name already exists in the respective child-list.

        :param position: index at which the object should be inserted.
        :param obj: Section or Property object.
        """
        if isinstance(obj, BaseSection):
            if obj.name in self.sections:
                raise ValueError("odml.Section.insert: "
                                 "Section with name '%s' already exists." % obj.name)

            self._sections.insert(position, obj)
            obj._parent = self
        elif isinstance(obj, BaseProperty):
            if obj.name in self.properties:
                raise ValueError("odml.Section.insert: "
                                 "Property with name '%s' already exists." % obj.name)

            self._props.insert(position, obj)
            obj._parent = self
        else:
            raise ValueError("Can only insert sections and properties")

    def remove(self, obj):
        """
        Remove a Section or a Property from the respective child-lists of the current
        Section and sets the parent attribute of the handed in object to None.
        Raises a ValueError if the object is not a Section or a Property or if
        the object is not contained in the child-lists.

        :param obj: Section or Property object.
        """
        if isinstance(obj, BaseSection):
            self._sections.remove(obj)
            obj._parent = None
        elif isinstance(obj, BaseProperty):
            self._props.remove(obj)
            obj._parent = None
        else:
            raise ValueError("Can only remove sections and properties")

    def clone(self, children=True):
        """
        Clone this object recursively allowing to copy it independently
        to another document
        """
        obj = super(BaseSection, self).clone(children)
        obj._id = str(uuid.uuid4())

        obj._props = base.SmartList(BaseProperty)
        if children:
            for p in self._props:
                obj.append(p.clone())

        return obj

    def contains(self, obj):
        """
        If the child-lists of the current Section contain a Section with
        the same *name* and *type* or a Property with the same *name* as
        the provided object, the found Section or Property is returned.

        :param obj: Section or Property object.
        """
        if isinstance(obj, BaseSection):
            return super(BaseSection, self).contains(obj)

        elif isinstance(obj, BaseProperty):
            for i in self._props:
                if obj.name == i.name:
                    return i
        else:
            raise ValueError("odml.Section.contains:"
                             "Section or Property object expected.")

    def merge_check(self, source_section, strict=True):
        """
        Recursively checks whether a source Section and all its children can be merged
        with self and all its children as destination and raises a ValueError if any of
        the Section attributes definition and reference differ in source and destination.

        :param source_section: an odML Section.
        :param strict: If True, definition and reference attributes of any merged Sections
                       as well as most attributes of merged Properties on the same
                       tree level in source and destination have to be identical.
        """
        if strict and self.definition is not None and source_section.definition is not None:
            self_def = ''.join(map(str.strip, self.definition.split())).lower()
            other_def = ''.join(map(str.strip, source_section.definition.split())).lower()
            if self_def != other_def:
                raise ValueError(
                    "odml.Section.merge: src and dest definitions do not match!")

        if strict and self.reference is not None and source_section.reference is not None:
            self_ref = ''.join(map(str.strip, self.reference.lower().split()))
            other_ref = ''.join(map(str.strip, source_section.reference.lower().split()))
            if self_ref != other_ref:
                raise ValueError(
                    "odml.Section.merge: src and dest references are in conflict!")

        # Check all the way down the rabbit hole / Section tree.
        for obj in source_section:
            mine = self.contains(obj)
            if mine is not None:
                mine.merge_check(obj, strict)

    def merge(self, section=None, strict=True):
        """
        Merges this section with another *section*.
        See also: :py:attr:`odml.section.BaseSection.link`
        If section is none, sets the link/include attribute (if _link or
        _include are set), causing the section to be automatically merged
        to the referenced section.

        :param section: an odML Section. If section is None, *link* or *include*
                        will be resolved instead.
        :param strict: Bool value to indicate whether the attributes of affected
                       child Properties except their ids and values have to be identical
                       to be merged. Default is True.
        """
        if section is None:
            # for the high level interface
            if self._link is not None:
                self.link = self._link
            elif self._include is not None:
                self.include = self._include
            return

        # Check all the way down the tree if the destination source and
        # its children can be merged with self and its children since
        # there is no rollback in case of a downstream merge error.
        self.merge_check(section, strict)

        if self.definition is None and section.definition is not None:
            self.definition = section.definition
        if self.reference is None and section.reference is not None:
            self.reference = section.reference

        for obj in section:
            mine = self.contains(obj)
            if mine is not None:
                mine.merge(obj, strict)
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

    def _reorder(self, childlist, new_index):
        l = childlist
        old_index = l.index(self)

        # 2 cases: insert after old_index / insert before
        if new_index > old_index:
            new_index += 1
        l.insert(new_index, self)
        if new_index < old_index:
            del l[old_index + 1]
        else:
            del l[old_index]
        return old_index

    def reorder(self, new_index):
        """
        Move this object in its parent child-list to the position *new_index*.

        :return: The old index at which the object was found.
        """
        if not self.parent:
            raise ValueError("odml.Section.reorder: "
                             "Section has no parent, cannot reorder in parent list.")

        return self._reorder(self.parent.sections, new_index)
