import gtk, gobject
from TreeIters import PropIter, ValueIter
from TreeModel import TreeModel, ColumnMapper
import sys
from ... import value, property as odmlproperty
debug = lambda x: sys.stderr.write(x+"\n")
debug = lambda x: 0


ColMapper = ColumnMapper({"Name"        : (0, "name"),
                         "Value"       : (1, "value"),
                         "Definition"  : (2, "definition"),
                         "Type"        : (3, "dtype"),
                         "Unit"        : (4, "unit"),
                         "Comment"     : (5, "comment"),
                         "Endcoder"    : (6, "encoder"),
                         "Checksum"    : (7, "checksum"),
                         "Id"          : (8, "id")})

class SectionModel(TreeModel):
    def __init__(self, section):
        super(SectionModel, self).__init__(ColMapper)
        self._section = section
        self._section._Changed += self.on_section_changed
        self.offset = len(section.to_path())

    @staticmethod
    def model_path_to_odml_path(path):
        # (n, ...) -> (1, ...)
        return (1,) + path # we consider properties only

    @staticmethod
    def odml_path_to_model_path(path):
        return path[1:]

    def on_get_iter(self, path):
        debug(":on_get_iter [%s] " % repr(path))

        if len(self._section._props) == 0: return None

        path = self.model_path_to_odml_path(path) # we consider properties only
        node = self._section.from_path(path)
        return self._get_node_iter(node)

    def on_iter_nth_child(self, tree_iter, n):
        debug(":on_iter_nth_child [%d]: %s " % (n, tree_iter))
        if tree_iter == None:
            prop = self._section._props[n]
            return PropIter(prop)
        return super(SectionModel, self).on_iter_nth_child(tree_iter, n)

    def _get_node_iter(self, node):
        if isinstance(node, value.Value):
            return ValueIter(node)
        return PropIter(node)

    def post_delete(self, parent, old_path):
        super(SectionModel, self).post_delete(parent, old_path)
        if isinstance(parent, odmlproperty.BaseProperty):
            # a value was deleted
            if len(parent) == 1:
                # the last child row is also not present anymore,
                # the value is now displayed inline
                path = self.get_node_path(parent)
                print "row deleted", path + (0,)
                self.row_deleted(path + (0,)) # first child
                self.row_has_child_toggled(path, self.get_iter(path))

    def post_insert(self, node):
        # this actually already works fine, since the subtree will always start
        # collapsed, however in fact we would need to insert an additional row
        # if the property switched from one value to two values
        # (the first was displayed inline, but now gets its own row)
        super(SectionModel, self).post_insert(node)

    def on_section_changed(self, context):
        """
        this is called by the Eventable modified MixIns of Value/Property/Section
        and causes the GUI to refresh the corresponding cells
        """
        print "change event(property): ", context

        # we are only interested in changes going up to the section level,
        # but not those dealing with subsections of ours
        if not context.cur is self._section or \
                isinstance(context.val, self._section.__class__):
            return

        if context.action == "set" and context.postChange:
            path = self.get_node_path(context.obj)
            if not path: return # probably the section changed
            iter = self.get_iter(path)
            self.row_changed(path, iter)

        # there was some reason we did this, however context.obj can
        # also be a property of the current section
        #if not context.obj is self._section:
        #    return

        if context.action == "remove":
            self.event_remove(context)

        if (context.action == "append" or context.action == "insert") and context.postChange:
            self.event_insert(context)

    def destroy(self):
        self._section._Changed -= self.on_section_changed


    @property
    def section(self):
        return self._section
