import gtk
import commands
from TreeView import TreeView

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

    def set_model(self, model):
        self._treeview.set_model(model)

    def on_object_edit(self, tree_iter, attr, new_value):
        section = tree_iter._obj
        cmd = commands.ChangeValue(
            value     = section,
            prop      = "name",
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
