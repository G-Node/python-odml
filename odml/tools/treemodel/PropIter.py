from ...property import Property
from ValueIter import ValueIter
import SectionModel

class PropIter(object):
    """
    An iterator for a Property

    returns ValueIter objects if queried for children.
    Since Values don't have a parent relationship, the PropIter will store
    pass a corresponding parent attribute (the Property object) to the ValueIter

    As odML supports multi-values, each property may or may not have multiple children.
    """
    counter = {}
    def __init__(self, prop):
        assert (isinstance(prop, Property))
        self._prop = prop
        self.id = self.counter.get(prop, 0)
        self.counter[prop] = self.id+1

    def get_value(self, column):
        #Stuff that is handled the same way in both cases
        #appears here
        name = SectionModel.ColMapper.name_by_column(column)
        if name == "name":
            return self._prop.name
        
        if self.has_child:
            return self.get_mulitvalue(name)
        else:
            return self.get_singlevalue(name)
        
    def get_mulitvalue(self, name):
        #Most of the stuff is empty and handled by the
        #value
        if name == "value":
                return "<multi>"
        return ""
    
    def get_singlevalue(self, name):
        #here we proxy the value object
        if len (self._prop._values) == 0:
            return ""
        
        prop = self._prop.values[0]
        return getattr(prop, name)
             
    def to_path(self):
        return self._prop.to_path()
    
    def get_next(self):
        prop = self._prop.next()
        if not prop:
            return None
        return PropIter(prop)
        
    def get_children(self):
        if self.has_child == False:
            return None
        return ValueIter(self._prop._values[0])

    @property
    def has_child(self):
        return self.n_children > 1
   
    @property
    def n_children(self):
        return len(self._prop._values)
    
    @property
    def parent(self):
        return None
    
    def get_nth_child(self, n):
        return ValueIter(self._prop._values[n])

    def __str__(self):
        return "<Iter%d %s>" % (self.id, repr(self._prop))
