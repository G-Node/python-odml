from ...value import Value
import PropIter
import SectionModel

class ValueIter(object):
    """
    An iterator for a Value object

    
    """
    def __init__(self, value):
        """
        create a new value iterator with a Value object and it's parent a Property object
        """
        assert isinstance(value, Value)
        self._value = value

    def get_value(self, column):
        prop = SectionModel.ColMapper.name_by_column(column)
        if prop == "name":
            return
        return getattr(self._value, prop)
    
    def to_path(self):
        return None

    def get_next(self):
        """
        returns a new ValueIter object for the next element in this multivalue list
        or None
        """
        print ":get_next(%s)" % repr(self._value)
        value = self._value.next()
        if value:
            return ValueIter(value)
    
    def get_children(self):
        return None

    @property
    def has_child(self):
        return False
    
    @property
    def n_children(self):
        return 0
    
    @property
    def parent(self):
        print ":get_parent(%s)" % repr(self._value)
        return PropIter.PropIter(self._value._property)
    
    def get_nth_child(self, n):
        return None

    def __repr__(self):
        return "<Iter %s <= %s[%d]>" % (repr(self._value), repr(self._value._property), self._value.position)
