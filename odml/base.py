# -*- coding: utf-8
"""
collects common base functionality
"""
import sys
import posixpath
from odml import terminology
from odml import mapping
# from odml import doc
from odml.tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class _baseobj(object):
    pass


class baseobject(_baseobj):
    _format = None

    @property
    def document(self):
        """returns the Document object in which this object is contained"""
        if self.parent is None:
            return None
        return self.parent.document

    def get_terminology_equivalent(self):
        """
        returns the equivalent object in an terminology (should there be one
        defined) or None
        """
        return None

    def __eq__(self, obj):
        """
        do a deep comparison of this object and its odml properties
        """
        # cannot compare totally different stuff
        if not isinstance(obj, _baseobj):
            return False

        if not isinstance(self, obj.__class__):
            return False

        for key in self._format:
            if getattr(self, key) != getattr(obj, key):
                return False

        return True

    def __ne__(self, obj):
        """
        use the __eq__ function to determine if both objects are equal
        """
        return not self == obj

    def clean(self):
        """
        stub that doesn't do anything for this class
        """
        pass

    def clone(self, children=True):
        """
        clone this object recursively (if children is True) allowing to copy it independently
        to another document. If children is False, this acts as a template cloner, creating
        a copy of the object without any children
        """
        # TODO don't we need some recursion / deepcopy here?
        import copy
        obj = copy.copy(self)
        return obj

    def _reorder(self, childlist, new_index):
        l = childlist
        old_index = l.index(self)

        # 2 cases: insert after old_index / insert before
        if new_index > old_index:
            new_index += 1
        l.insert(new_index, self)
        if new_index < old_index:
            del l[old_index+1]
        else:
            del l[old_index]
        return old_index

    def reorder(self, new_index):
        """
        move this object in its parent child-list to the position *new_index*

        returns the old index at which the object was found
        """
        raise NotImplementedError


class SafeList(list):
    def index(self, obj):
        """
        find obj in list

        be sure to use "is" based comparison (instead of __eq__)
        """
        for i, e in enumerate(self):
            if e is obj:
                return i
        raise ValueError("remove: %s not in list" % repr(obj))

    def remove(self, obj):
        """
        remove an element from this list

        be sure to use "is" based comparison (instead of __eq__)
        """
        del self[self.index(obj)]


class SmartList(SafeList):
    def __getitem__(self, key):
        """
        provides element index also by searching for an element with a given name
        """
        # try normal list index first (for integers)
        if isinstance(key, int):
            return super(SmartList, self).__getitem__(key)

        # otherwise search the list
        for obj in self:
            if (hasattr(obj, "name") and obj.name == key) or key == obj:
                return obj

        # and fail eventually
        raise KeyError(key)

    def __contains__(self, key):
        for obj in self:
            if (hasattr(obj, "name") and obj.name == key) or key == obj:
                return True

    def append(self, obj):
        if obj.name in self:
            raise KeyError("Object with the same name already exists! " + str(obj))
        else:
            super(SmartList, self).append(obj)


