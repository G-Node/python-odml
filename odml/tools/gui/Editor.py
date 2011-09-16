import os
import sys

import gtk
import gobject
import gio

import odml
import odml.tools.treemodel.mixin
import commands

from odml.tools.treemodel import SectionModel, DocumentModel
from odml.tools.xmlparser import XMLWriter, XMLReader

from InfoBar import EditorInfoBar
from CommandManager import CommandManager
from ScrolledWindow import ScrolledWindow
from SectionView import SectionView
from PropertyView import PropertyView
from ValueView import ValueView
from NavigationBar import NavigationBar

gtk.gdk.threads_init()

ui_info = \
'''<ui>
  <menubar name='MenuBar'>
    <menu name='FileMenu' action='FileMenu'>
      <menuitem action='NewFile'/>
      <menuitem action='FileOpen'/>
      <menuitem action='OpenRecent' />
      <menuitem name='Save' action='Save' />
      <separator/>
      <menuitem action='Quit'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='VisitHP'/>
      <separator/>
      <menuitem action='About'/>
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem name='New' action='NewFile' />
    <toolitem name='Open' action='OpenRecent' />
    <toolitem name='Save' action='Save' />
    <toolitem name='Undo' action='Undo' />
    <toolitem name='Redo' action='Redo' />
  </toolbar>
</ui>'''


license_lgpl = \
    '''This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with the Gnome Library; see the file COPYING.LIB.  If not,
write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.\n'''

class Editor(gtk.Window):
    odMLHomepage = "http://www.g-node.org/projects/odml"
    file_uri = None
    _prop_model = None
    _current_property_object = None
    edited = False

    def __init__(self, filename=None, parent=None):
        cmdm = CommandManager()
        cmdm.enable_undo = self.enable_undo
        cmdm.enable_redo = self.enable_redo
        cmdm.error_func  = self.command_error
        self.command_manager = cmdm

        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('delete-event', self.quit)

        self.set_title("odML Editor")
        self.set_default_size(800, 600)

        icons = load_icon_pixbufs()
        self.set_icon_list(*icons)

        merge = gtk.UIManager()
        self.set_data("ui-manager", merge)
        merge.insert_action_group(self.__create_action_group(), 0)
        self.add_accel_group(merge.get_accel_group())

        self.reset_editor()

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except gobject.GError, msg:
            print "building menus failed: %s" % msg
        bar = merge.get_widget("/MenuBar")
        bar.show()

        table = gtk.Table(2, 6, False)
        self.add(table)

        table.attach(bar,
                     # X direction #          # Y direction
                     0, 2,                      0, 1,
                     gtk.EXPAND | gtk.FILL,     0,
                     0,                         0);

        bar = merge.get_widget("/ToolBar")
        bar.set_tooltips(True)
        bar.show()
        table.attach(bar,
                     # X direction #       # Y direction
                     0, 1,                   1, 2,
                     gtk.EXPAND | gtk.FILL,  0,
                     0,                      0)

        tool_button = merge.get_widget("/ToolBar/Open")
        tool_button.connect("clicked", self.open_file)
        tool_button.set_arrow_tooltip_text("Open a recently used file")
        tool_button.set_label("Open")
        tool_button.set_tooltip_text("Open Files")

        navigation_bar = NavigationBar()
