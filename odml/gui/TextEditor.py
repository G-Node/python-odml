import gtk

import commands
from ScrolledWindow import ScrolledWindow

class TextEditor(gtk.Window):
    def __init__(self, obj, attr):
        super(TextEditor, self).__init__()
        self.obj = obj
        self.attr = attr
        self.set_title("Editing %s.%s" % (repr(obj), attr))
        self.set_default_size(400, 600)
        self.connect('destroy', self.on_close)

        self.text = gtk.TextView()
        buffer = self.text.get_buffer()
        buffer.set_text(getattr(obj, attr))

        #buffer.connect_object("changed", self.on_text_updated)
        #buffer.connect_object("mark_set", self.on_cursor_moved)
        self.add(ScrolledWindow(self.text))
        self.show_all()

    def on_close(self, window):
        import commands
        buffer = self.text.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end)
        cmd = commands.ChangeValue(object=self.obj, attr=self.attr, new_value=text)
        self.execute(cmd)

    def execute(self, cmd):
        cmd()

if __name__=="__main__":
    class A(object):
        _a = "no text"
        @property
        def a(self):
            print "read prop a"
            return self._a
        @a.setter
        def a(self, new_value):
            print "set a to ", repr(new_value)
            self._a = new_value

    x = TextEditor(A(), "a")
    gtk.mainloop()
