from ...value import Value
from ...property import Property
import PropIter
import SectionModel

class ValueIter(object):
    """
    An iterator for a Value object

    
    """
    def __init__(self, value, parent):
        """
        create a new value iterator with a Value object and it's parent a Property object
        """
        assert isinstance(value, Value)
        assert isinstance(parent, Property)
        self._value = value
        self._parent = parent

    def get_value(self, column):
        if column == SectionModel.ColMapper["Value"]:
            return self._value.data
        if column == SectionModel.ColMapper["Type"]:
            return self._value.dtype
        return ""
    
    def to_path(self):
        return None

    def get_next(self):
        """
        returns a new ValueIter object for the next element in this multivalue list
        or None
        """
        try:
            value = self._parent._values[self.position + 1]
        except IndexError:
            return None
        return ValueIter(value, self._parent)
    
    def get_children(self):
        return None

    @property
    def position(self):
        return self._parent._values.index(self._value)

    @property
    def has_child(self):
        return False
    
    @property
    def n_children(self):
        return 0
    
    @property
    def parent(self):
        return PropIter.PropIter(self._parent)
    
    def get_nth_child(self, n):
        return None

    def __repr__(self):
        return "<Iter %s <= %s[%d]>" % (repr(self._value), repr(self._parent), self.position)
