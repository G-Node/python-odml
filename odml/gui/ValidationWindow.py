import gtk

import commands
from ScrolledWindow import ScrolledWindow
from TreeView import TreeView
COL_PATH = 0
COL_INDEX = 1
COL_DESC = 2
class ValidationView(TreeView):
    """
    A two-columnn TreeView to display the validation errors
    """
    def __init__(self):
        self._store = gtk.ListStore(str, int, str)

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

        elements = [(err.path, j, err.msg, err.is_error) for j,err in enumerate(self.errors)]
        elements.sort()
        for (path, idx, msg, is_error) in elements:
            if not is_error:
                path = "<span foreground='darkgrey'>%s</span>" % path
            msg = u"<span foreground='%s'>\u26A0</span> " % ("red" if is_error else "orange") + msg
            self._store.append((path, idx, msg))

    def on_selection_change(self, tree_selection):
        """
        select the corresponding object in the editor upon a selection change
        """
        (model, tree_iter) = tree_selection.get_selected()
        index = self._store.get_value(tree_iter, COL_INDEX)
        self.on_select_object(self.errors[index].obj)

    def on_select_object(self, obj):
        raise NotImplementedError
                
class ValidationWindow(gtk.Window):
    max_height = 600
    max_width  = 800
    height = max_height
    width = max_width
    def __init__(self, tab):
        super(ValidationWindow, self).__init__()
        self.tab = tab
        self.set_title("Validation errors in %s" % tab.get_name())
        
        self.connect('delete_event', self.on_close)

        self.tv = ValidationView()
        self.tv.on_select_object = tab.window.navigate
        self.tv.set_errors(tab.document.validation_result.errors)

        self.add(ScrolledWindow(self.tv._treeview))
        width, height = self.tv._treeview.size_request()
        width  = min(width+10,  max(self.width,  self.max_width))
        height = min(height+10, max(self.height, self.max_height))
        self.set_default_size(width, height)

        self.show_all()

    def on_close(self, window, data=None):
        ValidationWindow.width, ValidationWindow.height = self.get_size()
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
        print err.path, err.msg
    x = ValidationWindow(tab)
    gtk.mainloop()
