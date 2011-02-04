#!/usr/bin/evn python

from event import *

class odMLList(list):
    def __init__(self, *args, **kargs):
        list.__init__(self, *args, **kargs)

    def append(self, x):
        print "Appending: %s" % (x)
        print "len: %d" % (len (self))
        list.append(self, x)
        print "len: %d" % (len (self))

    def remove(self, x):
        list.remove(self, x)

class odMLDocument(object):
    """A represenation of an odML document in memory"""
    def __init__(self, author=None, date=None, version=1.0):
        self._sections = odMLList()
        self._author = author
        self._date = date
        self._version = version

    @property
    def author(self):
        return self._author

    def add_section(self, section):
        self._sections.append (section)
        section._parent = self

    @property
    def sections(self):
        return self._sections

    def from_path (self, path):
        child = self._sections[path[0]]
        if len (path) == 1:
            return child
        return child.from_path (path[1:])

    def to_path(self):
        return None

class odMLValue(object):
    """A odML value"""
    def __init__(self, value, type=None, prop = None):
        self._value = value
        self._prop = prop
        self._dtype = None
        
    @property
    def prop(self):
        return self._prop
    
    @property
    def position(self):
        return self._prop.values.index(self)
        
    def get_next(self):
        try:
            return self._prop.values[self.position + 1]
        except:
            return None

    @property
    def data(self):
        return self._value

    @property
    def dtype(self):
        return self._dtype
    
    @dtype.setter
    def dtype(self, new_type):
        self._dtype = new_type
        
    @property
    def uncertainty(self):
        return self._uncertainty
        
    @property
    def unit(self):
        return self._unit
    
    @property
    def id(self):
        return self._id
    
    @property
    def comment(self):
        return self._comment
    
    @property
    def defaultFilename(self):
        return self._default_filename
        
class odMLProperty(object):
    """A odML Property"""
    def __init__(self, name, section=None):
        self._name = name
        self._values = odMLList()
        self._section = section

    def get_name(self, UseTerminology=False):
        return self._name

    def set_name(self, val):
        self._name = val

    def del_name(self):
        del self._name

    Name = property(get_name, set_name, del_name, "Name of the Property")
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        self._fire_change_event("name")
    
    @property
    def values(self):
        return self._values

    @property
    def section(self):
        return self._section

    def add_value (self, val):
        self._values.append (val)
        val._prop = self

    @property
    def position(self):
        return self._section.props.index(self)
        
    def get_next(self):
        try:
            return self._section.props[self.position + 1]
        except:
            return None

    def _fire_change_event(self, prop_name):
        if not self.section:
            return
        path = (self.position,)
        print "YYY %s %s" % (self.position, path)
        self.section.Changed(prop=self, propname=prop_name, path=path)
        
class odMLSection(object):
    """A odML Section"""
    def __init__(self, name, parent=None):
        self._name = name
        self._props = odMLList()
        self._sections = odMLList()
        self._parent = parent
        self.Changed = Event()
                
    def get_name(self, UseTerminology=True):
        return self._name

    def set_name(self, val):
        self._name = val

    def del_name(self):
        del self._name

    Name = property(get_name, set_name, del_name, "Name of the section")
    name = property(get_name, set_name, del_name, "Name of the section")

    def get_name_definition(self, UseTerminology=True):
        if hasattr (self, "_name_definition"):
            return self._name_definition
        else:
            return None

    def set_name_definition(self, val):
        self._name_definition = val

    def del_name_definition(self):
        del self._name_definition

    NameDefinition = property(get_name_definition,
                              set_name_definition,
                              del_name_definition,
                              "Name Definition of the section")

    def append(self, obj):
        if obj.__class__ is odMLSection:
            self._sections.append (obj)
            obj._parent = self
        elif obj.__class__ is odMLProperty:
            self._props.append (obj)
            obj._section = self
        else:
            raise ValueError, "Can only append sections and properties"

    def sectioniter(self):
        for section in self._sections:
            yield section

    getsections = sectioniter

    def propiter(self):
        for prop in self._props:
            yield prop

    getproperties = propiter

    @property
    def type(self):
        return self._odml_type

    @property
    def parent(self):
        return self._parent

    @property
    def sections(self):
        return self._sections

    @property
    def props(self):
        return self._props

    @property
    def position(self):
        return self.parent.sections.index(self)

    def next(self):
        sps = self.parent.sections
        try:
            n = sps[self.position + 1]
            return n
        except:
            return None

    def from_path (self, path):
        child = self._sections[path[0]]
        if len (path) == 1:
            return child
        return child.from_path (path[1:])


    def to_path (self):
        path = self.parent.to_path()
        if not path:
            return (self.position, )
        return path + (self.position, )

