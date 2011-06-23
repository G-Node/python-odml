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

    def on_edited(self, widget, path, new_value, data):
        """
        a user edited a value

        now callback another method with more meaningful information
        """
        model = self._treeview.get_model()
        #tree_iter = store.get_iter(row)
        #path = model.get_path(tree_iter)
        path = map(int, path.split(':'))
        return self.on_section_edit(model, path, new_value)

    def on_section_edit(self, model, path, new_value):
        path = model.model_path_to_odml_path(path)
        print path

        section = model._document.from_path(path)
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
        path = model.get_path(tree_iter)
        return self.on_section_change(path)
