import gtk

import commands
from ScrolledWindow import ScrolledWindow
from TreeView import TreeView
COL_PATH = 0
COL_DESC = 1
class ValidationView(TreeView):
    """
    A two-columnn TreeView to display the validation errors
    """
    def __init__(self):
        self._store = gtk.ListStore(str, str)

        super(ValidationView, self).__init__(self._store)

        for i, name in ((COL_PATH, "Path"), (COL_DESC, "Description")):
            self.add_column(name=name, data=i, id=i)

        tv = self._treeview
        tv.show()

    def set_errors(self, errors):
        self.errors = errors
        self.fill()

    def fill(self):
        self._store.clear()

        for err in self.errors:
            self._store.append([err.obj.get_path(), err.msg])

    def on_selection_change(self, tree_selection):
        """
        select the corresponding object in the editor upon a selection change
        """
        (model, tree_iter) = tree_selection.get_selected()
        (row,) = self._store.get_path(tree_iter)
        self.on_select_object(self.errors[row].obj)

    def on_select_object(self, obj):
        raise NotImplementedError
                
class ValidationWindow(gtk.Window):
    def __init__(self, tab):
        super(ValidationWindow, self).__init__()
        self.tab = tab
        self.set_title("Validation errors in %s" % tab.get_name())
        self.set_default_size(400, 600)
        self.connect('destroy', self.on_close)

        self.tv = ValidationView()
        self.tv.on_select_object = tab.window.navigate
        self.tv.set_errors(tab.document.validation_result.errors)

        self.add(ScrolledWindow(self.tv._treeview))
        self.show_all()

    def on_close(self, window):
        self.tab.remove_validation()

    def execute(self, cmd):
        cmd()

if __name__=="__main__":
    from odml.validation import Validation
    from odml.tools.jsonparser import JSONReader

    class Tab: # a small stupid mock object
        document = JSONReader().fromString("""
    {"_type": "Document", "section": [
        {"_type": "Section", "name": "sec1", "property": [
            {"_type": "Property", "name": "prop1", "value": [{"_type": "Value", "value": "1"}]},
            {"_type": "Property", "name": "prop1", "value": [{"_type": "Value", "value": "1"}]}
        ]}
    ]}
    """)
        def get_name(self):
            return "sample.odml"
        class window:
            navigate = None

    import odml.tools.dumper

    tab = Tab()
    tab.document.validation_result = Validation(tab.document)
    for err in tab.document.validation_result.errors:
        print err.obj.get_path(), err.msg
    x = ValidationWindow(tab)
    gtk.mainloop()
