import gtk
import gobject

class NavigationBar(gtk.Label):
    def __init__(self, *args, **kargs):
        super(NavigationBar, self).__init__(*args, **kargs)
        self._document = None
        self.show()
        self.set_use_markup(True)
        self.set_justify(gtk.JUSTIFY_RIGHT)
        self.set_alignment(1, 0.9) # all free space left, and most top of widget
        self.connect("activate-link", self.switch)
        self.possible_move = None

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, doc):
        if self._document is not None:
            self._document._Changed -= self.on_section_changed

        self._document = doc
        self.set_model(doc)
        doc._Changed += self.on_section_changed

    @property
    def current_object(self):
        return self._current_object

    @current_object.setter
    def current_object(self, obj):
        self._current_object = obj
        self.update_display()
        self.on_selection_change(obj)

    def switch(self, widget, path):
        """called if a link in the property_status Label widget is clicked"""
        if path:
            path = [int(i) for i in path.split(":")]
            obj = self._document.from_path(path)
        else:
            obj = self._document
        self.current_object = obj
        return True

    def set_model(self, obj):
        """
        show the hierarchy for object *obj* and make
        it the selected one
        """
        self._current_hierarchy = [obj]

        cur = obj
        while hasattr(obj, "parent") and obj.parent is not None:
            obj = obj.parent
            self._current_hierarchy.append(obj)

        self.current_object = cur

    def update_display(self):
        names = []
        cur = self._current_object
        for obj in self._current_hierarchy:
            name = "Document" #repr(obj).replace("<", "[")
            if hasattr(obj, "name"):
                name = obj.name
            elif hasattr(obj, "value"):
                name = obj.value

            names.append(
                ( ("<b>%s</b>" if obj == cur else "%s") % name,
                  ":".join([str(i) for i in obj.to_path()])) )

        self.set_markup(": ".join(
            ['<a href="%s">%s</a>' % (path, name) for name, path in names[::-1]]
            ) + " ")

    def on_selection_change(self, obj):
        """
        called whenever this widget elects a new current obj
        """
        raise NotImplementedError

    def on_section_changed(self, context):
        """
        this is called by the Eventable modified MixIns of Value/Property/Section
        and causes the GUI to refresh correspondingly
        """
        print "change event(document): ", context

        # we are only interested in changes on sections
        if context.cur is not self._document: return

        if context.action == "set" and context.postChange:
            name, val = context.val
            if name != "name": return

            for obj in self._current_hierarchy:
                if context.obj is obj:
                    self.update_display()

        if context.action == "remove" and context.postChange:
            # an object is removed, two reasons possible:
            # a) move (an append-action will take care of everything later, however we don't know yet)
            # b) remove
            for obj in self._current_hierarchy:
                if context.val is obj:
                    self.possible_move = (obj, self.current_object)
                    self.set_model(context.obj) # set the view to the parent

        if (context.action == "append" or context.action == "insert") and context.postChange:
            if self.possible_move is None: return
            obj, cur = self.possible_move
            if context.val is obj:
                self.set_model(cur)
            self.possible_move = None

