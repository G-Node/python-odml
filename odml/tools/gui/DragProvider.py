import gtk

class DragProvider(object):
    drag_targets = []
    drop_targets = []
    DROP_TARGET_MODIFIER = 0x800000

    def __init__(self, widget):
        self.widget = widget
        self.connect()
        # TODO params to allow copy and move

    def connect(self):
        tv = self.widget
        # TODO make this customizeable, allow LINK action
        SOURCE_ACTIONS = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_DEFAULT
        DEST_ACTIONS = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_DEFAULT

        # first enable tree model drag/drop (to get the actual row as drag_icon)
        # however this alone will only work for TreeStore/ListStore,
        # so we need to manage drag and drop by hand due to the GenericTreeModel
        tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                    self.drag_targets,
                                    SOURCE_ACTIONS)
        tv.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                    self.drag_targets,
                                    SOURCE_ACTIONS)
        tv.enable_model_drag_dest(self.drop_targets, DEST_ACTIONS)
        tv.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                         self.drop_targets,
                         DEST_ACTIONS)

        #tv.connect("drag_begin", self.drag_begin)
        tv.connect("drag-data-get", self._on_drag_get_data)
        tv.connect("drag-data-received", self._on_drag_received_data)
        tv.connect("drag-data-delete", self._on_drag_delete_data)
        #tv.connect('drag_motion', self._on_drag_motion)
        tv.connect('drag_drop', self._on_drag_drop)

    def add_mime_type(self, string, flags=0, allow_drag=True, allow_drop=True):
        """
        Add a mime type, that this widgets can drag and drop with
        """
        if allow_drag:
            self.drag_targets.append((string, flags, len(self.drag_targets)))
        if allow_drop:
            self.drop_targets.append((string, flags, len(self.drop_targets) | self.DROP_TARGET_MODIFIER))

        self.connect()

    def get_data(self, mime, model, iter):
        """
        Returns the data for the selected node and mime type
        """
        return model.get_value(iter, 0)

    def get_mime_type(self, index):
        """
        Returns the mime type for a certain target index (target_id)
        """
        if (index & self.DROP_TARGET_MODIFIER) == 0:
            return self.drag_targets[index][0]
        else:
            return self.drop_targets[index & (~self.DROP_TARGET_MODIFIER)][0]

    def _on_drag_get_data(self, widget, context, selection, target_id,
                           etime):
        """callback function to put data into dnd-selection"""
        treeselection = widget.get_selection()
        model, iter = treeselection.get_selected()
        action = context.suggested_action
        mime = self.get_mime_type(target_id)
        data = self.get_data(mime, model, iter)
        print action, "setting data", data
        if mime == "TEXT": # so type will be COMPOUND_TEXT whatever foo?
            selection.set_text(data, -1)
        else:
            selection.set(selection.target, 8, data)
        return True

    def can_handle_data(self, mime_types):
        """
        Returns True if the widget accepts this mime_type
        and False otherwise
        """
        # TODO this should also have the data, so it can actually
        # be checked, whether its text makes some sense
        return True

    def receive_data(self, mime, action, data, model, iter, position):
        """
        Retrieves the string data of a certain mime-type for a model

        * iter may be None
        * position refers to a insert-position such as gtk.TREE_VIEW_DROP_BEFORE

        returns True on a successful drop operation, False otherwise
        """
        return False

    def _on_drag_received_data(self, treeview, context, x, y, selection,
                                target_id, etime):
        """callback function for received data upon dnd-completion"""
        self.context = context
        model = treeview.get_model()
        data = selection.data
        mime = self.get_mime_type(target_id)
        action = context.action
        drop_info = treeview.get_dest_row_at_pos(x, y)
        treeview.emit_stop_by_name('drag-data-received')

        if not drop_info:
            ret = self.receive_data(mime, action, data, model, None, 0)
        else:
            path, position = drop_info
            iter = model.get_iter(path)
            ret = self.receive_data(mime, action, data, model, iter, position)

        ret = bool(ret)
        # only delete successful move actions
        delete = ret and action == gtk.gdk.ACTION_MOVE
        context.finish(ret, delete, etime)

    def _on_drag_drop(self, widget, context, x, y, time):
        """
        Determine if drop is allowed?
        """
        widget.emit_stop_by_name('drag-drop')
        return self.can_handle_data(context.targets)
        # TODO this is not yet completely understood
        #if 'gaphor/element-id' in context.targets:
        #    self._on_drag_get_data(context, context.targets[-1], time)
        #    return True
        #return False

    def delete_data(self, site):
        # TODO not implemented to be called
        pass

    def _on_drag_delete_data(self, widget, context):
        """
        Delete data from original site, when `ACTION_MOVE` is used.
        """
        widget.emit_stop_by_name('drag-data-delete')
        self.delete_data(None) # TODO find useful parameters

    def _on_drag_motion(self, widget, context, x, y, time):
        try:
            path, pos = widget.get_dest_row_at_pos(x, y)
            widget.set_drag_dest_row(path, pos)
        except TypeError:
            widget.set_drag_dest_row(len(widget.get_model()) - 1, gtk.TREE_VIEW_DROP_AFTER)

        kind = gtk.gdk.ACTION_COPY

        context.drag_status(kind, time)
        return False