@allow_inherit_docstring
class sectionable(baseobject, mapping.mapped):
    def __init__(self):
        self._sections = SmartList()
        self._repository = None

    @property
    def document(self):
        """
        returns the parent-most node (if its a document instance) or None
        """
        p = self
        while p.parent:
            p = p.parent
        import odml.doc as doc
        if isinstance(p, doc.Document):
            return p

    @property
    def sections(self):
        """the list of sections contained in this section/document"""
        return self._sections

    @mapping.remapable_insert
    def insert(self, position, section):
        """
        adds the section to the section-list and makes this document the section’s parent

        currently just appends the section and does not insert at the specified *position*
        """
        self._sections.append(section)
        section._parent = self

    @mapping.remapable_append
    def append(self, section):
        """adds the section to the section-list and makes this document the section’s parent"""
        self._sections.append(section)
        section._parent = self

    @inherit_docstring
    def reorder(self, new_index):
        return self._reorder(self.parent.sections, new_index)

    @mapping.remapable_remove
    def remove(self, section):
        """removes the specified child-section"""
        self._sections.remove(section)
        section._parent = None

    def __getitem__(self, key):
        return self._sections[key]

    def __len__(self):
        return len(self._sections)

    def __iter__(self):
        return self._sections.__iter__()

    def itersections(self, recursive=True, yield_self=False, filter_func=lambda x: True, max_depth=None):
        """
        iterate each child section

        >>> # example: return all subsections which name contains "foo"
        >>> filter_func = lambda x: getattr(x, 'name').find("foo") > -1
        >>> sec_or_doc.itersections(filter_func=filter_func)

        :param recursive: iterate all child sections recursively (deprecated)
        :type recursive: bool

        :param yield_self: includes itself in the iteration
        :type yield_self: bool

        :param filter_func: accepts a function that will be applied to each iterable. Yields
                            iterable if function returns True
        :type filter_func: function
        """
        stack = []
        # below: never yield self if self is a Document
        if self == self.document and ((max_depth is None) or (max_depth > 0)):
            for sec in self.sections:
                stack.append((sec, 1))  # (<section>, <level in a tree>)
        elif not self == self.document:
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
        iterate each related property (recursively)

        >>> # example: return all children properties which name contains "foo"
        >>> filter_func = lambda x: getattr(x, 'name').find("foo") > -1
        >>> sec_or_doc.iterproperties(filter_func=filter_func)

        :param max_depth: iterate all properties recursively if None, only to a certain
                            level otherwise
        :type max_depth: bool

        :param filter_func: accepts a function that will be applied to each iterable. Yields
                            iterable if function returns True
        :type filter_func: function
        """
        for sec in [s for s in self.itersections(max_depth=max_depth, yield_self=True)]:
            if hasattr(sec, "properties"):  # not to fail if odml.Document
                for i in sec.properties:
                    if filter_func(i):
                        yield i

    def itervalues(self, max_depth=None, filter_func=lambda x: True):
        """
        iterate each related value (recursively)

        >>> # example: return all children values which string converted version has "foo"
        >>> filter_func = lambda x: str(getattr(x, 'data')).find("foo") > -1
        >>> sec_or_doc.itervalues(filter_func=filter_func)

        :param max_depth: iterate all properties recursively if None, only to a certain
                            level otherwise
        :type max_depth: bool

        :param filter_func: accepts a function that will be applied to each iterable. Yields
                            iterable if function returns True
        :type filter_func: function
        """
        for prop in [p for p in self.iterproperties(max_depth=max_depth)]:
            for v in prop.values:
                if filter_func(v):
                    yield v

    def contains(self, obj):
        """
        checks if a subsection of name&type of *obj* is a child of this section
        if so return this child
        """
        for i in self._sections:
            if obj.name == i.name and obj.type == i.type:
                return i

    def _matches(self, obj, key=None, type=None, include_subtype=False):
        """
        find out
        * if the *key* matches obj.name (if key is not None)
        * or if *type* matches obj.type (if type is not None)
        * if type does not match exactly, test for subtype. (e.g.stimulus/white_noise)
        comparisons are case-insensitive, however both key and type
        MUST be lower-case.
        """
        name_match = (key is None or (key is not None and hasattr(obj, "name") and obj.name == key))
        exact_type_match = (type is None or (type is not None and hasattr(obj, "type") and obj.type.lower() == type))
        if not include_subtype:
            return name_match and exact_type_match
        subtype_match = type is None or (type is not None and hasattr(obj, "type") and
                                         type in obj.type.lower().split('/')[:-1])
        return name_match and (exact_type_match or subtype_match)

    def get_section_by_path(self, path):
        """
        find a Section through a path like "../name1/name2"

        :param path: path like "../name1/name2"
        :type path: str
        """
        return self._get_section_by_path(path)

    def get_property_by_path(self, path):
        """
        find a Property through a path like "../name1/name2:property_name"

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
            raise ValueError("A section with no Document cannot resolve absolute path")

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
        """return the first subsection named *key* of type *type*"""
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

    def find_related(self, key=None, type=None, children=True, siblings=True, parents=True, recursive=True, findAll=False):
        """
        finds a related section named *key* and/or *type*

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
                    obj = section.find_related(key, type, children, siblings=False, parents=False, recursive=recursive, findAll=findAll)
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
        returns the absolute path of this section
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
        returns a relative path for navigation from dir *a* to dir *b*

        if the common parent of both is "/", return an absolute path
        """
        a += "/"
        b += "/"
        parent = posixpath.dirname(posixpath.commonprefix([a,b]))
        if parent == "/":
            return b[:-1]

        a = posixpath.relpath(a, parent)
        b = posixpath.relpath(b, parent)
        if a == ".":
            return b

        return posixpath.normpath("../" * (a.count("/")+1) + b)

    def get_relative_path(self, section):
        """
        returns a relative (file)path to point to section (e.g. ../other_section)

        if the common parent of both sections is the document (i.e. /), return an absolute path
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
        clone this object recursively allowing to copy it independently
        to another document
        """
        obj = super(sectionable, self).clone(children)
        obj._parent = None
        obj._sections = SmartList()
        if children:
            for s in self._sections:
                obj.append(s.clone())

        return obj

    @property
    def repository(self):
        """An url to a terminology."""
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
        return the current applicable repository (may be inherited from a
        parent) or None
        """
        return self._repository
