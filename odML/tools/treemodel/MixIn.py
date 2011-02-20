from ...doc import Document
from ...section import Section
from ...property import Property
from ..event import Eventable

class RootNode(Eventable):
    def from_path (self, path):
        child = self._sections[path[0]]
        if len (path) == 1:
            return child
        return child.from_path (path[1:])

    def to_path(self):
        return None

class ChildNode(RootNode):
    def to_path (self):
        path = self._parent.to_path()
        if not path:
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
            return self._parent._sections[self.position + 1]
        except:
            return None

    @property
    def position(self):    
        return self._parent._sections.index(self)

class ListElement(Eventable):
    @property
    def position(self):
        return self._section._props.index(self)
        
    def next(self):
        try:
            return self._section._props[self.position + 1]
        except:
            return None

    def _fire_change_event(self, prop_name):
        if not self._section:
            return
        path = (self.position,)
        print "YYY %s %s" % (self.position, path)
        self.section.Changed(prop=self, propname=prop_name, path=path)

def extend_class(A, B):
    """
    add our mixin class B to A.__bases__
    also make sure, that __init__ of both A and B is called
    """
    bases = list(A.__bases__)
    bases.append(B)
    A.__bases__ = tuple(bases)
    org = A.__init__
    def init(*args, **kwargs):
        org(*args, **kwargs)
        B.__init__(*args, **kwargs)
    A.__init__ = init

extend_class(Document, RootNode)
extend_class(Section, ChildNode)
extend_class(Property, ListElement)
