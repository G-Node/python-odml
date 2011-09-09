"""
provides node functionality for the eventable odml types
Document, Section, Property and Value

additionally implements change notifications up to the corresponding section
"""
from .. import event

def identity_index(obj, val):
    """
    same as obj.index(val) but will only return a position
    if the object val is found in the list

    i.e.
    >>> identity_index(["1"], "1")
    will raise an ValueError because the two strings
    are different objects with the same content

    >>> a = "1"
    >>> identity_index([a], a)
    0

    The difference to obj.index comes apparent here as well:
    >>> a="1", b="1"
    >>> identity_index([a,b], b)
    1
    >>> [a,b].index(b)
    0
    """
    for i, v in enumerate(obj):
        if v is val: return i

    import pdb; pdb.set_trace()
    raise ValueError("%s does not contain the item %s" % (repr(obj), repr(val)))

class RootNode(object):
    @property
    def children(self):
        return self._sections

    def from_path(self, path):
        child = self.children[path[0]]
        if len(path) == 1:
            return child
        return child.from_path(path[1:])

    def to_path(self, parent=None):
        return ()

    def path_to(self, child):
        """return the path from this node to its direct child *child*"""
        return (identity_index(self._sections, child),)

class ParentedNode(RootNode):
    def to_path(self, parent=None):
        if self.parent is parent:
            return self.parent.path_to(self)
        return self.parent.to_path(parent) + self.parent.path_to(self)

    def successor(self):
        return self.parent.children[self.position + 1]

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
            return self.successor()
        except IndexError:
            return None

    @property
    def position(self):
        return self.parent.path_to(self)[-1]

    @property
    def parent(self):
        return self._parent

class SectionNode(ParentedNode):
    """
    SectionNodes are special as they wrap two types of sub-nodes:

    * SubSections (path = (0, idx))
    * Properties  (path = (1, idx))
    """
    def from_path(self, path):
        assert len(path) > 1

        if path[0] == 0: # sections
            return super(SectionNode, self).from_path(path[1:])

        # else: properties
        child = self._props[path[1]]

        if len(path) == 2:
            return child
        return child.from_path(path[2:])


    def path_to(self, child):
        if isinstance(child, event.Property):
            return (1, identity_index(self._props, child))
        return (0, identity_index(self._sections, child))


class PropertyNode(ParentedNode):
    @property
    def parent(self):
        """returns the parent section of this Property"""
        return self._section

    @property
    def children(self):
        return self._values

    def successor(self):
        return self.parent._props[self.position + 1]

    def path_to(self, child):
        return (identity_index(self.values, child),)

class ValueNode(ParentedNode):
    @property
    def parent(self):
        return self._property

    def path_from(self, path):
        raise TypeError("Value objects have no children")

    def path_to(self, child):
        raise TypeError("Value objects have no children")

#TODO? provide this externally?
class Document(event.Document, RootNode): pass
class Value(event.Value, ValueNode): pass
class Property(event.Property, PropertyNode): pass
class Section(event.Section, SectionNode): pass

def pass_on_change(context):
    parent = context.cur.parent
    if parent is not None:
        context.passOn(parent)

Value._Changed.finish    = pass_on_change
Property._Changed.finish = pass_on_change
Section._Changed.finish  = pass_on_change

# TODO this should probably be mixed in somewhere else too
import TreeIters
Section.IterClass  = TreeIters.SectionIter
Property.IterClass = TreeIters.PropIter
Value.IterClass    = TreeIters.ValueIter

# TODO on_section_change(sec, **kwargs)
