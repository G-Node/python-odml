import unittest

import odml
import odml.gui.dnd.targets as targets
import odml.gui.dnd.odmldrop as odmldrop
import odml.gui.dnd.text as text
import odml.gui.dnd.tree as tree
from odml.gui.DocumentRegistry import DocumentRegistry
import samplefile
import mapping
import gtk

MOVE = gtk.gdk.ACTION_MOVE
COPY = gtk.gdk.ACTION_COPY

class TestDND(unittest.TestCase):
    """
    Try to test only parts of the DND system that are independent of the
    actual gtk Widgets
    """
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        self.MOVE = tree.Action(MOVE)
        self.COPY = tree.Action(COPY)
        #for s in self.doc: xmlparser.dumpSection(s)

    def test_text_drops_to_propertyview(self):
        sec = odml.Section(name="test")

        dropper = text.TextGenericDropForPropertyTV(None)
        data = '<property><name>test</name><value>1</value></property>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertTrue(ret)

        data = '<value>15</value>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertFalse(ret)

        data = '<section name="test"><type>undefined</type></section>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertFalse(ret)

    def test_text_drops_to_sectionview(self):
        sec = odml.Section(name="test")

        dropper = text.TextGenericDropForSectionTV(None)
        data = '<property><name>test</name><value>1</value></property>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertTrue(ret)

        data = '<value>15</value>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertFalse(ret)

        data = '<section name="test"><type>undefined</type></section>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertTrue(ret)

        data = '<odml version=1>%s</odml>'
        ret = dropper.odml_tree_can_drop(self.MOVE, sec, -1, data)
        self.assertFalse(ret)

    def execute(self, cmd):
        return cmd()

    def test_text_drop(self):
        sec = odml.Section(name="s1", type="t1")

        dropper = text.TextGenericDropForSectionTV(exec_func=self.execute)
        data = '<section name="s2"><type>t2</type></section>'
        print dropper.odml_tree_receive_data(self.MOVE, sec, -1, data)

        dst = mapping.parse("""
        s1[t1]
        - s2[t2]
        """)
        self.assertEqual(sec, dst.sections[0])

    def test_ref_drop(self):
        s1 = odml.Section(name="s1", type="t1")
        doc = odml.Document()
        s2 = odml.Section(name="s2", type="t2")
        doc.append(s2)

        r = DocumentRegistry()
        id = r.add(doc)

        dropper = odmldrop.OdmlDrop(registry=r, target=targets.SectionDrop(exec_func=self.execute))
        dragger = odmldrop.OdmlDrag(inst=odml.section.Section)
        ret = dropper.odml_tree_can_drop(self.MOVE, s1, -1, None)
        self.assertTrue(ret)
        data = dragger.odml_get_data(self.MOVE, s2)
        dropper.odml_tree_receive_data(self.MOVE, s1, -1, data)

        dst = mapping.parse("""
        s1[t1]
        - s2[t2]
        """)
        self.assertEqual(s1, dst.sections[0])


if __name__ == '__main__':
    unittest.main()

