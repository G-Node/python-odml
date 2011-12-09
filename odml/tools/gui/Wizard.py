#!/usr/bin/env python

import gtk
from ..treemodel.DocumentModel import DocumentModel
from SectionView import SectionView
from ScrolledWindow import ScrolledWindow
import odml
import odml.terminology as terminology

class Table(object):
    def __init__(self, cols):
        self.table = gtk.Table(rows=1, columns=cols)
        self.cols = cols
        self.rows = 0
    def append(self, fill=[], *cols):
        self.table.resize(rows=self.rows+1, columns=self.cols)
        for i,widget in enumerate(cols):
            xoptions = gtk.EXPAND | gtk.FILL if widget in fill else 0
            self.table.attach(widget, i, i+1, self.rows, self.rows+1, xoptions=xoptions)
        self.rows += 1

class Page(gtk.VBox):
    type = gtk.ASSISTANT_PAGE_CONTENT
    complete = True
    def __init__(self, *args, **kargs):
        super(Page, self).__init__(*args, **kargs)
        self.set_border_width(5)
        self.init()

    def init(self, *args, **kargs):
        """
        called in the beginning to perform additional initialization
        """
        pass

    def deploy(self, assistant, title):
        page = assistant.append_page(self)
        assistant.set_page_title(self, title)
        assistant.set_page_type(self, self.type)
        assistant.set_page_complete(self, self.complete)
        return page

    def prepare(self, assistant, prev_page):
        """
        called before actually showing the page, but after all previous pages
        have finished
        """
        pass

    def finalize(self):
        """
        called to finish processing the page and allow it to collect all entered data
        """
        pass

class IntroPage(Page):
    type = gtk.ASSISTANT_PAGE_INTRO
    complete = True
    def init(self):
        label = gtk.Label("Welcome! This will guide you to the first steps of creating a new odML-Document")
        label.set_line_wrap(True)
#        label.show()
        self.pack_start(label, True, True, 0)

def get_username():
    import getpass
    username = getpass.getuser()
    try: # this only works on linux
        import pwd
        username = pwd.getpwnam(username).pw_gecos
    except:
        pass
    return username

def get_date():
    import datetime
    return datetime.date.today().isoformat()

class DataPage(Page):
    def init(self):
        self.table = Table(cols=2)
        # put the data area in center, fill only horizontally
        align = gtk.Alignment(0.5, 0.5, xscale=1.0)
        self.add(align)
        self.fields = fields = {
            'Author': get_username(),
            'Date': get_date(),
            'Version': '1.0',
            'Repository': 'http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml',
            }
        # add a label and an entry box for each field
        for k, v in fields.iteritems():
            label = gtk.Label("%s: " % k)
            label.set_alignment(1, 0.5)
            entry = gtk.Entry()
            entry.set_text(v)
            setattr(self, k.lower(), entry)
            self.table.append([entry], label, entry)
        align.add(self.table.table)
        # already load the data in background
        terminology.terminologies.deferred_load(fields['Repository'])

    def finalize(self):
        """read the data from the corresponding labels"""
        self.data = {}
        for k in self.fields:
            self.data[k.lower()] = getattr(self, k.lower()).get_text()

class CheckableSectionView(SectionView):
    """
    A TreeView showing all the documents sections of a terminology
    together with Checkboxes, allowing to select subsets of it
    """
    def __init__(self, *args, **kargs):
        super(CheckableSectionView, self).__init__(*args, **kargs)
        # add a column for the toggle button
        renderer = gtk.CellRendererToggle()
        renderer.connect("toggled", self.toggled)

        column = gtk.TreeViewColumn(None, renderer)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_cell_data_func(renderer, self.celldatamethod)

        self._treeview.insert_column(column, 0)
        self._treeview.set_expander_column(self._treeview.get_column(1))
        self.sections = {}

    def celldatamethod(self, column, cell, model, iter):
        """
        custom method to set the active state for the CellRenderer
        """
        sec = model.get_object(iter)
        cell.set_active(self.sections.get(sec, False))

    def toggled(self, renderer, path):
        active = not renderer.get_active()

        model = self._treeview.get_model()
        iter = model.get_iter(path)
        obj = model.get_object(iter)
        # checking a section, includes/excludes all subsections by default
        for sec in obj.itersections(recursive=True, yield_self=True):
            self.set_active(sec, active)
        # if activating a section, all parent sections must be included too
        if active:
            while sec.parent is not None:
                sec = sec.parent
                self.set_active(sec, active)

    def set_active(self, sec, active):
        """
        marks an item as active/inactive and triggers
        the corresponding treeview actions
        """
        self.sections[sec] = active
        model = self.get_model()
        path = model.get_node_path(sec)
        if not path: return
        model.row_changed(path, model.get_iter(path))

class SectionPage(Page):
    def init(self):
        self.view = CheckableSectionView(None)
        self.pack_start(ScrolledWindow(self.view._treeview), True, True, 0)

    def prepare(self, assistant, prev_page):
        self.term = terminology.terminologies.load(prev_page.data['repository'])
        self.view.set_model(DocumentModel(self.term))

    @property
    def sections(self):
        for sec in self.term.itersections(recursive=True):
            if sec in self.view.sections:
                yield sec

class SummaryPage(Page):
    type = gtk.ASSISTANT_PAGE_CONFIRM
    def init(self):
        self.add(gtk.Label("All information has been gathered. Ready to create document."))

class DocumentWizard:
    def __init__(self):
        assistant = gtk.Assistant()

        assistant.set_default_size(-1, 500)

        assistant.connect("apply", self.apply)
        assistant.connect("close", self.cancel)
        assistant.connect("cancel", self.cancel)

        IntroPage().deploy(assistant, "New Document Wizard")

        data_page = DataPage()
        data_page.deploy(assistant, "Setup generic information")
        self.data_page = data_page

        section_page = SectionPage()
        section_page.data = data_page
        section_page.deploy(assistant, "Select which sections to import from the repository")
        self.section_page = section_page

        SummaryPage().deploy(assistant, "Complete")

        assistant.connect('prepare', self.prepare)
        # third page loads the repository and offers which sections to import
        # initially
        assistant.show_all()

    def prepare(self, assistant, page):
        last_page_idx = assistant.get_current_page()-1
        prev_page = None
        if last_page_idx >= 0:
            prev_page = assistant.get_nth_page(last_page_idx)
            prev_page.finalize()
        return page.prepare(self, prev_page)

    def cancel(self, assistant):
        assistant.destroy()

    def apply(self, assistant):
        """
        the process is finished, create the desired document
        """
        doc = odml.Document()
        for k, v in self.data_page.data.iteritems():
            setattr(doc, k, v)

        # copy all selected sections from the terminology
        term = self.section_page.term
        term._assoc_sec = doc # set the associated section
        for sec in term.itersections(recursive=True):
            if not sec in self.section_page.sections:
                continue
            newsec = sec.clone(children=False)
            for prop in sec.properties:
                newsec.append(prop.clone())
            sec._assoc_sec = newsec
            sec.parent._assoc_sec.append(newsec)

        self.finish(doc)

    def finish(self, document):
        """
        Placeholder that is overridden by an actual implementation
        """
        raise NotImplementedError

if __name__=="__main__":
    DocumentWizard()
    gtk.main()
