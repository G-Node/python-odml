#-*- coding: utf-8
import base
import format
from property import Property # this is supposedly ok, as we only use it for an isinstance check
                              # it MUST however not be used to create any Property objects
import doc

class Section(base.sectionable):
    """A odML Section"""
    type       = None
    id         = None
    _link      = None
    repository = None
    mapping    = None
    reference  = None # the *import* property

    _merged = None

    _format = format.Section

    def __init__(self, name, type="undefined", parent=None):
        self._parent = parent
        self._name = name
        self._props = base.SmartList()
        super(BaseSection, self).__init__()
        # this may fire a change event, so have the section setup then
        self.type = type

    def __repr__(self):
        return "<Section %s (%d)>" % (self._name, len(self._sections))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_value):
        self._name = new_value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, new_value):
        if self.parent is None: # we cannot possibly know where the link is going
            self._link = new_value
            return

        if new_value == '':
            self._link = None
            self.clean()
            return

        new_section = self.find_by_path(new_value) # raises exception if path cannot be found
        if self._link is not None:
            self.clean()
        self._link = new_value
        self.merge(new_section)

    def get_name_definition(self, UseTerminology=True):
        if hasattr(self, "_name_definition"):
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

    @property
    def document(self):
        """
        returns the parent-most node (if its a document instance) or None
        """
        p = self
        while p.parent:
            p = p.parent
        if isinstance(p, doc.Document):
            return p

    def append(self, obj):
        """append a Section or Property"""
        if isinstance(obj, Section):
            self._sections.append(obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.append(obj)
            obj._section = self
        else:
            raise ValueError, "Can only append sections and properties"


    def insert(self, position, obj):
        """insert a Section or Property at the respective position"""
        if isinstance(obj, Section):
            self._sections.insert(position, obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.insert(position, obj)
            obj._section = self
        else:
            raise ValueError, "Can only insert sections and properties"

    def remove(self, obj):
        if isinstance(obj, Section): # TODO make sure this is not compare based
            self._sections.remove(obj)
            obj._parent = None
        elif isinstance(obj, Property):
            self._props.remove(obj)
            obj._section = None
        else:
            raise ValueError, "Can only remove sections and properties"

    def __iter__(self):
        """iterate over each section and property contained in this section"""
        for section in self._sections:
            yield section
        for prop in self._props:
            yield prop

    def __len__(self):
        """number of children (sections AND properties)"""
        return len(self._sections) + len(self._props)

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

    def contains(self, obj):
        """
        finds a property or section with the same name&type properties or None
        """
        if isinstance(obj, Section):
            return super(BaseSection, self).contains(obj)
        for i in self._props:
            if obj.name == i.name:
                return i

    def _find_by_path(self, path):
        if path[0] == "": # this indicates a path like "/name1" i.e. starting with a slash
            if self.document is None: # for dangling sections (e.g. parsing not complete)
                return None
            return self.document._find_by_path(path[1:])
        return super(BaseSection, self)._find_by_path(path)

    def merge(self, section):
        for obj in section:
            mine = self.contains(obj)
            if mine is not None:
                mine.merge(obj)
            else:
                self.append(obj.clone())
        self._merged = section

    def clean(self):
        if self._merged is not None:
            self.unmerge(self._merged)
        super(BaseSection, self).clean()

    def unmerge(self, section):
        """
        clean up a merged section by removing objects that are totally equal
        to the linked object
        """
        if self == section:
            raise RuntimeException("cannot unmerge myself?")
            return #self._sections
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
        self._merged = None

BaseSection = Section
