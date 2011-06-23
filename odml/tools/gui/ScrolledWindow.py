import gtk

class ScrolledWindow(gtk.ScrolledWindow):
    def __init__(self, widget):
        super(ScrolledWindow, self).__init__()
        self.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.add(widget)
        self.show()
