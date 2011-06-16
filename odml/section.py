import base
import format
from property import Property # this is supposedly ok, as we only use it for an isinstance check
                              # it MUST however not be used to create any Property objects

class Section(base.sectionable):
    """A odML Section"""
    type       = None
    id         = None
    link       = None
    repository = None
    mapping    = None
    reference  = None # the *import* property

    _format = format.Section

    def __init__(self, name, type="undefined", parent=None):
        self._name = name
        self.type = type
        self._parent = parent
        self._props = base.SmartList()
        super(BaseSection, self).__init__()

    def __repr__(self):
        return "<Section %s (%d)>" % (self._name, len(self._sections))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_value):
        self._name = new_value
        
    def get_name_definition(self, UseTerminology=True):
        if hasattr (self, "_name_definition"):
            return self._name_definition
        else:
            return None

    def set_name_definition(self, val):
        self._name_definition = val

    def del_name_definition(self):
        del self._name_definition

    definition = property(get_name_definition,
                              set_name_definition,
                              del_name_definition,
                              "Name Definition of the section")

    # API (public) 
    #
    #  properties
    @property
    def properties(self):
    	return self._props

    @property
    def sections(self):
    	return self._sections

    @property
    def parent(self):
        return self._parent
    
    def append(self, obj):
        """append a Section or Property"""
        if isinstance(obj, Section):
            self._sections.append (obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.append (obj)
            obj._section = self
        else:
            raise ValueError, "Can only append sections and properties"

    def __iter__(self):
        """iterate over each section and property contained in this section"""
        for section in self._sections:
            yield section
        for prop in self._props:
            yield prop

    def clone(self):
        """
        clone this object recursively allowing to copy it independently
        to another document
        """
        obj = super(BaseSection, self).clone()
        
        obj._props = base.SmartList()
        for p in self._props:
            obj.append(p.clone())
        
        return obj

BaseSection = Section
