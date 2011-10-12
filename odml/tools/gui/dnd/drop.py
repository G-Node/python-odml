import gtk

class DropTarget(object):
    """
    A DropTarget supports a certain mime-type and is responsible for figuring
    out if a drop is possible at a certain position and to actually handle
    the drop with incoming text-data
    """
    app = 0
    widget = 0
    actions = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK
    preview_required = False

    def can_drop(self, widget, context, x, y, data=None):
        """
        returns True if a drop at these coordinates is possible

        if preview_required is True, data will contain the actual data to
        be dropped
        """
        return True

    def receive_data(self, widget, context, x, y, data, etime):
        """
        handles a drop operation at the given coordinates
        """
        raise NotImplementedError
