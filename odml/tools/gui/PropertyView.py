import gtk
from ... import format
import commands

COL_KEY = 0
COL_VALUE = 1
class PropertyView():
    """
    A key-value ListStore based TreeView
    
    showing properties and allows to edit them
    based on the format-description of the obj's class
    """
    def __init__(self, obj=None):
        self._store = gtk.ListStore(str, str)
        self._store.set_sort_column_id(COL_KEY, gtk.SORT_ASCENDING)
        if obj is not None:
            self.set_model(obj)
        tv = gtk.TreeView(self._store)

        for i, name in ((COL_KEY, "Property"), (COL_VALUE, "Value")):
            renderer = gtk.CellRendererText()
            column   = gtk.TreeViewColumn(name, renderer, text=i)
            if i == COL_VALUE:
                renderer.connect("edited", self.on_edited, i)
                renderer.set_property("editable", True)
            column.set_sort_column_id(i)
            tv.append_column(column)
        
        tv.set_headers_visible(True)
        tv.set_rules_hint(True)
        tv.set_visible(True)
        self._treeview = tv
        #self._treeview.connect("edited", self.on_edited)
    
    def set_model(self, obj):
        self._model = obj
        self._fmt   = obj._format
        self.fill()
    
    def fill(self):
        self._store.clear()
        
        for k in self._fmt._args:
            v = getattr(self._model, self._fmt.map(k))
            if not isinstance(v, list):
                self._store.append([k, v])

    def on_edited(self, widget, row, new_value, col):
        print "edit:", widget, row, col, new_value
        #if col == COL_KEY: return False # cannot edit keys!
        store = self._store
        iter = store.get_iter(row)
        k = store.get_value(iter, COL_KEY)
        cmd = commands.ChangeValue(
            value     = self._model,
            prop      = self._fmt.map(k),
            new_value = new_value)

        def cmd_action(undo=False):
            new_value = getattr(cmd.value, cmd.prop)
            store.set_value(iter, COL_VALUE, new_value)

        cmd.on_action = cmd_action

        # TODO call one level higher to execute the command
        # TODO ... .execute(cmd)
