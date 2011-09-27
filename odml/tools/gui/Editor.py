import os
import sys

import gtk
import gobject

import odml
import odml.tools.treemodel.mixin
import commands

from odml.tools.treemodel import SectionModel, DocumentModel

from InfoBar import EditorInfoBar
from ScrolledWindow import ScrolledWindow
from SectionView import SectionView
from PropertyView import PropertyView
from ValueView import ValueView
from NavigationBar import NavigationBar
from ChooserDialog import odMLChooserDialog
from EditorTab import EditorTab

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

class EditorWindow(gtk.Window):
    odMLHomepage = "http://www.g-node.org/projects/odml"

    def __init__(self, parent=None):
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
                     0, 2,                   1, 2,
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
        section_tv.execute = self.execute
        section_tv.on_section_change = self.on_section_change
        section_view = gtk.VBox(homogeneous=False, spacing=0)
        section_view.pack_start(ScrolledWindow(section_tv._treeview), True, True, 1)
        section_view.show()
        hpaned.add1(section_view)

        property_tv = ValueView(self.execute)
        property_tv.execute = self.execute
        property_tv.on_property_select = self.on_object_select
        property_view = gtk.VBox(homogeneous=False, spacing=0)

        info_bar = EditorInfoBar ()
        self._info_bar = info_bar
        property_view.pack_start(info_bar, False, False, 1)
        property_view.pack_start(ScrolledWindow(property_tv._treeview), True, True, 1)
        property_view.show()
        hpaned.add2(property_view)

        self._property_tv = property_tv
        self._section_tv = section_tv

        # property_view to edit ODML-Properties

        # to edit properties of Document, Section or Property:
        self._property_view = PropertyView(self.execute)
        frame = gtk.Frame()
        frame.set_label_widget(navigation_bar)
        frame.add(ScrolledWindow(self._property_view._treeview))
        frame.show()

        vpaned = gtk.VPaned()
        vpaned.show()
        vpaned.set_position(350)
        vpaned.pack1(hpaned, resize=True, shrink=False)
        vpaned.pack2(frame, resize=False, shrink=True)

        class Tab(gtk.HBox):
            """
            a tab container
            """
            child = vpaned

        self.Tab = Tab

        notebook = gtk.Notebook() # we want tabs
        notebook.connect("switch-page", self.on_tab_select)
        notebook.connect("create-window", self.on_new_tab_window)
        notebook.show()
        self.notebook = notebook

        table.attach (notebook,
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

        #if not filename is None:
        #    self.load_document(filename)
        #else:
        #    self._info_bar.show_info("Welcome to the G-Node odML Editor 0.1")
        #    self.new_file(None)

        self.show_all()

    def mktab(self, tab):
        t = self.Tab()
        t.tab = tab
        t.show()
        return t

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
        odMLChooserDialog._setup_file_filter(recent_filter)

        recent_action.set_sort_type (gtk.RECENT_SORT_MRU)
        recent_action.add_filter (recent_filter)
        recent_action.set_show_not_found (False)

        action_group = gtk.ActionGroup("EditorActions")
        self.editor_actions = action_group
        action_group.add_actions(entries)
        action_group.add_action(recent_action)
        return action_group

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

    def new_file(self, action=None):
        """open a new tab with an empty document"""
        tab = EditorTab(self)
        tab.new()
        self.append_tab(tab)
        return tab

    def load_document(self, uri):
        """open a new tab, load the document into it"""
        tab = EditorTab(self)
        tab.load(uri)
        self.append_tab(tab)
        return tab

    def clone_tab(self, tab, document=None):
        ntab = EditorTab(self, tab.command_manager)
        ntab.document = tab.document if document is None else document
        ntab.file_uri = tab.file_uri
        self.append_tab(ntab)
        return ntab

    def map_tab(self, tab):
        mapdoc = mapping.create_mapping(tab.document)
        ntab = self.clone_tab(tab, mapdoc)
        ntap.file_uri += ".mapped.odml"
        return ntab

    def select_tab(self, tab, force_reset=False):
        """
        activate a new tab, reset the statusbar and models accordingly
        """
        ctab = self.current_tab
        if not force_reset and ctab is tab: return

        if ctab is not None:
            ctab.state = self.get_tab_state()

        if not force_reset:
            self.current_tab = tab

        self.set_status_filename()
        self.update_model(tab)
        self.enable_undo(tab.command_manager.can_undo)
        self.enable_redo(tab.command_manager.can_redo)

        if hasattr(tab, "state"):
            self.set_tab_state(tab.state)

    @property
    def current_tab(self):
        page = self.notebook.get_current_page()
        child = self.notebook.get_nth_page(page)
        if child is not None:
            return child.tab

    @current_tab.setter
    def current_tab(self, tab):
        if self.current_tab is tab:
            return
        self.notebook.set_current_page(self.get_notebook_page(tab))

    def get_tab_state(self):
        state = self._section_tv.save_state(), self._property_tv.save_state() #, self._property_view.save_state()
        return state

    def set_tab_state(self, state):
        self._section_tv.restore_state(state[0])
        self._property_tv.restore_state(state[1])
        #self._property_view.restore_state(state[2])

    def get_notebook_page(self, tab):
        """
        returns the index holding *tab*
        """
        for i, child in enumerate(self.notebook):
            if child.tab is tab:
                return i

    def mk_tab_label(self, title, tab):
        #hbox will be used to store a label and button, as notebook tab title
        hbox = gtk.HBox(False, 0)
        label = gtk.Label(title)
        hbox.pack_start(label)

        #get a stock close button image
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)

        #make the close button
        btn = gtk.Button()
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_focus_on_click(False)
        btn.connect('clicked', self.on_tab_close_click, tab)
        btn.add(close_image)
        hbox.pack_start(btn, False, False)

        #this reduces the size of the button
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        btn.modify_style(style)

        hbox.show_all()
        return hbox

    def append_tab(self, tab):
        """
        append the tab to our tab list

        may replace the current tab, if its a new file that
        has not been edited
        """
        child = self.mktab(tab)
        self.notebook.append_page(child, self.mk_tab_label(str(tab.file_uri), tab))
        self.notebook.set_tab_reorderable(child, True)
        self.notebook.set_tab_detachable(child, True)
        self.notebook.set_show_tabs(self.notebook.get_n_pages() > 1)

    def close_tab(self, tab, save=True):
        """
        try to save and then remove the tab from our tab list
        and remove the tab from the Notebook widget
        """
        if save and not tab.save_if_changed():
            return # action canceled

        idx = self.get_notebook_page(tab)
        if self.notebook.get_n_pages() == 1:
            tab = self.new_file() # open a new tab already, so we never get empty

        self.notebook.remove_page(idx)
        self.notebook.set_show_tabs(self.notebook.get_n_pages() > 1)

    def on_tab_select(self, notebook, page, pagenum):
        """
        the notebook widget selected a tab
        """
        hbox = notebook.get_nth_page(pagenum)
        if hbox.child.get_parent() is None:
            hbox.add(hbox.child)
        else:
            hbox.child.reparent(hbox)
        self.select_tab(hbox.tab, force_reset=True)

    def on_tab_close_click(self, button, tab):
        self.close_tab(tab)

    def on_new_tab_window(self, notebook, page, x, y):
        """
        the tab so dropped to another window
        """
        editor = EditorWindow()
        tab = page.tab
        state = self.get_tab_state()
        tab.window = editor
        editor.append_tab(tab)
        editor.set_tab_state(state)
        self.close_tab(tab, save=False)
        return True

    def chooser_dialog(self, title, callback, save=False):
        chooser = odMLChooserDialog(title=title, save=save)
        chooser.on_accept = callback
        chooser.show()

    def open_file(self, action):
        """called to show the open file dialog"""
        self.chooser_dialog(title="Open Document", callback=self.load_document)

    def open_recent(self, recent_action):
        uri = recent_action.get_current_uri ()
        self.load_document(uri)

    def set_status_filename(self):
        filename = self.current_tab.file_uri
        if not filename:
            filename = "<new file>"
        self.update_statusbar(filename)

    def update_model(self, tab):
        """updates the models if a different tab is selected changed"""
        model = None
        if tab.document:
            model = DocumentModel.DocumentModel(tab.document)

        self._section_tv.set_model(model)
        # TODO restore selection/expansion if known in tab

        self._navigation_bar.document = tab.document
        # self._property_tv.set_model()
        # TODO restore selection/expansion if known in tab

    def save(self, action):
        """
        called upon save_file action

        runs a file_chooser dialog if the file_uri is not set
        """
        if self.current_tab.file_uri:
            return self.current_tab.save(self.current_tab.file_uri)
        self.chooser_dialog(title="Save Document", callback=self.on_file_save, save=True)
        return False # TODO this signals that file saving was not successful
                     #      because no action should be taken until the chooser
                     #      dialog is finish, however the user might then need to
                     #      repeat the action, once the document was saved and the
                     #      edited flag was cleared

    def on_file_save(self, uri):
        if not uri.lower().endswith('.odml') and \
            not uri.lower().endswith('.xml'):
                uri += ".xml"
        self.current_tab.file_uri = uri
        self.current_tab.save(uri)
        self.set_status_filename()

    def save_if_changed(self):
        """
        if any open document was modified, ask the user if he or she wants to save the document

        returns false if the user cancelled the action
        """
        for child in self.notebook:
            if not child.tab.save_if_changed(): return False
        return True

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
        self.current_tab.command_manager.undo()

    def redo(self, action):
        self.current_tab.command_manager.redo()

    def command_error(self, cmd, error):
        self._info_bar.show_info("Editing failed: %s" % error.message)

    def execute(self, cmd):
        self.current_tab.command_manager.execute(cmd)

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

