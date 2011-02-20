import gtk, gobject
from PropIter import PropIter
from ValueIter import ValueIter
import sys
debug = lambda x: sys.stderr.write(x+"\n")
#debug = lambda x: 0

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

ColMapper = ColumnMapper()

class SectionModel(gtk.GenericTreeModel):
    def __init__(self, section):
        gtk.GenericTreeModel.__init__(self)
        self._section = section
        self._section.Changed += self.on_section_changed

    def on_get_flags(self):
        return 0

    def on_get_n_columns(self):
        return len(ColMapper)

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
        self.row_changed(path, iter)
        print ":: Foo! %s" % (str (path))

    @property
    def section(self):
        return self._section
