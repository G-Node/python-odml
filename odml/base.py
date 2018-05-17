# -*- coding: utf-8
"""
Collects common base functionality
"""
import collections
import posixpath

from . import terminology
from .tools.doc_inherit import allow_inherit_docstring


class BaseObject(object):
    _format = None

    def __hash__(self):
        """
        Allow all odML objects to be hash-able.
        """
        return id(self)

    def __eq__(self, obj):
        """
        Do a deep comparison of this object and its odml properties.
        The 'id' attribute of an object is excluded, since it is
        unique within a document.
        """
        # cannot compare totally different stuff
        if not isinstance(self, obj.__class__):
            return False

        for key in self._format:
            if key == "id" or key == "oid":
                continue
            elif getattr(self, key) != getattr(obj, key):
                return False

        return True

    def __ne__(self, obj):
        """
        Use the __eq__ function to determine if both objects are equal
        """
        return not self == obj

    def format(self):
        return self._format

    @property
    def document(self):
        """ Returns the Document object in which this object is contained """
        if self.parent is None:
            return None
        return self.parent.document

    def get_terminology_equivalent(self):
        """
        Returns the equivalent object in an terminology (should there be one
        defined) or None
        """
        return None

    def clean(self):
        """
        Stub that doesn't do anything for this class
        """
        pass

    def clone(self, children=True):
        """
        Clone this object recursively (if children is True) allowing to copy it
        independently to another document. If children is False, this acts as
        a template cloner, creating a copy of the object without any children
        """
        # TODO don't we need some recursion / deepcopy here?
        import copy
        obj = copy.copy(self)
        return obj


