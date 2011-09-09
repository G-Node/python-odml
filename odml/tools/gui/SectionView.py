import gtk
import commands
from TreeView import TreeView
from DragProvider import DragProvider
from .. import xmlparser

class SectionDragProvider(DragProvider):
    def get_data(self, mime, model, iter):
        obj = model.get_object(iter)
        print (":get_data(%s)" % (mime)), repr(obj)
        if mime == "odml/section-path":
            return model.get_string_from_iter(iter) #':'.join(map(str, obj.to_path()))
        return unicode(xmlparser.XMLWriter(obj))

    def can_handle_data(self, mime_types):
        print ":can_handle_data", mime_types
        return True

    def receive_data(self, mime, action, data, model, iter, position):
        print ":receive_data(%s)" % mime
        if iter is None:
            iter = model.get_iter_root()
        dest = model.get_object(iter)

        copy = action == gtk.gdk.ACTION_COPY

        if mime == "odml/property-path":
            model = self.context.get_source_widget().get_model()
            data_iter = model.get_iter_from_string(data)
            data = model.get_object(data_iter)

            cmd = commands.CopyOrMoveObject(
                     obj=data,
                     dst=dest,
                     copy=copy)

        elif mime == "odml/section-path":
            data_iter = model.get_iter_from_string(data)
            data = model.get_object(data_iter)
            if position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_AFTER:
                dest = dest.parent
            else: # if position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
                pass

            cmd = commands.CopyOrMoveObject(
                     obj=data,
                     dst=dest,
                     copy=copy)
        else:
            print "unimplemented (from xml)", data
            raise NotImplementedError

        self.execute(cmd)

class SectionView(TreeView):
    """
    A key-value ListStore based TreeView

    showing properties and allows to edit them
    based on the format-description of the obj's class
    """
    def __init__(self):
        super(SectionView, self).__init__()
        self.add_column(name="Name", edit_func=self.on_edited)
        self._treeview.show()

        # set up our drag provider
        dp = SectionDragProvider(self._treeview)
        dp.add_mime_type('odml/section-path', flags=gtk.TARGET_SAME_WIDGET)
        dp.add_mime_type('odml/property-path', flags=gtk.TARGET_SAME_APP, allow_drag=False)
        dp.add_mime_type('TEXT', allow_drop=False)
        dp.add_mime_type('STRING', allow_drop=False)
        dp.add_mime_type('text/plain', allow_drop=False)
        dp.execute = lambda cmd: self.execute(cmd)

    def set_model(self, model):
        self._treeview.set_model(model)

    def on_object_edit(self, tree_iter, attr, new_value):
        section = tree_iter._obj
        cmd = commands.ChangeValue(
            object    = section,
            attr      = "name",
            new_value = new_value)

        self.execute(cmd)

    def on_selection_change(self, tree_selection):
        """
        the selection moved

        now callback another method with more meaningful information
        """
        (model, tree_iter) = tree_selection.get_selected()
        if not tree_iter:
            return

        return self.on_section_change(model.get_object(tree_iter))