#        table.attach(navigation_bar,
#                     # X direction           Y direction
#                     1, 2,                   1, 2,
#                     0,                      0,
#                     0,                      0)
        navigation_bar.on_selection_change = self.on_navigate
        self._navigation_bar = navigation_bar

        # schematic organization
        #  -vpaned---------------------------
        # | -hpaned-----+-------------------
        # ||            | -property_view(vbox)
        # || scrolled:  | | info_bar
        # ||  section_tv| +----------------
        # ||            | | scrolled: property_tv
        # ||            | \----------------
        # |\------------+-------------------
        # +----------------------------------
        # |  --frame: navigation bar -------
        # | +-------------------------------
        # | | scrolled: _property_view
        # | \-------------------------------
        # \----------------------------------
        hpaned = gtk.HPaned()
        hpaned.show()
        hpaned.set_position(150)

        section_tv = SectionView()
        section_tv.execute = cmdm.execute
        section_tv.on_section_change = self.on_section_change
        section_view = gtk.VBox(homogeneous=False, spacing=0)
        section_view.pack_start(ScrolledWindow(section_tv._treeview), True, True, 1)
        section_view.show()
        hpaned.add1(section_view)

        property_tv = ValueView(self.command_manager.execute)
        property_tv.execute = cmdm.execute
        property_tv.on_property_select = self.on_object_select
        property_view = gtk.VBox(homogeneous=False, spacing=0)

        info_bar = EditorInfoBar ()
        self._info_bar = info_bar
        property_view.pack_start(info_bar, False, False, 1)

        property_view.pack_start(ScrolledWindow(property_tv._treeview), True, True, 1)
        hpaned.add2(property_view)

        self._property_tv = property_tv
        self._section_tv = section_tv

        # property_view to edit ODML-Properties

        # to edit properties of Document, Section or Property:
        self._property_view = PropertyView(self.command_manager.execute)
        frame = gtk.Frame()
        frame.set_label_widget(navigation_bar)
        frame.add(ScrolledWindow(self._property_view._treeview))
        frame.show()

        vpaned = gtk.VPaned()
        vpaned.show()
        vpaned.set_position(350)
        vpaned.pack1(hpaned, resize=True, shrink=False)
        vpaned.pack2(frame, resize=False, shrink=True)

        table.attach (vpaned,
                      # X direction           Y direction
                      0, 2,                   3, 4,
                      gtk.EXPAND | gtk.FILL,  gtk.EXPAND | gtk.FILL,
                      0,                      0)

        statusbar = gtk.Statusbar()
        table.attach(statusbar,
                     # X direction           Y direction
                     0, 2,                   5, 6,
                     gtk.EXPAND | gtk.FILL,  0,
                     0,                      0)
        self._statusbar = statusbar
        statusbar.show()

        if not filename is None:
            self.load_document(filename)
        else:
            self._info_bar.show_info("Welcome to the G-Node odML Editor 0.1")

        self.show_all()

    def __create_action_group(self):
        entries = (
              ( "FileMenu", None, "_File" ),               # name, stock id, label */
              ( "OpenMenu", None, "_Open" ),               # name, stock id, label */
              ( "HelpMenu", None, "_Help" ),               # name, stock id, label */
              ( "NewFile", gtk.STOCK_NEW,                  # name, stock id */
                "_New", "<control>N",                      # label, accelerator */
                "Create a new document",                   # tooltip */
                self.new_file ),
              ( "FileOpen", gtk.STOCK_OPEN,                # name, stock id */
                "_Open", None,                             # label, accelerator */
                "Open a File",                             # tooltip */
                self.open_file ),
              ( "Save", gtk.STOCK_SAVE,                    # name, stock id */
                "_Save", None,                             # label, accelerator */
                "Save the current file",                   # tooltip */
                self.save ),
              ( "Quit", gtk.STOCK_QUIT,                    # name, stock id */
                "_Quit", "<control>Q",                     # label, accelerator */
                "Quit",                                    # tooltip */
                self.quit ),
              ( "Undo", gtk.STOCK_UNDO,                    # name, stock id */
                "_Undo", "<control>Z",                     # label, accelerator */
                "Undo last editing action",                # tooltip */
                self.undo ),
              ( "Redo", gtk.STOCK_REDO,                    # name, stock id */
                "_Redo", "<control>Y",                     # label, accelerator */
                "Redo an undone editing action",           # tooltip */
                self.redo ),
              ( "About", None,                             # name, stock id */
                "_About", "",                    # label, accelerator */
                "About",                                   # tooltip */
                self.activate_action ),
              ( "VisitHP", None,                           # name, stock id */
                "Visit Homepage", "",                      # label, accelerator */
                "Go to the odML Homepage",                 # tooltip */
                self.on_visit_homepage ),
              )

        recent_action = gtk.RecentAction ("OpenRecent",
                                          "Open Recent",
                                          "Open Recent Files",
                                          gtk.STOCK_OPEN)
        recent_action.connect ("item-activated", self.open_recent)

        recent_filter = gtk.RecentFilter()
        self._setup_file_filter (recent_filter)

        recent_action.set_sort_type (gtk.RECENT_SORT_MRU)
        recent_action.add_filter (recent_filter)
        recent_action.set_show_not_found (False)

        action_group = gtk.ActionGroup("EditorActions")
        self.editor_actions = action_group
        action_group.add_actions(entries)
        action_group.add_action(recent_action)
        return action_group

    def _setup_file_filter(self, filter):
        filter.set_name("odML documents (*.xml, *.odml)")
        filter.add_mime_type("application/xml")
        filter.add_mime_type("text/xml")
        filter.add_pattern('*.xml')
        filter.add_pattern('*.odml')

    def activate_action(self, action):
        logo = self.render_icon("odml-logo", gtk.ICON_SIZE_DIALOG)

        dialog = gtk.AboutDialog()
        dialog.set_name("odMLEditor")
        dialog.set_copyright("\302\251 Copyright 2010-2011 G-Node")
        dialog.set_authors([
            "Christian Kellner <kellner@bio.lmu.de>",
            "Hagen Fritsch <fritsch+odml@in.tum.de>",
            ])
        dialog.set_website(Editor.odMLHomepage)
        dialog.set_license (license_lgpl)
        dialog.set_logo(logo)

        dialog.set_transient_for(self)

        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

    def new_file(self, action):
        if not self.save_if_changed():
            return
        doc = odml.doc.Document()
        sec = odml.section.Section(name="Default Section")
        doc.append(sec)
        self._document = doc
        self.file_uri = None
        self.update_statusbar("<new file>")
        self.update_model()
        # TODO self.set_section(sec)
        self.edited = False

    def chooser_dialog(self, title, callback, save=False):
        default_button = gtk.STOCK_SAVE if save else gtk.STOCK_OPEN
        default_action = gtk.FILE_CHOOSER_ACTION_OPEN if save else gtk.FILE_CHOOSER_ACTION_SAVE
        chooser = gtk.FileChooserDialog(title="Open Document",
                                        parent=self,
                                        buttons=(default_button, gtk.RESPONSE_OK,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
                                        action=default_action)
        file_filter = gtk.FileFilter()
        self._setup_file_filter(file_filter)
        chooser.add_filter (file_filter)

        if not save:
            all_files = gtk.FileFilter()
            all_files.set_name ("All Files")
            all_files.add_pattern("*")
            chooser.add_filter (all_files)

        chooser.connect("response", callback)
        chooser.show()

    def open_file(self, action):
        """called to show the open file dialog"""
        if not self.save_if_changed():
            return False
        self.chooser_dialog(title="Open Document", callback=self.on_file_open)

    def on_file_open(self, chooser, response_id):
        if response_id == gtk.RESPONSE_OK:
            uri = chooser.get_uri()
            self.load_document(uri)
        chooser.destroy()

    def open_recent(self, recent_action):
        uri = recent_action.get_current_uri ()
        print 'open recent %s' % (uri)
        self.load_document (uri)

    def load_document(self, uri):
        self.file_uri = uri
        xml_file = gio.File(uri)
        self._document = XMLReader(ignore_errors=True).fromFile(xml_file.read())
        self._document.finalize()
        self._info_bar.show_info("Loading of %s done!" % (xml_file.get_basename()))
        self.set_status_filename()
        self.update_model()
        self.reset_editor()
        # TODO select default section

    def set_status_filename(self):
        self.update_statusbar("%s" % (self.file_uri))

    def reset_editor(self):
        self.edited = 0 # initialize the edit stack position
        self.command_manager.reset()
        self.enable_undo(enable=False)
        self.enable_redo(enable=False)

    def update_model(self):
        """updates the models if self._document changed"""
        model = None
        if self._document:
            model = DocumentModel.DocumentModel(self._document)

        self._section_tv.set_model(model)
        self._navigation_bar.document = self._document
        self._document_model = model
        # TODO select first section

    def save_if_changed(self):
        """
        if the document was modified, ask the user if he or she wants to save the document

        returns false if the user cancelled the action
        """
        if not self.edited: return True

        dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                                   "%s has been modified. Do you want to save your changes?" % self.file_uri)

        dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dialog.set_title("Save changes?")
        dialog.set_default_response(gtk.RESPONSE_CANCEL)

        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_CANCEL: return False
        if response == gtk.RESPONSE_NO: return True
        return self.save(None)

    def save(self, action):
        """
        called upon save_file action

        runs a file_chooser dialog if the file_uri is not set
        """
        if self.file_uri:
            return self.save_file(self.file_uri)
        self.chooser_dialog(title="Save Document", callback=self.on_file_save, save=True)
        return False # TODO this signals that file saving was not successful
                     #      because no action should be taken until the chooser
                     #      dialog is finish, however the user might then need to
                     #      repeat the action, once the document was saved and the
                     #      edited flag was cleared

    def on_file_save(self, chooser, response_id):
        if response_id == gtk.RESPONSE_OK:
            uri = chooser.get_uri()
            if not uri.lower().endswith('.odml') and \
                not uri.lower().endswith('.xml'):
                    uri += ".xml"
            self.file_uri = uri
            self.save_file(self.file_uri)
            self.set_status_filename()
        chooser.destroy()

    def save_file(self, uri):
        self._document.clean()
        doc = XMLWriter(self._document)
        gf = gio.File(uri)
        xml_file = gf.replace(etag='', make_backup=False) # TODO make backup?
        xml_file.write(doc.header)
        xml_file.write(unicode(doc))
        xml_file.close()
        self._document.finalize() # undo the clean
        self._info_bar.show_info("%s was saved" % (gf.get_basename()))
        self.edited = 0
        return True # TODO return false on any error and notify the user

    def quit(self, action, extra=None):
        if not self.save_if_changed(): return True # the event is handled and
                                                   # won't be passed to the window
        gtk.main_quit()

    # TODO should we save a navigation history here?
    def on_section_change(self, section):
        self._property_tv.section = section
        self.set_navigation_object(section)

    def on_object_select(self, obj):
        """an object has been selected, now fix the current property_view"""
        self.set_navigation_object(obj)

    def set_navigation_object(self, obj):
        """
        set a new item for the navigation bar
        """
        self._navigation_bar.set_model(obj)

    def on_navigate(self, obj):
        """
        update the property_view to work on object *obj*
        """
        self._property_view.set_model(obj)

    def update_statusbar(self, message, clear_previous=True):
        if clear_previous:
            self._statusbar.pop(0)
        self._statusbar.push(0, message)

    def visit_uri(self, uri, timestamp=None):
        if not timestamp:
            timestamp = gtk.get_current_event_time()
        gtk.show_uri(self.get_screen(), uri, timestamp)

    def on_visit_homepage(self, action):
        timestamp = None
        self.visit_uri(Editor.odMLHomepage, timestamp)

    def enable_action(self, action_name, enable):
        self.editor_actions.get_action(action_name).set_sensitive(enable)

    def enable_undo(self, enable=True):
        self.enable_action("Undo", enable)

    def enable_redo(self, enable=True):
        self.enable_action("Redo", enable)

    def undo(self, action):
        self.command_manager.undo()

    def redo(self, action):
        self.command_manager.redo()

    def command_error(self, cmd, error):
        self._info_bar.show_info("Editing failed: %s" % error.message)

