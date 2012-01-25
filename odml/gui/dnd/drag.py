import gtk

class DragTarget(object):
    """
    A DragTarget supports a certain mime type and has methods to figure out if
    a drag is possible as well as to retrieve the actual text-data representation
    for the drag
    """
    app = 0
    widget = 0
    actions = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK

    def get_data(self, widget, context):
        """
        called when the destination requests the data

        may also be called to find out if a particular widget state (selection)
        supports this target as a drag source. In this case, context will be
        None
        """
        raise NotImplementedError

    def delete_data(self, widget, context):
        """
        called when the drag operation finished and the destination requests
        to delete the original data
        """
        pass
