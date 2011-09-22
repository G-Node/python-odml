import gtk
import gio

import odml
from odml.tools.xmlparser import XMLWriter, XMLReader

from CommandManager import CommandManager

class EditorTab(object):
    """
    Represents a Document Object in the Editor
    """
    file_uri = None
    edited = 0

    def __init__(self, window):
        cmdm = CommandManager()
        cmdm.enable_undo = self.enable_undo
        cmdm.enable_redo = self.enable_redo
        cmdm.error_func  = window.command_error
        self.command_manager = cmdm
        self.document = None
        self.window = window

    def new(self):
        """
        initialize a new document
        """
        doc = odml.doc.Document()
        sec = odml.section.Section(name="Default Section")
        doc.append(sec)

        self.document = doc
        self.file_uri = None

    def load(self, uri):
        self.file_uri = uri
        xml_file = gio.File(uri)
        self.document = XMLReader(ignore_errors=True).fromFile(xml_file.read())
        self.document.finalize()
        self.window._info_bar.show_info("Loading of %s done!" % (xml_file.get_basename()))
        # TODO select default section

    def reset(self):
        self.edited = 0 # initialize the edit stack position
        self.command_manager.reset()
        self.enable_undo(enable=False)
        self.enable_redo(enable=False)

    @property
    def is_modified(self):
        return self.edited != len(self.command_manager)

    def save_if_changed(self):
        """
        if the document was modified, ask the user if he or she wants to save the document

        returns false if the user cancelled the action
        """
        if not self.is_modified: return True

        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                                   "%s has been modified. Do you want to save your changes?" % self.file_uri)

        dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dialog.set_title("Save changes?")
        dialog.set_default_response(gtk.RESPONSE_CANCEL)

        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_CANCEL: return False
        if response == gtk.RESPONSE_NO: return True
        return window.save(None)

    def save(self, uri):
        self.document.clean()
        doc = XMLWriter(self.document)
        gf = gio.File(uri)
        try:
            data = unicode(doc)
        except Exception, e:
            self._info_bar.show_info("Save failed: %s" % e.message)
            return
        xml_file = gf.replace(etag='', make_backup=False) # TODO make backup?
        xml_file.write(doc.header)
        xml_file.write(data)
        xml_file.close()
        self.document.finalize() # undo the clean
        self.window._info_bar.show_info("%s was saved" % (gf.get_basename()))
        self.edited = len(self.command_manager)
        return True # TODO return false on any error and notify the user

    def enable_undo(self, enable=True):
        if self.window._current_tab is self:
            self.window.enable_undo(enable)

    def enable_redo(self, enable=True):
        if self.window._current_tab is self:
            self.window.enable_redo(enable)
