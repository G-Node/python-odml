import gtk
import gobject

from odml import *

class PropIter(object):
    def __init__(self, prop):
        assert (isinstance(prop, odMLProperty))
        self._prop = prop

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
        if len (self._prop.values) == 0:
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
        prop = self._prop.get_next()
        if not prop:
            return None
        return PropIter(prop)
        
    def get_children(self):
        if self.has_child == False:
            return None
        return ValueIter (self._prop.values[0])

    @property
    def has_child(self):
        return self.n_children > 1
   
    @property
    def n_children(self):
        return len (self._prop.values)
    
    @property
    def parent(self):
        return None
    
    def get_nth_child(self, n):
        return ValueIter (self._prop.values[n])
    
class ValueIter(object):
    def __init__(self, value):
        assert (isinstance(value, odMLValue))
        self._value = value

    def get_value(self, column):
        if column == SectionModel.ColMapper["Value"]:
            return self._value.data
        if column == SectionModel.ColMapper["Type"]:
            return self._value.dtype
        return ""
    
    def to_path(self):
        return None

    def get_next(self):
        value = self._value.get_next()
        if not value:
            return None
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
        return PropIter (self._value.prop)
    
    def get_nth_child(self, n):
        return None

class ColumnMapper(object):
    def __init__(self):
        self._col_map = {"Name"        : 0,
                         "Value"       : 1,
                         "Definition"  : 2,
                         "Type"        : 3,
                         "Unit"        : 4,
                         "Comment"     : 5}    

    def __getitem__(self, key):
        return self._col_map[key]

    def __len__(self):
        return len (self._col_map)

class SectionModel(gtk.GenericTreeModel):
    
    ColMapper = ColumnMapper()

    def __init__(self, section):
        gtk.GenericTreeModel.__init__(self)
        self._section = section
        self._section.Changed += self.on_section_changed
        

    def on_get_flags(self):
        return 0

    def on_get_n_columns(self):
        return len (SectionModel.ColMapper)

    def on_get_column_type(self, index):
        return gobject.TYPE_STRING

    def on_get_path(self, tree_iter):
        #print "+on_get_path: %s" % (tree_iter)
        return tree_iter.to_path()

    def on_get_iter(self, path):
        assert (len (path) < 3)
        
        if len (self._section.props) < (path[0] + 1):
            return None
        
        prop = self._section.props[path[0]]
        if len(path) == 1:
            return PropIter(prop)

        #print "XXX %s %s" % (len (path), path)
        value = prop.values[path[1]]
        if not value:
            return None
        return ValueIter(value)

    def on_get_value(self, tree_iter, column):
        print ":on_get_value [%d]: %s" % (column, tree_iter)
        return tree_iter.get_value (column)

    def on_iter_next(self, tree_iter):
        next = tree_iter.get_next()
        print ":on_iter_next [%s]: %s" % (tree_iter, next)
        return next

    def on_iter_children(self, tree_iter):
        return tree_iter.get_children()
  
    def on_iter_has_child(self, tree_iter):
        return tree_iter.has_child

    def on_iter_n_children(self, tree_iter):
        return tree_iter.n_children

    def on_iter_nth_child(self, tree_iter, n):
        if tree_iter == None:
            prop = self._section.props[n]
            return PropIter (prop)
            
        tree_iter.get_nth_child(n)

    def on_iter_parent(self, tree_iter):
        return tree_iter.parent
    
    
    def on_section_changed(self, *args, **kargs):
        path = kargs["path"]
        iter = self.get_iter(path)
        self.row_changed (path, iter)
        print ":: Foo! %s" % (str (path))

    @property
    def section(self):
        return self._section
