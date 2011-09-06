import gtk, gobject
debug = lambda x: 0

class ColumnMapper(object):
    def __init__(self, mapping_dictionary):
        """
        takes a dictionary of the form
        {"Text": (row_id, "attribute_name")}
        """
        self._col_map = mapping_dictionary
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

class TreeModel(gtk.GenericTreeModel):
    offset = 0 # number of elements to be cutoff from treeiter paths
    def __init__(self, col_mapper):
        self.col_mapper = col_mapper
        gtk.GenericTreeModel.__init__(self)

    def get_object(self, gtk_tree_iter):
        """
        gtk has its on special tree_iter that don't do our cool stuff

        the method gets our on tree_iter-version of the gtk one and returns
        its holding object
        """
        path = self.get_path(gtk_tree_iter)
        tree_iter = self.on_get_iter(path)
        return tree_iter._obj

    def on_get_flags(self):
        return 0

    def on_get_n_columns(self):
        return len(self.col_mapper)

    def on_get_column_type(self, index):
        return gobject.TYPE_STRING

    def on_get_path(self, tree_iter):
        debug("+on_get_path: %s" % (tree_iter))
        debug(" odml path: %s" % repr(tree_iter.to_path()))
        return self.odml_path_to_model_path(tree_iter.to_path()[self.offset:])

    def on_get_value(self, tree_iter, column):
        attr = self.col_mapper.name_by_column(column)
        debug(":on_get_value [%d:%s]: %s" % (column, attr, tree_iter))
        return tree_iter.get_value(attr)

    def on_iter_next(self, tree_iter):
        next = tree_iter.get_next()
        debug(":on_iter_next [%s]: %s" % (tree_iter, next))
        return next

    def on_iter_children(self, tree_iter):
        debug(":on_iter_children [%s]" % tree_iter)
        return tree_iter.get_children()

    def on_iter_has_child(self, tree_iter):
        debug(":on_iter_has_child [%s,%s]" % (tree_iter, tree_iter.has_child))
        return tree_iter.has_child

    def on_iter_n_children(self, tree_iter):
        if tree_iter is None: return 0
        return tree_iter.n_children

    def on_iter_nth_child(self, tree_iter, n):
        debug(":on_iter_nth_child [%d]: %s " % (n, tree_iter))
        if tree_iter is None:
            return None
        return tree_iter.get_nth_child(n)

    def on_iter_parent(self, tree_iter):
        debug(":on_iter_parent [%s]" % tree_iter)
        return tree_iter.parent
