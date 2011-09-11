import gtk

#TODO build a GenericDragProvider and a TreeDragProvider
class DragProvider(object):
    DROP_TARGET_MODIFIER = 0x800000
    inspector = None

    SOURCE_ACTIONS = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK
    DEST_ACTIONS = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK

    def __init__(self, widget):
        self.widget = widget
        self.drag_targets = []
        self.drop_targets = []
        self.connect()
	tv = widget
        #tv.connect("drag_begin", self.drag_begin)
        tv.connect("drag-data-get", self._on_drag_get_data)
        tv.connect("drag-data-received", self._on_drag_received_data)
        tv.connect("drag-data-delete", self._on_drag_delete_data)
        tv.connect('drag_motion', self._on_drag_motion)
        tv.connect('drag_drop', self._on_drag_drop)
        # TODO params to allow copy and move

    def connect(self):
        tv = self.widget
        # TODO make this customizeable, allow LINK action

        # stuff that gtk shall do automatically
        GTK_HANDLERS = gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP

        # first enable tree model drag/drop (to get the actual row as drag_icon)
        # however this alone will only work for TreeStore/ListStore,
        # so we need to manage drag and drop by hand due to the GenericTreeModel
        tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                    self.drag_targets,
                                    self.SOURCE_ACTIONS)
        tv.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                    self.drag_targets,
                                    self.SOURCE_ACTIONS)
        tv.enable_model_drag_dest(self.drop_targets, self.DEST_ACTIONS)
        tv.drag_dest_set(0, # gtk.DEST_DEFAULT_ALL, # if DEFAULT_ALL is set, data preview won't work
                         self.drop_targets,
                         self.DEST_ACTIONS)


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
        if mime == "TEXT": # so type will be COMPOUND_TEXT whatever foo?
            selection.set_text(data, -1)
        else:
            selection.set(selection.target, 8, data)
        return True

    def get_suiting_target(self, context, widget):
        for (target, flags, id) in self.drop_targets:
            if target in context.targets:
                same_app = context.get_source_widget() is not None
                if flags & gtk.TARGET_SAME_APP != 0 and not same_app:
                    continue
                same_widget = context.get_source_widget() is widget
                if flags & gtk.TARGET_SAME_WIDGET != 0 and not same_widget:
                    continue
                # other flags? gtk.TARGET_OTHER_APP?
                return (target, flags)
        return None, 0

    def can_handle_data(self, widget, context, time):
        """
        Returns True if the widget accepts this drag and False
        otherwise. Uses context.drag_status(action, time) to force
        a certain action
        """
        target, flags = self.get_suiting_target(context, widget)
        if target is None:
            return False

        if context.suggested_action & self.DEST_ACTIONS != 0:
            context.drag_status(context.suggested_action, time)
        else:
            # TODO or do i have to select one explicitly?
            context.drag_status(self.DEST_ACTIONS, time)
        return True

    def receive_data(self, mime, action, data, model, iter, position):
        """
        Retrieves the string data of a certain mime-type for a model

        * iter may be None
        * position refers to a insert-position such as gtk.TREE_VIEW_DROP_BEFORE

        returns True on a successful drop operation, False otherwise
        """
        return False

    def preview(self, widget, context, target, callback, etime):
        """
        can be called to retrieve the dragged data in a drag-motion event
        """
        def inspector(context, data, time):
            ret = callback(context, data, time)
            self.inspector = None
            return ret
        self.inspector = inspector
        # if gtk.DEST_DEFAULT_ALL is set do:
        # widget.drag_dest_set(0, [], 0)
        widget.drag_get_data(context, target, etime)

    def _on_drag_received_data(self, treeview, context, x, y, selection,
                                target_id, etime):
        """callback function for received data upon dnd-completion"""
        data = selection.data
        treeview.emit_stop_by_name('drag-data-received')

        # if we want to preview the data in the drag-motion handler
        # we will call drag_get_data there which eventually calls this
        # method, however the context will not be the actual drop
        # operation, so we forward this to a callback function
        # that needs to be set up for this
        if self.inspector is not None:
            return self.inspector(context, data, etime)

        self.context = context
        model = treeview.get_model()
        mime = self.get_mime_type(target_id)
        action = context.action
        drop_info = treeview.get_dest_row_at_pos(x, y)

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
        target, flags = self.get_suiting_target(context, widget)
        if target is None: return False

        widget.drag_get_data(context, target, time)
        #return self.can_handle_data(context.targets)
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
        """
        here
        """
        widget.emit_stop_by_name('drag-motion')
        if not self.can_handle_data(widget, context, time):
            context.drag_status(0, time)
            return False

        # do the highlighting
        try:
            path, pos = widget.get_dest_row_at_pos(x, y)
            widget.set_drag_dest_row(path, pos)
        except TypeError:
            widget.set_drag_dest_row(len(widget.get_model()) - 1, gtk.TREE_VIEW_DROP_AFTER)
        return True
