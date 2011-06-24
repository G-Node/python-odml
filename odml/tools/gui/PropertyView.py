import gtk
from ... import format
import commands
from TreeView import TreeView
COL_KEY = 0
COL_VALUE = 1
class PropertyView(TreeView):
    """
    A key-value ListStore based TreeView

    showing properties and allows to edit them
    based on the format-description of the obj's class
    """
    def __init__(self, execute_func=lambda x: x(), obj=None):
        self.execute = execute_func
        self._store = gtk.ListStore(str, str)
        self._store.set_sort_column_id(COL_KEY, gtk.SORT_ASCENDING)
        if obj is not None:
            self.set_model(obj)

        super(PropertyView, self).__init__(self._store)

        for i, name in ((COL_KEY, "Property"), (COL_VALUE, "Value")):
            self.add_column(
                name=name,
                edit_func=self.on_edited if i == COL_VALUE else None,
                data=i,
                id=i)

        tv = self._treeview
        tv.show()

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
            object    = self._model,
            attr      = self._fmt.map(k),
            new_value = new_value)

        def cmd_action(undo=False):
            # TODO this needs actually be handle by a change listener on the model
            new_value = getattr(cmd.object, cmd.attr[0])
            store.set_value(iter, COL_VALUE, new_value)

        cmd.on_action = cmd_action

        self.execute(cmd)

