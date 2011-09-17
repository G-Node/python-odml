import gtk
import cgi
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
        self._model = None
        if obj is not None:
            self.set_model(obj)

        super(PropertyView, self).__init__(self._store)

        for i, name in ((COL_KEY, "Attribute"), (COL_VALUE, "Value")):
            self.add_column(
                name=name,
                edit_func=self.on_edited if i == COL_VALUE else None,
                data=i,
                id=i)

        tv = self._treeview
        tv.show()

    def set_model(self, obj):
        if self._model:
            self._model._Changed -= self.on_object_change
        obj._Changed += self.on_object_change

        self._model = obj
        self._fmt   = obj._format
        self.fill()

    def fill(self):
        self._store.clear()

        for k in self._fmt._args:
            v = getattr(self._model, self._fmt.map(k))
            if not isinstance(v, list):
                if v is not None:
                    v = cgi.escape(v)
                self._store.append([k, v])

    def on_edited(self, widget, row, new_value, col):
        print "edit:", widget, row, col, new_value
        store = self._store
        iter = store.get_iter(row)
        k = store.get_value(iter, COL_KEY)
        cmd = commands.ChangeValue(
            object    = self._model,
            attr      = self._fmt.map(k),
            new_value = new_value)

        self.execute(cmd)

    def on_object_change(self, context):
        """
        this change listener is attached to the current object class
        and updates the GUI elements upon relevant change events
        """
        if context.cur is self._model and context.postChange:
            self.fill()
