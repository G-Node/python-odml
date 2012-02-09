import gtk

class ChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title, save):
        default_button = gtk.STOCK_SAVE if save else gtk.STOCK_OPEN
        default_action = gtk.FILE_CHOOSER_ACTION_SAVE if save else gtk.FILE_CHOOSER_ACTION_OPEN
        super(ChooserDialog, self).__init__(
                title=title,
                buttons=(default_button, gtk.RESPONSE_OK,
                         gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
                action=default_action)

        self.save = save
        self.connect('response', self.response)



    def response(self, widget, response_id):
        if response_id == gtk.RESPONSE_OK:
            self.on_accept(self.get_uri())
        self.destroy()

    def on_accept(self, uri):
        raise NotImplementedError

class odMLChooserDialog(ChooserDialog):
    def __init__(self, title, save):
        super(odMLChooserDialog, self).__init__(title, save)
        self.add_filters()

    @staticmethod
    def _setup_file_filter(filter):
        filter.set_name("odML documents (*.xml, *.odml)")
        filter.add_mime_type("application/xml")
        filter.add_mime_type("text/xml")
        filter.add_pattern('*.xml')
        filter.add_pattern('*.odml')

    def add_filters(self):
        file_filter = gtk.FileFilter()
        self._setup_file_filter(file_filter)
        self.add_filter (file_filter)

        if not self.save:
            all_files = gtk.FileFilter()
            all_files.set_name ("All Files")
            all_files.add_pattern("*")
            self.add_filter (all_files)
