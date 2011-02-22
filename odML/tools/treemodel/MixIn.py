from .. import event

class RootNode(object):
    child_name  = "_sections"
    def from_path(self, path):
        child = getattr(self, self.child_name)[path[0]]
        if len (path) == 1:
            return child
        return child.from_path(path[1:])

    def to_path(self):
        return None

class ParentedNode(RootNode):
    parent_name = "_parent"
    def to_path(self):
        path = getattr(self, self.parent_name).to_path()
        if path is None:
            return (self.position, )
        return path + (self.position, )
        
    def next(self):
        """
        returns the next section following in this section's parent's list of sections
        returns None if there is no further element available

        i.e.:
            parent
              sec-a (<- self)
              sec-b

        will return sec-b
        """
        try:
            parent = getattr(self, self.parent_name)
            return getattr(parent, self.child_name)[self.position + 1]
        except IndexError:
            return None
            
    @property
    def position(self):
        parent = getattr(self, self.parent_name)
        return getattr(parent, self.child_name).index(self)

class SectionNode(ParentedNode):
    def from_path(self, path):
        if not str(path[0]).startswith('p'):
            return super(SectionNode, self).from_path(path)
            
        child = self._props[int(path[0][1:])]
        if len(path) == 1:
            return child
        return child.from_path(path[1:])

class PropertyNode(ParentedNode):
    parent_name = "_section"
    child_name = "_props"
    def to_path(self, parent_name=None):
        path = super(PropertyNode, self).to_path()
        return path[:-1] + ("p"+str(path[-1]),)

class ValueNode(SectionNode):
    parent_name = "_property"
    child_name  = "_values"

class Document(event.Document, RootNode): pass
class Value(event.Value, ValueNode): pass
class Property(event.Property, PropertyNode): pass
class Section(event.Section, SectionNode): pass

def on_value_change(value, **kwargs):
    prop = val._property
    prop.Changed(prop=prop, value=value, value_pos=treetools.value_position(val), **kwargs)
    
Value.Changed += on_value_change

def on_property_change(prop, **kwargs):
    sec = prop._section
    sec.Changed(section=sec, prop=prop, prop_pos=treetools.property_position(prop), **kwargs)
    
Property.Changed += on_property_change

#old obsolete stuff
def value_position(cls):
    return cls._property._values.index(cls)

def property_position(cls):
    return cls._section._props.index(cls)

def section_position(cls):
    return cls._parent._sections.index(cls)

def position(cls):
    if isinstance(cls, Value):
        return value_position(cls)
    elif isinstance(cls, Property):
        return property_position(cls)
    elif isinstance(cls, Section):
        return section_position(cls)
