#-*- coding: utf-8
"""
collects common base functionality
"""
import posixpath

class baseobject(object):
    _terminology_mapping = None
    _format = None

    def is_terminology_default(self, attribute=None, recursive=True):
        """
        returns whether this object is equal to its default terminology

        returns False if the object has no terminology associated

        by providing an *attribute* name, only this attribute is checked

        if *recursive* is False, no sub-objects (e.g. sections, properties or values)
        will be checked
        """

        term = self._terminology_mapping
        if term is None: return False

        fields = self._format

        if attribute is not None:
            fields = [attribute]

        for key in fields:
            val = getattr(self, key)
            if isinstance(val, list):
                if recursive:
                    for obj in val:
                        if not obj.is_terminology_default(attribute, recursive):
                            return False
            elif val != getattr(term, key):
                return False

        return True

    def __eq__(self, obj):
        """
        do a deep comparison of this object and its odml properties
        """
        # cannot compare totally different stuff
        if not isinstance(obj, baseobject): return False
        if not isinstance(self, obj.__class__ ): return False

        for key in self._format:
            if getattr(self, key) != getattr(obj, key):
                return False

        return True

    def clean(self):
        pass

    def clone(self):
        """
        clone this object recursively allowing to copy it independently
        to another document
        """
        # TODO don't we need some recursion / deepcopy here?
        import copy
        obj = copy.copy(self)
        return obj

class SmartList(list):
    def __getitem__(self, key):
        """
        provides element index also by searching for an element with a given name
        """
        # try normal list index first (for integers)
        if type(key) is int:
            return super(SmartList, self).__getitem__(key)

        # otherwise search the list
        for obj in self:
            if (hasattr(obj, "name") and obj.name == key) or key == obj:
                return obj

        # and fail eventually
        raise KeyError(key)

    def remove(self, obj):
        """
        remove an element from this list

        be sure to use "is" based comparison (instead of __cmp__ / ==)
        """
        for i, e in enumerate(self):
            if e is obj:
                del self[i]
                return
        raise ValueError("remove: %s not in list" % repr(obj))

class sectionable(baseobject):
    def __init__(self):
        self._sections = SmartList()

    @property
    def sections(self):
        return self._sections

    def append(self, section):
        """adds the section to the section-list and makes this document the section’s parent"""
        self._sections.append(section)
        section._parent = self

    def remove(self, section):
        self._sections.remove(section)
        section._parent = None

    def __getitem__(self, key):
        return self._sections[key]

    def __len__(self):
        return len(self._sections)

    def __iter__(self):
        return self._sections.__iter__()

    def itersections(self, recursive=False, yield_self=False):
        """
        iterate each child section

        if *recursive* is set, iterate all child sections recurively (depth-search)
        """
        if yield_self:
            yield self
        for i in self._sections:
            yield i
            if recursive:
                for j in i.itersections(recursive=recursive):
                    yield j

    def contains(self, obj):
        """
        checks if a subsection of name&type of *obj* is a child of this section
        if so return this child
        """
        for i in self._sections:
            if obj.name == i.name and obj.type == i.type:
                return i

    def _matches(self, obj, key=None, type=None):
        return (key is None or (key is not None and hasattr(obj, "name") and obj.name == key)) \
            and (type is None or (type is not None and hasattr(obj, "type") and obj.type == type))

    def find_by_path(self, path):
        """
        find a Section/Property through a path like "name1/name2"
        """
        path = path.split("/")
        return self._find_by_path(path)

    def _find_by_path(self, path):
        """
        find a Section/Property through a path like ("name1", "name2")
        """
        cur = self
        for i in path:
            if i == "." or i == "": continue
            if i == "..":
                cur = cur.parent
                continue
            cur = cur[i]
        return cur

    def find(self, key=None, type=None):
        """return the first subsection named *key* of type *type*"""
        for s in self._sections:
            if self._matches(s, key, type): return s

    def find_related(self, key=None, type=None, children=True, siblings=True, parents=True, recursive=True):
        """
        finds a related section named *key* and/or *type*

          * by searching its children’s children if *children* is True
            if *recursive* is true all leave nodes will be searched
          * by searching its siblings if *siblings* is True
          * by searching the parent element if *parents* is True
            if *recursive* is True all parent nodes until the root are searched
        """
        if children:
            for section in self._sections:
                if self._matches(section, key, type):
                    return section

                if recursive:
                    obj = section.find_related(key, type, children, siblings=False, parents=False, recursive=recursive)
                if obj is not None: return obj

        # docs have no parent attribute # TODO should use _parent instead of parent?
        if siblings and hasattr(self, "parent"):
            obj = self.parent.find(key, type)
            if obj is not None: return obj

        if parents:
            obj = self
            while hasattr(obj, "parent"):
                obj = obj.parent
                if self._matches(obj, key, type):
                    return obj
                if not recursive: break

        return None

    def get_path(self):
        """
        returns the absolute path of this section
        """
        node = self
        path = []
        while hasattr(node, "_parent"):
            path.insert(0, node.name)
            node = node._parent
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
        if parent == "/": return b[:-1]

        a = posixpath.relpath(a, parent)
        b = posixpath.relpath(b, parent)
        if a == ".": return b

        return posixpath.normpath("../" * (a.count("/")+1) + b)

    def get_relative_path(self, section):
        """
        returns a relative (file)path to point to section (e.g. ../other_section)

        if the common parent of both sections is the document (i.e. /), return an absolute path
        """
        a = self.get_path()
        b = section.get_path()
        return self._get_relative_path(a,b)

    def clean(self):
        for i in self:
            i.clean()

    def clone(self):
        """
        clone this object recursively allowing to copy it independently
        to another document
        """
        obj = super(sectionable, self).clone()
        obj._parent = None
        obj._sections = SmartList()
        for s in self._sections:
            obj.append(s.clone())

        return obj
