import gtk
from dnd.drag import DragTarget
from dnd.drop import DropTarget

#TODO build a GenericDragProvider and a TreeDragProvider
class DragProvider(object):
    """
    A DragProvider handles complicated Drag&Drop interactions with multiple sources
    and targets.
    """
    inspector = None

    SOURCE_ACTIONS = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK
    DEST_ACTIONS = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK

    def __init__(self, widget):
        self.widget = widget
        self.drag_targets = []
        self.drop_targets = []
        self.connect()
        tv = widget
        tv.connect("drag_begin", self._on_drag_begin)
        tv.connect("drag-data-get", self._on_drag_get_data)
        tv.connect("drag-data-received", self._on_drag_received_data)
        tv.connect("drag-data-delete", self._on_drag_delete_data)
        tv.connect('drag_motion', self._on_drag_motion)
        tv.connect('drag_drop', self._on_drag_drop)

        tv.get_selection().connect('changed', self._on_selection_change)

    def connect(self):
        """
        connect the currently available targets to the drag and drop interface
        of gtk, also does some magic (that is not yet completely understood) so
        that the treeview uses approriate drag icons (row preview)

        this method is implicitly called by append()
        """
        tv = self.widget
        # TODO make this customizeable, allow LINK action

        # stuff that gtk shall do automatically
        GTK_HANDLERS = gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP

        drag_targets = []
        for i, target in enumerate(self.drag_targets):
            drag_targets.append((target.mime, target.app | target.widget, 1500+i))
        # first enable tree model drag/drop (to get the actual row as drag_icon)
        # however this alone will only work for TreeStore/ListStore,
        # so we need to manage drag and drop by hand due to the GenericTreeModel
        tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                    drag_targets,
                                    self.SOURCE_ACTIONS)
        tv.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                    drag_targets,
                                    self.SOURCE_ACTIONS)
        tv.enable_model_drag_dest([], self.DEST_ACTIONS)
        tv.drag_dest_set(0, # gtk.DEST_DEFAULT_ALL, # if DEFAULT_ALL is set, data preview won't work
                         [],
                         self.DEST_ACTIONS)


    def append(self, obj):
        """
        Add a mime type, that this widgets can drag and drop with
        """
        if isinstance(obj, DragTarget):
            self.drag_targets.append(obj)
        if isinstance(obj, DropTarget):
            self.drop_targets.append(obj)
        print self.drag_targets
        print self.drop_targets
        self.connect()

    def _on_drag_begin(self, widget, context):
        """
        save the current selection to the context
        """
        # this is tree-view specific
        try:
            context.set_data("org-selection", widget.get_selection().get_selected())
        except:
            pass

    def _on_selection_change(self, tree_selection):
        """
        the DragProvider listens to selection_change events as targets may be valid
        for a certain selection, but invalid for others. Thus we update the target
        list here. This cannot be done in drag_begin as there, the context is already
        completely established
        """
        drag_targets = []
        for i, target in enumerate(self.drag_targets):
            if target.get_data(self.widget, None) is not None:
                drag_targets.append((target.mime, target.app | target.widget, 1600+i))
        # first enable tree model drag/drop (to get the actual row as drag_icon)
        # however this alone will only work for TreeStore/ListStore,
        # so we need to manage drag and drop by hand due to the GenericTreeModel
        tv = self.widget
        tv.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                    drag_targets,
                                    self.SOURCE_ACTIONS)
        tv.drag_source_set(gtk.gdk.BUTTON1_MASK,
                                    drag_targets,
                                    self.SOURCE_ACTIONS)
        #print "resulting drag targets", drag_targets

    def get_source_target(self, context, mime):
        for target in self.drag_targets:
            if target.mime == mime:
                return target
        return None

    def _on_drag_get_data(self, widget, context, selection, info, etime):
        """
        called when the destination requests data from the source

        selects a target and fill the selection with the data provided
        by the target
        """
        target = self.get_source_target(context, selection.target)
        if not target:
            return False
        # save the selected target, so we can use it in the drag-delete event
        context.set_data("target", target.mime)

        data = target.get_data(widget, context)
        if target.mime == "TEXT": # so type will be COMPOUND_TEXT whatever foo?
            selection.set_text(data, -1)
        else:
            selection.set(selection.target, 8, data)
        return True

    def get_suiting_target(self, widget, context, x, y, data=None):
        """
        find a suiting target within the registered drop_targets
        that allows to drop
        """
        for target in self.drop_targets:
            if target.mime in context.targets:
                same_app = context.get_source_widget() is not None
                if target.app & gtk.TARGET_SAME_APP != 0 and not same_app:
                    continue
                if target.app & gtk.TARGET_OTHER_APP != 0 and same_app:
                    continue

                same_widget = context.get_source_widget() is widget
                if target.widget & gtk.TARGET_SAME_WIDGET != 0 and not same_widget:
                    continue
                if target.widget & gtk.TARGET_OTHER_WIDGET != 0 and same_widget:
                    continue

                if data is None and target.preview_required:
                    # we can potentially drop here, however need a data preview first
                    return target

                if target.can_drop(widget, context, x, y, data):
                    return target
        # no suitable target found
        return None

    def can_handle_data(self, widget, context, x, y, time, data=None):
        """
        Determines if the widget accepts this drag.
        Uses context.drag_status(action, time) to force a certain action.
        Note this always returns True and uses drag_status to indicate
        available actions (which may be none).

        If a target has the preview_required attribute set, a preview will be
        requested, so that the target can determine if it can drop the data.
        """
        target = self.get_suiting_target(widget, context, x, y, data)
        if target is None:
            # normally return false, however if a target is only valid at a certain
            # position, we want to reevaluate constantly
            context.drag_status(0, time)
            return True

        if data is None and target.preview_required:
            recv_func = lambda context, data, time: \
                self.can_handle_data(widget, context, x, y, time, data)
            self.preview(widget, context, target.mime, recv_func, time)
            return True

        if context.suggested_action & target.actions != 0:
            context.drag_status(context.suggested_action, time)
        else:
            # TODO or do i have to select one explicitly?
            context.drag_status(target.actions, time)
        return True

    def preview(self, widget, context, mime, callback, etime):
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
        widget.drag_get_data(context, mime, etime)

    def _on_drag_received_data(self, widget, context, x, y, selection,
                                target_id, etime):
        """callback function for received data upon dnd-completion"""
        data = selection.data
        widget.emit_stop_by_name('drag-data-received')

        # if we want to preview the data in the drag-motion handler
        # we will call drag_get_data there which eventually calls this
        # method, however the context will not be the actual drop
        # operation, so we forward this to a callback function
        # that needs to be set up for this
        if self.inspector is not None:
            return self.inspector(context, data, etime)

        target = self.get_suiting_target(widget, context, x, y, data)
        if target is None:
            return False

        self.context = context

        ret = bool(target.receive_data(widget, context, x, y, data, etime))
        # only delete successful move actions
        delete = ret and context.action == gtk.gdk.ACTION_MOVE
        context.finish(ret, delete, etime)

    def _on_drag_drop(self, widget, context, x, y, time):
        """
        User initiated drop action, return False if drop is not allowed
        otherwise request the data. The actual drop handling is then done
        in the _on_drag_receive_data function.
        """
        widget.emit_stop_by_name('drag-drop')
        target = self.get_suiting_target(widget, context, x, y)
        if target is None:
            return False

        widget.drag_get_data(context, target.mime, time)
        return True

    def _on_drag_delete_data(self, widget, context):
        """
        Delete data from original site, when `ACTION_MOVE` is used.
        """
        widget.emit_stop_by_name('drag-data-delete')
        # select the target based on the mime type we stored in the drag-get-data handler
        target = self.get_source_target(context, context.get_data("target"))
        cmd = target.delete_data(widget, context)
        if cmd:
            self.execute(cmd)

    def _on_drag_motion(self, widget, context, x, y, time):
        """
        figure out if a drop at the current coordinates is possible for any
        registered target
        """
        widget.emit_stop_by_name('drag-motion')
        if not self.can_handle_data(widget, context, x, y, time):
            context.drag_status(0, time)
            return False

        # do the highlighting
        # TODO: this is treeview dependent, move it to TreeDropTarget
        try:
            path, pos = widget.get_dest_row_at_pos(x, y)
            widget.set_drag_dest_row(path, pos)
        except TypeError:
            widget.set_drag_dest_row(len(widget.get_model()) - 1, gtk.TREE_VIEW_DROP_AFTER)
        return True
