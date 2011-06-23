import gtk, gobject
from PropIter import PropIter
from ValueIter import ValueIter
import sys
from ... import value, property as odmlproperty
debug = lambda x: sys.stderr.write(x+"\n")
debug = lambda x: 0

class ColumnMapper(object):
    def __init__(self):
        self._col_map = {"Name"        : (0, "name"),
                         "Value"       : (1, "value"),
                         "Definition"  : (2, "definition"),
                         "Type"        : (3, "dtype"),
                         "Unit"        : (4, "unit"),
                         "Comment"     : (5, "comment"),
                         "Id"          : (6, "id")}
        rev_map = {}
        for k, v in self._col_map.iteritems():
            rev_map[v[0]] = k

        self.rev_map = rev_map

    def __getitem__(self, key):
        return self._col_map[key]

    def iteritems(self):
        return self._col_map.iteritems()

    def sort_iteritems(self):
        for i in xrange(len(self.rev_map)):
            yield self.rev_map[i], self._col_map[self.rev_map[i]]

    def name_by_column(self, column):
        return self._col_map[self.rev_map[column]][1]

    def __len__(self):
        return len (self._col_map)

ColMapper = ColumnMapper()

class SectionModel(gtk.GenericTreeModel):
    def __init__(self, section):
        gtk.GenericTreeModel.__init__(self)
        self._section = section
        self._section._Changed += self.on_section_changed

    def on_get_flags(self):
        return 0

    def on_get_n_columns(self):
        return len(ColMapper)

    def on_get_column_type(self, index):
        return gobject.TYPE_STRING

    def model_path_to_odml_path(self, path):
        # (n, ...) -> (1, ...)
        return self.section.to_path() + (1,) + path # we consider properties only

    def odml_path_to_model_path(self, path):
        sp = len(self.section.to_path())
        return path[sp+1:]

    def on_get_path(self, tree_iter):
        debug("+on_get_path: %s" % (tree_iter))
        debug("path: %s" % repr(tree_iter.to_path()))
        return tree_iter.to_path()

    def on_get_iter(self, path):
        debug(":on_get_iter [%s] " % repr(path))
        assert (len (path) < 3)

        if len(self._section._props) == 0: return None

        path = (1,) + path # we consider properties only

        res = self._section.from_path(path)
        if isinstance(res, value.Value):
            return ValueIter(res)
        else:
            return PropIter(res)

    def on_get_value(self, tree_iter, column):
        debug(":on_get_value [%d]: %s" % (column, tree_iter))
        return tree_iter.get_value(column)

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

    def on_section_changed(self, section=None, prop=None, value=None, prop_pos=None, value_pos=None, *args, **kargs):
        """
        this is called by the Eventable modified MixIns of Value/Property/Section
        and causes the GUI to refresh the corresponding cells
        """
        if prop is None: return

        # a change listener is installed globally
        # we only take notifications for our own section
        if not section == self._section: return

        path = (prop_pos,)
        if value_pos is not None:
            path += (value_pos,)

        iter = self.get_iter(path)
        self.row_changed(path, iter)

    def destroy(self):
        self._section._Changed -= self.on_section_changed

    @property
    def section(self):
        return self._section
