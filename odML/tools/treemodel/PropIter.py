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
        if column == SectionModel.ColMapper["Name"]:
            return self._prop.name
        
        if self.has_child:
            return self.get_mulitvalue(column)
        else:
            return self.get_singlevalue(column)
        
    def get_mulitvalue(self, column):
        #Most of the stuff is empty and handled by the
        #value
        if column == SectionModel.ColMapper["Value"]:
                return "<multi>"
        return ""
    
    def get_singlevalue(self, column):
        #here we proxy the value object
        if len (self._prop._values) == 0:
            return ""
        
        prop = self._prop.values[0]
        if column == SectionModel.ColMapper["Value"]:
            return prop.data
        elif column == SectionModel.ColMapper["Type"]:
            return prop.dtype
        return "" 
             
    def to_path(self):
        return None
    
    def get_next(self):
        prop = self._prop.next()
        if not prop:
            return None
        return PropIter(prop)
        
    def get_children(self):
        if self.has_child == False:
            return None
        return ValueIter(self._prop._values[0], parent=self._prop)

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
        return ValueIter(self._prop._values[n], parent=self._prop)

    def __str__(self):
        return "<Iter%d %s>" % (self.id, repr(self._prop))