class SmartList(list):

    def __init__(self, content_type):
        """
        Only values of the instance *content_type* can be added to the SmartList.
        """
        self._content_type = content_type
        super(SmartList, self).__init__()

    def __getitem__(self, key):
        """
        Provides element index also by searching for an element with a given name.
        """
        # Try normal list index first (for integers)
        if isinstance(key, int):
            return super(SmartList, self).__getitem__(key)

        # Otherwise search the list
        for obj in self:
            if (hasattr(obj, "name") and obj.name == key) or key == obj:
                return obj

        # and fail eventually
        raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Replaces item at list[*key*] with *value*.
        :param key: index position
        :param value: object that replaces item at *key* position.
                      value has to be of the same content type as the list.
                      In this context usually a Section or a Property.
        """
        if not isinstance(value, self._content_type):
            raise ValueError("List only supports elements of type '%s'" %
                             self._content_type)

        # If required remove new object from its old parents child-list
        if hasattr(value, "_parent") and (value._parent and value in value._parent):
            value._parent.remove(value)

        # If required move parent reference from replaced to new object
        # and set parent reference on replaced object None.
        if hasattr(self[key], "_parent"):
            value._parent = self[key]._parent
            self[key]._parent = None

        super(SmartList, self).__setitem__(key, value)

    def __contains__(self, key):
        for obj in self:
            if (hasattr(obj, "name") and obj.name == key) or key == obj:
                return True

    def index(self, obj):
        """
        Find obj in list
        """
        for i, e in enumerate(self):
            if e is obj:
                return i
        raise ValueError("remove: %s not in list" % repr(obj))

    def remove(self, obj):
        """
        Remove an element from this list.
        """
        del self[self.index(obj)]

    def append(self, *obj_tuple):
        for obj in obj_tuple:
            if obj.name in self:
                raise KeyError(
                    "Object with the same name already exists! " + str(obj))

            if not isinstance(obj, self._content_type):
                raise ValueError("List only supports elements of type '%s'" %
                                 self._content_type)

            super(SmartList, self).append(obj)


@allow_inherit_docstring
class Sectionable(BaseObject):
    def __init__(self):
        from odml.section import BaseSection
        self._sections = SmartList(BaseSection)
        self._repository = None

    def __getitem__(self, key):
        return self._sections[key]

    def __len__(self):
        return len(self._sections)

    def __iter__(self):
        return self._sections.__iter__()

    @property
    def document(self):
        """
        Returns the parent-most node (if its a document instance) or None
        """
        from odml.doc import BaseDocument
        p = self
        while p.parent:
            p = p.parent
        if isinstance(p, BaseDocument):
            return p

    @property
    def sections(self):
        """ The list of sections contained in this section/document """
        return self._sections

    def insert(self, position, section):
        """
        Insert a Section at the child-list position. A ValueError will be raised,
        if a Section with the same name already exists in the child-list.

        :param position: index at which the object should be inserted.
        :param section: odML Section object.
        """
        from odml.section import BaseSection
        if isinstance(section, BaseSection):
            if section.name in self._sections:
                raise ValueError("Section with name '%s' already exists." % section.name)

            self._sections.insert(position, section)
            section._parent = self
        else:
            raise ValueError("Can only insert objects of type Section.")

    def append(self, section):
        """
        Method appends a single Section to the section child-lists of the current Object.

        :param section: odML Section object.
        """
        from odml.section import BaseSection
        if isinstance(section, BaseSection):
            self._sections.append(section)
            section._parent = self
        elif isinstance(section, collections.Iterable) and not isinstance(section, str):
            raise ValueError("Use extend to add a list of Sections.")
        else:
            raise ValueError("Can only append objects of type Section.")

    def extend(self, sec_list):
        """
        Method adds Sections to the section child-list of the current object.

        :param sec_list: Iterable containing odML Section entries.
        """
        from odml.section import BaseSection
        if not isinstance(sec_list, collections.Iterable):
            raise TypeError("'%s' object is not iterable" % type(sec_list).__name__)

        # Make sure only Sections with unique names will be added.
        for sec in sec_list:
            if not isinstance(sec, BaseSection):
                raise ValueError("Can only extend objects of type Section.")

            elif isinstance(sec, BaseSection) and sec.name in self._sections:
                raise KeyError("Section with name '%s' already exists." % sec.name)

        for sec in sec_list:
            self.append(sec)

    def remove(self, section):
        """ Removes the specified child-section """
        self._sections.remove(section)
        section._parent = None

    def itersections(self, recursive=True, yield_self=False,
                     filter_func=lambda x: True, max_depth=None):
        """
        Iterate each child section

        Example: return all subsections which name contains "foo"
        >>> filter_func = lambda x: getattr(x, 'name').find("foo") > -1
        >>> sec_or_doc.itersections(filter_func=filter_func)

        :param recursive: iterate all child sections recursively (deprecated)
        :type recursive: bool

        :param yield_self: includes itself in the iteration
        :type yield_self: bool

        :param filter_func: accepts a function that will be applied to each
                            iterable. Yields iterable if function returns True
        :type filter_func: function
        """
        stack = []
        # Below: never yield self if self is a Document
        if self == self.document and ((max_depth is None) or (max_depth > 0)):
            for sec in self.sections:
                stack.append((sec, 1))  # (<section>, <level in a tree>)
        elif self != self.document:
            stack.append((self, 0))  # (<section>, <level in a tree>)

        while len(stack) > 0:
            (sec, level) = stack.pop(0)
            if filter_func(sec) and (yield_self if level == 0 else True):
                yield sec

            if max_depth is None or level < max_depth:
                for sec in sec.sections:
                    stack.append((sec, level + 1))

    def iterproperties(self, max_depth=None, filter_func=lambda x: True):
        """
        Iterate each related property (recursively)

        Example: return all children properties which name contains "foo"
        >>> filter_func = lambda x: getattr(x, 'name').find("foo") > -1
        >>> sec_or_doc.iterproperties(filter_func=filter_func)

        :param max_depth: iterate all properties recursively if None, only to
                          a certain level otherwise
        :type max_depth: bool

        :param filter_func: accepts a function that will be applied to each
                            iterable. Yields iterable if function returns True
        :type filter_func: function
        """
        for sec in [s for s in self.itersections(max_depth=max_depth,
                                                 yield_self=True)]:
            if hasattr(sec, "properties"):  # not to fail if odml.Document
                for i in sec.properties:
                    if filter_func(i):
                        yield i

    def itervalues(self, max_depth=None, filter_func=lambda x: True):
        """
        Iterate each related value (recursively)

        # Example: return all children values which string converted version
                   has "foo"
        >>> filter_func = lambda x: str(x).find("foo") > -1
        >>> sec_or_doc.itervalues(filter_func=filter_func)

        :param max_depth: iterate all properties recursively if None, only to
                          a certain level otherwise
        :type max_depth: bool

        :param filter_func: accepts a function that will be applied to each
                            iterable. Yields iterable if function returns True
        :type filter_func: function
        """
        for prop in [p for p in self.iterproperties(max_depth=max_depth)]:
            if filter_func(prop.value):
                yield prop.value

    def contains(self, obj):
        """
        Checks if a subsection of name&type of *obj* is a child of this section
        if so return this child
        """
        for i in self._sections:
            if obj.name == i.name and obj.type == i.type:
                return i

    def _matches(self, obj, key=None, otype=None, include_subtype=False):
        """
        Find out
        * if the *key* matches obj.name (if key is not None)
        * or if *otype* matches obj.type (if type is not None)
        * if type does not match exactly, test for subtype.
        (e.g.stimulus/white_noise)
        comparisons are case-insensitive, however both key and type
        MUST be lower-case.
        """
        name_match = (key is None or (
            key is not None and hasattr(obj, "name") and obj.name == key))

        exact_type_match = (otype is None or (otype is not None and
                                              hasattr(obj, "type") and
                                              obj.type.lower() == otype))

        if not include_subtype:
            return name_match and exact_type_match

        subtype_match = (otype is None or
                         (otype is not None and hasattr(obj, "type") and
                          otype in obj.type.lower().split('/')[:-1]))

        return name_match and (exact_type_match or subtype_match)

    def get_section_by_path(self, path):
        """
        Find a Section through a path like "../name1/name2"

        :param path: path like "../name1/name2"
        :type path: str
        """
        return self._get_section_by_path(path)

    def get_property_by_path(self, path):
        """
        Find a Property through a path like "../name1/name2:property_name"

        :param path: path like "../name1/name2:property_name"
        :type path: str
        """
        laststep = path.split(":")  # assuming section names do not contain :
        found = self._get_section_by_path(laststep[0])
        return self._match_iterable(found.properties, ":".join(laststep[1:]))

    def _match_iterable(self, iterable, key):
        """
        Searches for a key match within a given iterable.
        Raises ValueError if not found.
        """
        for obj in iterable:
            if self._matches(obj, key):
                return obj
        raise ValueError("Object named '%s' does not exist" % key)

    def _get_section_by_path(self, path):
        """
        Returns a Section by a given path.
        Raises ValueError if not found.
        """
        if path.startswith("/"):
            if len(path) == 1:
                raise ValueError("Not a valid path")
            doc = self.document
            if doc is not None:
                return doc._get_section_by_path(path[1:])
            raise ValueError(
                "A section with no Document cannot resolve absolute path")

        pathlist = path.split("/")
        if len(pathlist) > 1:
            if pathlist[0] == "..":
                found = self.parent
            elif pathlist[0] == ".":
                found = self
            else:
                found = self._match_iterable(self.sections, pathlist[0])

            if found:
                return found._get_section_by_path("/".join(pathlist[1:]))
            raise ValueError("Section named '%s' does not exist" % pathlist[0])
        else:
            return self._match_iterable(self.sections, pathlist[0])

    def find(self, key=None, type=None, findAll=False, include_subtype=False):
        """ Return the first subsection named *key* of type *type* """
        ret = []
        if type:
            type = type.lower()

        for s in self._sections:
            if self._matches(s, key, type, include_subtype=include_subtype):
                if findAll:
                    ret.append(s)
                else:
                    return s
        if ret:
            return ret

    def find_related(self, key=None, type=None, children=True, siblings=True,
                     parents=True, recursive=True, findAll=False):
        """
        Finds a related section named *key* and/or *type*

          * by searching its children’s children if *children* is True
            if *recursive* is true all leave nodes will be searched
          * by searching its siblings if *siblings* is True
          * by searching the parent element if *parents* is True
            if *recursive* is True all parent nodes until the root are searched
          * if *findAll* is True, returns a list of all matching objects
        """
        ret = []
        if type:
            type = type.lower()

        if children:
            for section in self._sections:
                if self._matches(section, key, type):
                    if findAll:
                        ret.append(section)
                    else:
                        return section

                if recursive:
                    obj = section.find_related(key, type, children,
                                               siblings=False, parents=False,
                                               recursive=recursive,
                                               findAll=findAll)
                    if obj is not None:
                        if findAll:
                            ret += obj
                        else:
                            return obj

        if siblings and self.parent is not None:
            obj = self.parent.find(key, type, findAll)
            if obj is not None:
                if findAll:
                    ret += obj
                else:
                    return obj

        if parents:
            obj = self
            while obj.parent is not None:
                obj = obj.parent
                if self._matches(obj, key, type):
                    if findAll:
                        ret.append(obj)
                    else:
                        return obj
                if not recursive:
                    break

        if ret:
            return ret
        return None

    def get_path(self):
        """
        Returns the absolute path of this section
        """
        node = self
        path = []
        while node.parent is not None:
            path.insert(0, node.name)
            node = node.parent
        return "/" + "/".join(path)

    @staticmethod
    def _get_relative_path(a, b):
        """
        Returns a relative path for navigation from dir *a* to dir *b*

        If the common parent of both is "/", return an absolute path
        """
        a += "/"
        b += "/"
        parent = posixpath.dirname(posixpath.commonprefix([a, b]))
        if parent == "/":
            return b[:-1]

        a = posixpath.relpath(a, parent)
        b = posixpath.relpath(b, parent)
        if a == ".":
            return b

        return posixpath.normpath("../" * (a.count("/") + 1) + b)

    def get_relative_path(self, section):
        """
        Returns a relative (file)path to point to section
        like (e.g. ../other_section)

        If the common parent of both sections is the document (i.e. /),
        return an absolute path
        """
        a = self.get_path()
        b = section.get_path()
        return self._get_relative_path(a, b)

    def clean(self):
        """
        Runs clean() on all immediate child-sections causing any resolved links
        or includes to be unresolved.

        This should be called for the document prior to saving.
        """
        for i in self:
            i.clean()

    def clone(self, children=True):
        """
        Clone this object recursively allowing to copy it independently
        to another document
        """
        from odml.section import BaseSection
        obj = super(Sectionable, self).clone(children)
        obj._parent = None
        obj._sections = SmartList(BaseSection)
        if children:
            for s in self._sections:
                obj.append(s.clone())

        return obj

    @property
    def repository(self):
        """ A URL to a terminology. """
        return self._repository

    @repository.setter
    def repository(self, url):
        if not url:
            url = None
        self._repository = url
        if url:
            terminology.deferred_load(url)

    def get_repository(self):
        """
        Return the current applicable repository (may be inherited from a
        parent) or None
        """
        return self._repository
