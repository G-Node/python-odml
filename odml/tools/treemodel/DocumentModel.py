import gtk, gobject
import odml.doc
from TreeIters import SectionIter
from TreeModel import TreeModel, ColumnMapper
debug = lambda x: 0
# to enable tree debugging:
#import sys
#debug = lambda x: sys.stdout.write(x + "\n")

ColMapper = ColumnMapper({"Name"        : (0, "name")})

class DocumentModel(TreeModel):
    def __init__(self, odml_document):
        super(DocumentModel, self).__init__(ColMapper)

        # otherwise bad things happen
        assert isinstance(odml_document, odml.doc.Document)

        self._section = odml_document
        #self._section._Changed += self.on_section_changed

    @property
    def document(self):
        return self._section

    def model_path_to_odml_path(self, path):
        # (a,b,c) -> (a,b,0,c)
        rpath = (path[0],) # document -> section
        for i in path[1:]:
            rpath += (0,i) # section -> sub-section
        return rpath

    def odml_path_to_model_path(self, path):
        # (a,b,0,c) -> (a,b,c)
        if not path: return (0,) # the 0, is also the root-node, which sucks :/
        return (path[0],) + path[1::2]

    def on_get_iter(self, path):
        debug("+on_get_iter: %s" % repr(path))
        if path == (0,) and len(self._section.sections) == 0: return None
        # we get the path from the treemodel which does not show the properties
        # therefore adjust the path to always select the sections
        rpath = (path[0],) # document -> section
        for i in path[1:]:
            rpath += (0,i) # section -> sub-section
        section = self._section.from_path(rpath)
        debug("-on_get_iter: %s" % (section))
        return SectionIter(section)

    def on_iter_nth_child(self, tree_iter, n):
        if tree_iter == None:
            return SectionIter(self._section.sections[n])
        return super(DocumentModel, self).on_iter_nth_child(tree_iter, n)
