import gtk
import gobject

class EditorInfoBar(gtk.InfoBar):
    def __init__(self, *args, **kargs):
        gtk.InfoBar.__init__(self, *args, **kargs)
        self._msg_label = gtk.Label("")
        self._msg_label.show ()
        self.get_content_area ().pack_start (self._msg_label, True, True, 0)
        self.add_button (gtk.STOCK_OK, gtk.RESPONSE_OK)

        self.connect ("response", self._on_response)
        self._timerid = 0

    def _on_response(self, obj, response_id):
        if self._timerid > 0:
            gobject.source_remove (self._timerid)
            self._timerid = 0
        self.hide()

    def show_info (self, text):
        self._msg_label.set_text (text)
        self.set_message_type (gtk.MESSAGE_INFO)
        self.show ()
        self.add_timer()

    def show_question(self, text, resp):
        self._msg_label.set_text (text)
        self.set_message_type (gtk.MESSAGE_QUESTION)
        self.show ()

    def add_timer(self):
        self._timerid = gobject.timeout_add_seconds (3, self.on_timer)

    def on_timer(self):
        self.hide()
        self._timerid = 0
