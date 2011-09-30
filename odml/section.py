#-*- coding: utf-8
import base
import format
import terminology
import mapping
from property import Property # this is supposedly ok, as we only use it for an isinstance check
                              # it MUST however not be used to create any Property objects

class Section(base._baseobj):
    pass

class BaseSection(base.sectionable, mapping.mapableSection, Section):
    """A odML Section"""
    type       = None
    id         = None
    _link      = None
    _include    = None
    _mapping    = None
    reference  = None # the *import* property

    _merged = None

    _format = format.Section

    def __init__(self, name, type="undefined", parent=None, mapping=None):
        self._parent = parent
        self._name = name
        self._props = base.SmartList()
        self._mapping = mapping
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
    def include(self):
        return self._include

    @include.setter
    def include(self, new_value):
        if self._link is not None:
            raise TypeError("%s.include: You can either set link or include, but not both." % repr(self))

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
        new_section = term.find_by_path(path) if path is not None else term.sections[0]

        if self._include is not None:
            self.clean()
        self._include = new_value
        self.merge(new_section)

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, new_value):
        if self._include is not None:
            raise TypeError("%s.link: You can either set link or include, but not both." % repr(self))

        if self.parent is None: # we cannot possibly know where the link is going
            self._link = new_value
            return

        if not new_value:
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

    def get_repository(self):
        """
        returns the repository responsible for this section,
        which might not be the *repository* attribute, but may
        be inherited from a parent section / the document
        """
        if self._repository is None and self.parent is not None:
            return self.parent.get_repository()
        return super(BaseSection, self).repository

    @base.sectionable.repository.setter
    def repository(self, url):
        if self._active_mapping is not None:
            raise ValueError("cannot edit repsitory while a mapping is active")
        base.sectionable.repository.fset(self, url)

    def get_terminology_equivalent(self):
        repo = self.get_repository()
        if repo is None: return None
        term = terminology.load(repo)
        if term is None: return None
        return term.find_related(type=self.type)

    def get_merged_equivalent(self):
        """
        return the merged object or None
        """
        return self._merged

    def append(self, obj):
        """append a Section or Property"""
        if isinstance(obj, Section):
            self._sections.append(obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.append(obj)
            obj._section = self
        else:
            raise ValueError("Can only append sections and properties")


    def insert(self, position, obj):
        """insert a Section or Property at the respective position"""
        if isinstance(obj, Section):
            self._sections.insert(position, obj)
            obj._parent = self
        elif isinstance(obj, Property):
            self._props.insert(position, obj)
            obj._section = self
        else:
            raise ValueError("Can only insert sections and properties")

    def remove(self, obj):
        if isinstance(obj, Section): # TODO make sure this is not compare based
            self._sections.remove(obj)
            obj._parent = None
        elif isinstance(obj, Property):
            self._props.remove(obj)
            obj._section = None
            # also: TODO unmap the property
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

    def clone(self, children=True):
        """
        clone this object recursively allowing to copy it independently
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

    def merge(self, section=None):
        """
        merges this section with another *section*

        if section is none, sets the link/include attribute causing
        the section to be automatically merged
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

        # the path may not be valid anymore, so make sure to update it
        # however this does not reflect changes happening while the section
        # is unmerged
        if self._link is not None:
            # TODO get_absolute_path, # TODO don't change if the section can still be reached using the old link
            self._link = self.get_relative_path(section)

        self._merged = None

    @property
    def is_merged(self):
        return self._merged is not None

    @property
    def can_be_merged(self):
        return self._link is not None or self._include is not None
