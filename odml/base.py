#-*- coding: utf-8
"""
collects common base functionality
"""

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
        # cannot compare totally different stuff # TODO do the check for the actual class
        if not isinstance(obj, baseobject): return False

        for key in self._format:
            if getattr(self, key) != getattr(obj, key):
                return False

        return True

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

class sectionable(baseobject):
    def __init__(self):
        self._sections = SmartList()

    @property
    def sections(self):
        return self._sections

    def append(self, section):
        """adds the section to the section-list and makes this document the section’s parent"""
        self._sections.append (section)
        section._parent = self
        
    def __iter__(self):
        return self._sections.__iter__()
    
    def itersections(self, recursive=False):
        """
        iterate each child section
        
        if *recursive* is set, iterate all child sections recurively (depth-search)
        """
        for i in self._sections:
            yield i
            if recursive:
                i.itersections(recursive=recursive)
    
    def _matches(self, obj, key=None, type=None): 
        return (key is None or (key is not None and hasattr(obj, "name") and obj.name == key)) \
            and (type is None or (type is not None and hasattr(obj, "type") and obj.type == type))
               
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
    
    def clone(self):
        """
        clone this object recursively allowing to copy it independently
        to another document
        """
        import copy
        obj = copy.copy(self)
        obj._sections = SmartList()
        for s in self._sections:
            obj.append(s.clone())
        
        return obj
