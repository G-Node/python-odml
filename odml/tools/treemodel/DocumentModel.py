import gtk, gobject
debug = lambda x: 0
# to enable tree debugging:
#import sys
#debug = lambda x: sys.stdout.write(x + "\n")

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
        debug("+on_get_path: %s (%s)" % (section, section.to_path()))
        return section.to_path()

    def on_get_iter(self, path):
        debug("+on_get_iter: %s" % repr(path))
        if path == (0,) and len(self._document.sections) == 0: return None
        # we get the path from the treemodel which does not show the properties
        # therefore adjust the path to always select the sections
        rpath = (path[0],) # document -> section
        for i in path[1:]:
            rpath += (0,i) # section -> sub-section
        section = self._document.from_path(rpath)
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
