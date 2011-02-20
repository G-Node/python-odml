#-*- coding: utf-8
"""
This module extends the odML base class by adding gtk.GenericTreeModel
functionality using MixIns

to use it just import this module::

>>> import odml.extras.treemodel
"""

import gtk
import gobject

from ..doc import Document
from ..section import Section
from ..property import Property
from ..value import Value
from ..event import Event

import sys
debug = lambda x: sys.stderr.write(x+"\n")
debug = lambda x: 0

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
        return PropIter(self._parent)
    
    def get_nth_child(self, n):
        return None

    def __repr__(self):
        return "<Iter %s <= %s[%d]>" % (repr(self._value), repr(self._parent), self.position)

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
        debug("+on_get_path: %s" % (tree_iter))
        return tree_iter.to_path()

    def on_get_iter(self, path):
        debug(":on_get_iter [%s] " % repr(path))
        assert (len (path) < 3)
        
        if len(self._section.properties) < (path[0] + 1):
            return None
        
        prop = self._section.properties[path[0]]
        if len(path) == 1:
            return PropIter(prop)

        value = prop.values[path[1]]
        if not value:
            return None
        return ValueIter(value, parent=prop)

    def on_get_value(self, tree_iter, column):
        debug(":on_get_value [%d]: %s" % (column, tree_iter))
        return tree_iter.get_value (column)

    def on_iter_next(self, tree_iter):
        next = tree_iter.get_next()
        debug(":on_iter_next [%s]: %s" % (tree_iter, next))
        return next

    def on_iter_children(self, tree_iter):
        debug(":on_iter_children [%s]" % tree_iter)
        return tree_iter.get_children()
  
    def on_iter_has_child(self, tree_iter):
        return tree_iter.has_child

    def on_iter_n_children(self, tree_iter):
        return tree_iter.n_children

    def on_iter_nth_child(self, tree_iter, n):
        debug(":on_iter_nth_child [%d]: %s " % (n, tree_iter))
        if tree_iter == None:
            prop = self._section._props[n]
            return PropIter(prop)
            
        tree_iter.get_nth_child(n)

    def on_iter_parent(self, tree_iter):
        debug(":on_iter_parent [%s]" % tree_iter)
        return tree_iter.parent
    
    def on_section_changed(self, *args, **kargs):
        path = kargs["path"]
        iter = self.get_iter(path)
        self.row_changed (path, iter)
        print ":: Foo! %s" % (str (path))

    @property
    def section(self):
        return self._section

class DocumentModel(gtk.GenericTreeModel):
    def __init__(self, odml_document):
        gtk.GenericTreeModel.__init__(self)
        self._document = odml_document

    def on_get_flags(self):
        return 0

    def on_get_n_columns(self):
        return 1

    def on_get_column_type(self, index):
        return gobject.TYPE_STRING

    def on_get_path(self, section):
        debug("+on_get_path: %s" % (section))
        return section.to_path()

    def on_get_iter(self, path):
        debug("+on_get_iter: %s" % repr(path))
        section = self._document.from_path (path)
        debug("-on_get_iter: %s" % (section))
        return section

    def on_get_value(self, section, column):
        assert column == 0
        debug(":on_get_value [%d]: %s" % (column, section))
        return section.name

    def on_iter_next(self, section):
        debug("+on_iter_next [%s]: %s" % (self._document, section))
        next = section.next()
        debug(":on_iter_next [%s]: %s" % (section, next))
        return next

    def on_iter_children(self, section):
        debug("+on_iter_children: %s" % (section))
        try:
            return section.sections[0]
        except:
            return None

    def on_iter_has_child(self, section):
        children = section.sections
        debug(":on_iter_has_children: %s:%s" % (section, len(children)))
        return len (children)

    def on_iter_n_children(self, section):
        return len (section.sections)

    def on_iter_nth_child(self, section, n):
        if section == None:
            children = self._document.sections
        else:
            children = section.sections
        return children[n]

    def on_iter_parent(self, section):
        parent = None
        if section._parent != self._document:
            parent = section._parent
        debug(":on_iter_parent: %s:%s" % (section, parent))
        return parent

class Eventable:
    def __init__(self, *args, **kwargs):
        self.Changed = Event()

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
        returns the next section following in this section’s parent’s list of sections
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
