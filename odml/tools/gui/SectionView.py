import gtk
import commands
from TreeView import TreeView
from DragProvider import DragProvider
from .. import xmlparser


class TreeMoveCommand(commands.MoveObject):
    """
    TreeMoveCommand(tv=, obj=, dst=)

    Move an object backed by a tree-view
    """
    undo_state = None

    def saveExpandedLines(self):
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
        super(TreeMoveCommand, self)._execute()
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
        super(TreeMoveCommand, self)._undo()
        self.tv.set_model(model)
        self.tv.thaw_child_notify()
        self.restoreExpandedLines(self.tv_state)

class SectionDragProvider(DragProvider):
    def get_data(self, mime, model, iter):
        obj = model.get_object(iter)
        print ":get_data(%s)" % (mime), obj
        if mime == "odml/object-path":
            return model.get_string_from_iter(iter) #':'.join(map(str, obj.to_path()))
        return unicode(xmlparser.XMLWriter(obj))

    def can_handle_data(self, mime_types):
        print ":can_handle_data", mime_types
        return True

    def receive_data(self, mime, data, model, iter, position):
        print ":receive_data(%s)" % mime
        if iter is None:
            iter = model.get_iter_root()
        dest = model.get_object(iter)
        if mime == "odml/object-path":
            data_iter = model.get_iter_from_string(data)
            data = model.get_object(data_iter)
        else:
            print "unimplemented (from xml)", data
            return False

        if position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_AFTER:
            dest = dest.parent
        else: # if position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
            pass

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

        cmd = TreeMoveCommand(
            tv = self.widget,
            obj=data, dst=dest,
            old_path  = model.get_path(data_iter),
            dest_path = model.get_path(iter))

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
        dp = SectionDragProvider(self._treeview)
        dp.add_mime_type('odml/object-path', gtk.TARGET_SAME_APP)
        dp.add_mime_type('TEXT')
        dp.add_mime_type('STRING')
        dp.add_mime_type('text/plain')
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