def get_image_path():
    try:
        filename = "./odml-gui" #__main__.__file__
    except:
        filename = sys.argv[0]

    path = os.path.join(os.path.dirname(filename), 'images')
    other_paths = ['/usr/share/pixmaps', '/usr/local/share/pixmaps', 'share/pixmaps']
    while not os.path.exists(path):
        path = other_paths.pop()
    return path

def register_stock_icons():
    icons = [('odml-logo', '_odML', 0, 0, '')]
    gtk.stock_add(icons)

    # Add our custom icon factory to the list of defaults
    factory = gtk.IconFactory()
    factory.add_default()

    img_dir = get_image_path()
    img_path = os.path.join(img_dir, 'odMLIcon.png')

    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file(img_path)
        icon = pixbuf.add_alpha(False, chr(255), chr(255),chr(255))
        icon_set = gtk.IconSet(icon)

        for icon in load_icon_pixbufs():
            src = gtk.IconSource()
            src.set_pixbuf (icon)
            icon_set.add_source(src)

        factory.add('odml-logo', icon_set)

    except gobject.GError, error:
        print 'failed to load GTK logo for toolbar', error

def load_pixbuf(path):
    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        transparent = pixbuf.add_alpha(False, chr(255), chr(255),chr(255))
        return transparent
    except:
        return None

def load_icon_pixbufs():
    icons = []
    img_dir = get_image_path()
    files = os.listdir (img_dir)
    for f in files:
        if f.startswith("odMLIcon"):
            abs_path = os.path.join (img_dir, f)
            icon = load_pixbuf(abs_path)
            if icon:
                icons.append(icon)
    return icons

