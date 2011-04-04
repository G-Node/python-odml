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
