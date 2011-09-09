import gtk
import commands
from TreeView import TreeView
from DragProvider import DragProvider
from .. import xmlparser

class CopyOrMoveCommand(commands.Command):
    """
    CopyOrMoveCommand(obj=, dst=, copy=True/False)                            tv=TreeView,)
    """
    def __init__(self, *args, **kwargs):
        super(CopyOrMoveCommand, self).__init__(*args, **kwargs)
        cmd_class = commands.CopyObject if self.copy else commands.MoveObject
        self.cmd = cmd_class(obj=self.obj, dst=self.dst)

    def _execute(self):
        self.cmd()

    def _undo(self):
        self.cmd.undo()

class TreeCopyOrMoveCommand(CopyOrMoveCommand):
    """
    TreeMoveCommand(tv=, obj=, dst=, old_path=)

    Move an object backed by a tree-view
    """
    undo_state = None

    def saveExpandedLines(self):
        # TODO: this could be stored directly in the odml nodes
        #       restoring would then work even after the modification
       def checkLine(model, path, iter, data = None):
           if self.tv.row_expanded(path):
               expandedLines.append(path)

       expandedLines = []
       self.tv.get_model().foreach(checkLine)
       return expandedLines

    def restoreExpandedLines(self, expandedLines):
        def restoreLine(model, path, iter, data = None):
            if path in expandedLines:
                self.tv.expand_row(path, False)

        self.tv.get_model().foreach(restoreLine)

    def _execute(self):
        self.tv_state = self.saveExpandedLines()
        model = self.tv.get_model()
        self.tv.freeze_child_notify()
        self.tv.set_model(None)
        self.cmd()
        self.tv.set_model(model)
        self.tv.thaw_child_notify()
        if self.undo_state is not None:
            self.restoreExpandedLines(self.undo_state)
        else:
            if self.old_path[:-1]: # the parent of the old path will still be valid
                self.tv.expand_to_path(self.old_path[:-1]) # old parent
            new_path = model.odml_path_to_model_path(self.dst.to_path())
            self.tv.expand_to_path(new_path)

    def _undo(self):
        self.undo_state = self.saveExpandedLines()
        model = self.tv.get_model()
        self.tv.freeze_child_notify()
        self.tv.set_model(None)
        self.cmd.undo()
        self.tv.set_model(model)
        self.tv.thaw_child_notify()
        self.restoreExpandedLines(self.tv_state)

class PropertyCopyOrMoveCommand(CopyOrMoveCommand):
    """
    PropertyCopyOrMoveCommand(obj=, dst=, copy=True/False,
                            tv=TreeView,)
    """
    def __init__(self, *args, **kwargs):
        super(PropertyCopyOrMoveCommand, self).__init__(*args, **kwargs)
        self.parent = self.obj.parent

    def _execute(self):
        model = self.tv.get_model()
        if model.section is self.parent:
            # we are in the source-section and the row is to be removed
            # remember the path!
            path = model.get_node_path(self.obj)
        self.cmd() # run the actual move / copy command

        if model.section is self.dst:
            # we are viewing the destination section now
            model.post_insert(self.cmd.new_obj)

        if model.section is self.parent:
            # we are viewing the source section now
            model.post_delete(parent=self.dst, old_path=path)

    def _undo(self):
        model = self.tv.get_model()
        if model.section is self.dst:
            # we are in the dest-section and the row is to removed again
            # remember the path!
            path = model.get_node_path(self.cmd.new_obj)

        self.cmd.undo()

        if model.section is self.dst:
            model.post_delete(parent=self.parent, old_path=path)

        if model.section is self.parent:
            model.post_insert(self.obj)

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
            return self.dropProperty(model, data, dest, data_iter, iter, copy)

        if mime == "odml/section-path":
            data_iter = model.get_iter_from_string(data)
            data = model.get_object(data_iter)
            if position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_AFTER:
                dest = dest.parent
            else: # if position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
                pass
            return self.dropSection(model, data, dest, data_iter, iter, copy)
        else:
            print "unimplemented (from xml)", data
            raise NotImplementedError

    def dropSection(self, model, section, dest, section_iter, dest_iter, copy=False):
#        cmd = commands.MoveObject(
#            obj=data, dst=dest,
#            old_path  = model.get_path(data_iter),
#            dest_path = model.get_path(iter))

        # so the problem is, that we move a whole subtree
        # and thus have to tell the tree-model every row that has (or will be) deleted
        # so in effect this action should be caught by an move-event handler
        # causing the related events and thus updating the tree view

        # for now we don't care about model updating and just reset the
        # treeview und expand the related rows

        cmd = TreeCopyOrMoveCommand(
                obj=section, dst=dest, copy=copy,
                tv=self.widget,
                old_path=model.get_path(section_iter))

        cmd = CopyOrMoveCommand(
                 obj=section, dst=dest, copy=copy)

        self.execute(cmd)

    def dropProperty(self, model, prop, dest, prop_iter, dest_iter, copy=False):
        if copy:
            cmd = commands.CopyObject(obj=prop, dst=dest)
        else:
            cmd = commands.MoveObject(obj=prop, dst=dest)

        print prop
        print model.get_node_iter(prop)
        widget = self.context.get_source_widget()
        prop_path = model.get_path(model.get_node_iter(prop))
        prop_parent = prop.parent

        cmd = PropertyCopyOrMoveCommand(
                    obj=prop,
                    dst=dest,
                    tv =widget,
                    copy=copy)

        cmd = CopyOrMoveCommand(
                 obj=prop, dst=dest, copy=copy)
        print cmd
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
