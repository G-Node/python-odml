import gtk
import commands

class TreeView(object):
    """
    Covers basic tasks of Treeview objects
    """
    popup = None

    def __init__(self, store=None):
        tv = gtk.TreeView(store)
        tv.set_headers_visible(False)

        renderer = gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.on_edited, None)

        if self.on_selection_change is not None:
            selection = tv.get_selection()
            selection.set_mode(gtk.SELECTION_BROWSE)
            selection.connect("changed", self.on_selection_change)

        if self.on_button_press is not None:
            tv.connect("button_press_event", self.on_button_press)

        tv.set_headers_visible(True)
        tv.set_rules_hint(True)

        self._treeview = tv

    def add_column(self, name, edit_func=None, id=0, data=0):
        renderer = gtk.CellRendererText()
        if edit_func:
            renderer.set_property("editable", True)
            renderer.connect("edited", edit_func, data)

        column = gtk.TreeViewColumn(name, renderer, text=id)
        self._treeview.append_column(column)
        return column

    def get_popup_menu(self):
        return None

    def on_button_press(self, widget, event):
        if event.button == 3: # right-click
            x = int(event.x)
            y = int(event.y)
            model = widget.get_model()
            path = widget.get_path_at_pos(x, y)
            obj = None

            if path:
                path, col, x, y = path
            else:
                path = ()

            if path:
                obj = model.on_get_iter(path)._obj

            self.popup_data = (model, path, obj)
            popup = self.get_popup_menu()
            if popup is not None:
                popup.popup(None, None, None, event.button, event.time)

    def on_edited(self, widget, path, new_value, data):
        """
        a user edited a value

        now callback another method with more meaningful information
        """
        model = self._treeview.get_model()
        gtk_tree_iter = model.get_iter(path)
        tree_iter = model.on_get_iter(model.get_path(gtk_tree_iter))
        return self.on_object_edit(tree_iter, data, new_value)

    def execute(self, cmd):
        cmd()

    on_selection_change = None

class TerminologyPopupTreeView(TreeView):
    def get_terminology_suggestions(self, obj, func):
        """
        return a list of objects

        return func(obj.terminology_equivalent())

        however if any result is None, return []
        """
        if obj is None: return []
        term = obj.get_terminology_equivalent()
        print "get term", obj, term
        if term is None: return []
        return func(term)

    def get_popup_menu(self):
        """
        create the popup menu for this object

        calls *get_popup_menu_items* to retrieve the actual
        items for the menu
        """
        print "term popup: get popup menu"
        popup = gtk.Menu()
        for i in self.get_popup_menu_items():
            popup.append(i)
            i.show()
        popup.show()
        return popup

    def get_popup_menu_items(self):
        """
        to be implemented by a concrete TreeView

        returns a list of gtk.MenuItem to be displayey in a popup menu
        """
        raise NotImplementedError

    def on_delete(self, widget, obj):
        """
        called for the popup menu action delete
        """
        cmd = commands.DeleteObject(obj=obj)
        self.execute(cmd)

    def create_popup_menu_del_item(self, obj):
        return self.create_menu_item("Delete %s" % repr(obj), self.on_delete, obj)

    def create_menu_item(self, name, func, data):
        item = gtk.MenuItem(name)
        item.connect('activate', func, data)
        item.show()
        return item

    def create_popup_menu_items(self, add_name, empty_name, obj, func, terminology_func, name_func):
        """
        create menu items for a popup menu

        * *add_name* is a menu item text e.g. ("Add Section")
        * *empty_name* is a menu item text e.g. ("Empty Section")
        * *obj* is the parent object to which to add the data
        * *func* is the target function that is called upon click action:
            func(widget, (obj, val)) where *val* is the template value or None
        * *terminology_func* is passed to *get_terminology_suggestions* and used to extract the relevant
          suggestions of a terminology object (e.g. lambda section: section.properties)
        * *name_func* is a function the create a menu-item label from an object (e.g. lambda prop: prop.name)

        returns an array of gtk.MenuItem
        """
        add_section = gtk.MenuItem(add_name)
        add_section.show()

        terms = self.get_terminology_suggestions(obj, terminology_func)
        if len(terms) == 0:
            add_section.connect('activate', func, (obj, None))
            return [add_section]

        menu = gtk.Menu()
        terms = [(name_func(sec), sec) for sec in terms]
        for name, val in [(empty_name, None), (None, None)] + terms:
            menu.append(self.create_menu_item(name, func, (obj, val)))

        menu.show()
        add_section.set_submenu(menu)
        return [add_section]
